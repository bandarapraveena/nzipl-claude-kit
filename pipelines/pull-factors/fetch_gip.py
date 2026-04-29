"""Fetch the Juhasz-Lashkaripour-Oehlmair-Protzer (JLOP) 2025 industrial policy
dataset and filter to green (LCT) industrial policy measures.

Source:
    https://github.com/industrialpolicygroup/IndustrialPolicyData
    data/JLOP_2025.xlsx (~4MB, 47k rows, CC-BY-4.0)

JLOP_2025 is built on Global Trade Alert data with a BERT classifier that flags
each measure as industrial policy (`D_IP_bert_3`=1), other policy intention,
or not-enough-info. We filter to measures that:
    1. Are flagged industrial policy (D_IP_bert_3 == 1).
    2. Affect at least one of our 8 LCT HS6 codes (see push-factors/sources/_common
       USER_HS_CODES plus the pre-2017 solar parent 854140).

Outputs a per-country/year/tech count of announced measures.

Filter notes:
- `MeasureAffectedProducts` is a comma-separated list of HS6 codes at the
  measure level — one measure may hit multiple techs; we count it toward each
  hit tech (not pro-rated).
- Country names use `CountryImposing_cleaned`. Supranational blocks (EU,
  Eurasian Economic Union) are expanded to member states where possible; see
  SUPRANATIONAL_EXPANSIONS below. Unexpanded blocks are dropped.

Cache:
    data/cache/gip/JLOP_2025.xlsx          raw download
    data/cache/gip/JLOP_green_measures.json filtered measure rows

stdlib-only.
"""
from __future__ import annotations

import argparse
import time
from collections import defaultdict
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    NAME_BY_ISO3,
    YEAR_END,
    YEAR_START,
    http_get_bytes,
    read_json,
    write_json,
)
from sources.xlsx import read_rows_as_dicts

JLOP_URL = "https://raw.githubusercontent.com/industrialpolicygroup/IndustrialPolicyData/main/data/JLOP_2025.xlsx"

# HS6 -> tech mapping (mirrors push-factors/sources/_common.hs_for_tech).
HS_TO_TECH: dict[str, str] = {
    "854140": "solar_pv", "854142": "solar_pv", "854143": "solar_pv",
    "850231": "wind",
    "850760": "batteries", "850780": "batteries",
    "870380": "evs", "870390": "evs",
}

# Map country names used in JLOP -> our ISO3 (COUNTRIES table).
# JLOP uses mostly English short names; patch the mismatches here.
JLOP_NAME_ALIASES: dict[str, str] = {
    "United States of America": "USA",
    "USA": "USA",
    "United States": "USA",
    "Republic of Korea": "KOR",
    "Korea, Republic of": "KOR",
    "South Korea": "KOR",
    "Korea": "KOR",
    "Russia": "RUS",  # not in our 40-country set, skipped
    "Russian Federation": "RUS",
    "Czechia": "CZE",
    "Czech Republic": "CZE",
    "Viet Nam": "VNM",
    "Vietnam": "VNM",
    "UK": "GBR",
    "United Kingdom": "GBR",
    "Great Britain": "GBR",
    "Hong Kong, China": "HKG",
    "Hong Kong": "HKG",
    "Taiwan, China": "TWN",
    "Chinese Taipei": "TWN",
    "Taiwan": "TWN",
    "UAE": "ARE",
    "United Arab Emirates": "ARE",
    "Iran": "IRN",
    "Turkiye": "TUR",
    "Turkey": "TUR",
    "Slovak Republic": "SVK",
    "Slovakia": "SVK",
}

# Build reverse lookup: add canonical names from our COUNTRIES list.
_JLOP_NAME_TO_ISO3: dict[str, str] = dict(JLOP_NAME_ALIASES)
for iso3, name in NAME_BY_ISO3.items():
    _JLOP_NAME_TO_ISO3.setdefault(name, iso3)

# Supranational blocks: for now we drop these (would need member-lists to
# attribute to individual home countries). Document in methodology.
SUPRANATIONAL_BLOCKS = {
    "European Union",
    "Eurasian Economic Union",
    "Customs Union of Russia & Belarus & Kazakhstan",
    "Gulf Cooperation Council",
    "GCC",
    "ECOWAS",
    "MERCOSUR",
    "ASEAN",
    "CARICOM",
    "Central American Common Market",
    "SACU",
    "EFTA",
}


def _resolve_iso3(name: str) -> str | None:
    return _JLOP_NAME_TO_ISO3.get(name.strip())


def _resolve_iso3s(name: str) -> list[str]:
    """JLOP sometimes concatenates countries with ' & ' for jointly-imposed
    measures (e.g., 'Italy & France & Germany'). Split on ' & ' and resolve
    each — attribute the measure to every constituent country.
    """
    name = name.strip()
    if not name:
        return []
    if name in SUPRANATIONAL_BLOCKS:
        return []
    parts = [p.strip() for p in name.split(" & ")]
    out: list[str] = []
    any_hit = False
    for p in parts:
        iso3 = _JLOP_NAME_TO_ISO3.get(p)
        if iso3 is None:
            continue
        any_hit = True
        if iso3 in NAME_BY_ISO3:
            out.append(iso3)
    # If nothing matched and we got here with a single name, it's an unknown country.
    if not any_hit:
        return []
    return out


def _extract_hs6s(field: str) -> list[str]:
    """MeasureAffectedProducts is comma-separated HS6 (sometimes HS8/HS10)."""
    out: list[str] = []
    seen: set[str] = set()
    for raw in field.split(","):
        s = raw.strip()
        if not s:
            continue
        # Keep first 6 chars (HS6 from HS8/HS10).
        if len(s) < 6:
            continue
        hs6 = s[:6]
        if hs6 in seen:
            continue
        seen.add(hs6)
        out.append(hs6)
    return out


def download(cache_path: Path) -> bytes:
    if cache_path.exists():
        return cache_path.read_bytes()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    data = http_get_bytes(JLOP_URL, timeout=180)
    cache_path.write_bytes(data)
    return data


def parse_green_measures(xlsx_path: Path) -> list[dict]:
    """Stream JLOP_2025.xlsx and keep only rows that:
       1. D_IP_bert_3 == 1  (industrial policy)
       2. at least one MeasureAffectedProducts HS6 in our LCT set
       3. AnnouncedYear in [YEAR_START, YEAR_END]
       4. CountryImposing_cleaned resolves to an ISO3 in our 40-country set
    """
    kept: list[dict] = []
    total = 0
    seen_countries_unmapped: dict[str, int] = defaultdict(int)
    for row in read_rows_as_dicts(xlsx_path):
        total += 1
        ip_flag = row.get("D_IP_bert_3", "").strip()
        if ip_flag != "1":
            continue
        yr_raw = row.get("AnnouncedYear", "").strip()
        try:
            yr = int(float(yr_raw))
        except (ValueError, TypeError):
            continue
        if yr < YEAR_START or yr > YEAR_END:
            continue
        hs_codes = _extract_hs6s(row.get("MeasureAffectedProducts", ""))
        techs = sorted({HS_TO_TECH[h] for h in hs_codes if h in HS_TO_TECH})
        if not techs:
            continue
        country = row.get("CountryImposing_cleaned", "").strip()
        iso3s = _resolve_iso3s(country)
        if not iso3s:
            if country and country not in SUPRANATIONAL_BLOCKS:
                seen_countries_unmapped[country] += 1
            continue
        for iso3 in iso3s:
            kept.append({
                "measure_id": row.get("MeasureID", ""),
                "year": yr,
                "iso3": iso3,
                "country_raw": country,
                "techs": techs,
                "hs6s": hs_codes,
                "measure_type": row.get("MeasureType", ""),
                "mast_chapter": row.get("MAST_chapterName", ""),
                "implementation_level": row.get("ImplementationLevel", ""),
                "firm_specific": row.get("firm_specific", ""),
                "same_year_published": row.get("same_year_published", ""),
            })
    print(f"  scanned {total} total rows")
    if seen_countries_unmapped:
        top = sorted(seen_countries_unmapped.items(), key=lambda x: -x[1])[:10]
        print(f"  note: dropped {sum(seen_countries_unmapped.values())} rows from unmapped countries; top: {top}")
    return kept


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-api", action="store_true",
                    help="Use cached xlsx and re-parse without re-downloading.")
    args = ap.parse_args()

    gip_dir = CACHE_DIR / "gip"
    gip_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = gip_dir / "JLOP_2025.xlsx"
    out_path = gip_dir / "JLOP_green_measures.json"

    if not args.skip_api or not xlsx_path.exists():
        t0 = time.time()
        data = download(xlsx_path)
        print(f"[gip] downloaded {len(data)} bytes in {time.time()-t0:.1f}s -> {xlsx_path.name}")

    t0 = time.time()
    rows = parse_green_measures(xlsx_path)
    write_json(out_path, rows)
    print(f"[gip] parsed {len(rows)} green-LCT industrial policy measures in {time.time()-t0:.1f}s -> {out_path.name}")

    by_tech: dict[str, int] = defaultdict(int)
    by_country: dict[str, int] = defaultdict(int)
    for r in rows:
        for t in r["techs"]:
            by_tech[t] += 1
        by_country[r["iso3"]] += 1
    print("  by tech:", dict(sorted(by_tech.items(), key=lambda x: -x[1])))
    print("  by country (top 10):",
          dict(sorted(by_country.items(), key=lambda x: -x[1])[:10]))


if __name__ == "__main__":
    main()
