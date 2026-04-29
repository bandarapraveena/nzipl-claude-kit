"""Fetch renewable installed capacity from IRENA IRENASTAT (pxweb JSON API).

No auth required. Caches the raw pxweb response under
  data/cache/irena_capacity_raw.json
and a flat list of observations under
  data/cache/irena_capacity.json

Pulled technologies (IRENA codes in parentheses):
  - Solar photovoltaic (2)   -> paper's "solar PV"
  - Onshore wind (5)         -> paper's "wind" (primary)
  - Offshore wind (6)        -> paper's "wind" (added)
  - Total solar energy (1)   -> reference aggregate
  - Total wind energy (4)    -> reference aggregate

Grid connection: both OnGrid (0) and OffGrid (1) are summed.

IRENA does NOT publish stationary battery or EV deployment. Those variables
are left out of this pull — methodology.md documents the IEA Global EV
Outlook (free) fall-back you can layer on later.

stdlib-only.

Usage:
    python fetch_irena.py            # refresh cache from API
    python fetch_irena.py --skip-api # read from cache only (no network)
"""
from __future__ import annotations

import argparse
import urllib.error
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    COUNTRIES,
    YEAR_END,
    YEAR_START,
    http_get_json,
    http_post_json,
    read_json,
    write_json,
)

IRENA_BASE = "https://pxweb.irena.org/api/v1/en/IRENASTAT/Power%20Capacity%20and%20Generation/"

IRENA_TECH_CODES: dict[str, str] = {
    "solar_pv":      "2",
    "onshore_wind":  "5",
    "offshore_wind": "6",
    "solar_total":   "1",
    "wind_total":    "4",
}


def discover_table_id() -> str:
    """IRENA bumps the table ID each release (ELECCAP_2026_H1 today).
    Resolve the current one dynamically so the pipeline keeps working.
    """
    items = http_get_json(IRENA_BASE)
    candidates = [it for it in items if "ELECCAP" in it.get("id", "") and it["id"].startswith("Country_")]
    if not candidates:
        raise RuntimeError("No Country_ELECCAP_* table found under IRENASTAT")
    # Pick the most recent — IDs sort lexicographically enough (2025_H2 < 2026_H1).
    candidates.sort(key=lambda it: it["id"], reverse=True)
    return candidates[0]["id"]


def year_codes(meta: dict) -> dict[int, str]:
    """pxweb indexes years as 0-based codes. Map 2000 -> '0', 2001 -> '1', …"""
    for v in meta["variables"]:
        if v["code"] == "Year":
            return {int(name): code for code, name in zip(v["values"], v["valueTexts"])}
    raise RuntimeError("pxweb metadata missing Year variable")


def fetch_raw(table_id: str) -> dict:
    url = IRENA_BASE + table_id.replace(" ", "%20")
    meta = http_get_json(url)
    y2code = year_codes(meta)
    wanted_year_codes = [y2code[y] for y in range(YEAR_START, YEAR_END + 1) if y in y2code]
    iso3s = [iso3 for _, iso3, _ in COUNTRIES]
    tech_codes = list(IRENA_TECH_CODES.values())

    query = {
        "query": [
            {"code": "Country/area",    "selection": {"filter": "item", "values": iso3s}},
            {"code": "Technology",      "selection": {"filter": "item", "values": tech_codes}},
            {"code": "Grid connection", "selection": {"filter": "item", "values": ["0", "1"]}},
            {"code": "Year",            "selection": {"filter": "item", "values": wanted_year_codes}},
        ],
        "response": {"format": "json"},
    }
    raw = http_post_json(url, query)
    raw["_table_id"] = table_id
    raw["_year_codes"] = {str(y): c for y, c in y2code.items()}
    return raw


def flatten(raw: dict) -> list[dict]:
    """pxweb returns { columns, comments, data: [{key:[...], values:[...]}] }.

    Each `key` is [country/area, tech, grid, year] in column order.
    We emit one row per (country, year, irena_tech) with OnGrid+OffGrid summed.
    Units are MW — convert to GW on emit (divide by 1000).
    """
    col_codes = [c["code"] for c in raw["columns"]]
    idx = {c: col_codes.index(c) for c in col_codes}
    # Reverse maps
    code2year = {c: int(y) for y, c in raw["_year_codes"].items()}
    code2tech = {v: name for name, v in IRENA_TECH_CODES.items()}
    agg: dict[tuple[str, int, str], float] = {}
    for row in raw.get("data", []):
        key = row["key"]
        country = key[idx["Country/area"]]
        tech_code = key[idx["Technology"]]
        year_code = key[idx["Year"]]
        try:
            value = float(row["values"][0])
        except (ValueError, TypeError):
            continue
        year = code2year.get(year_code)
        tech_name = code2tech.get(tech_code)
        if year is None or tech_name is None:
            continue
        k = (country, year, tech_name)
        agg[k] = agg.get(k, 0.0) + value  # sum OnGrid + OffGrid

    flat: list[dict] = []
    for (iso3, year, tech), mw in sorted(agg.items()):
        flat.append({
            "iso3": iso3,
            "year": year,
            "irena_tech": tech,
            "capacity_mw": round(mw, 3),
            "capacity_gw": round(mw / 1000.0, 4),
            "source": f"IRENA IRENASTAT {raw.get('_table_id','')}",
        })
    return flat


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-api", action="store_true", help="Use cached raw response; no network call.")
    args = ap.parse_args()

    raw_path = CACHE_DIR / "irena_capacity_raw.json"
    flat_path = CACHE_DIR / "irena_capacity.json"

    if args.skip_api:
        if not raw_path.exists():
            raise SystemExit(f"--skip-api but no cache at {raw_path}")
        raw = read_json(raw_path)
    else:
        table_id = discover_table_id()
        print(f"[irena] table: {table_id}")
        raw = fetch_raw(table_id)
        write_json(raw_path, raw)
        print(f"[irena] wrote raw -> {raw_path} ({len(raw.get('data', []))} cells)")

    flat = flatten(raw)
    write_json(flat_path, flat)
    print(f"[irena] wrote flat -> {flat_path} ({len(flat)} rows)")

    # quick coverage line
    by_tech: dict[str, int] = {}
    for r in flat:
        by_tech[r["irena_tech"]] = by_tech.get(r["irena_tech"], 0) + 1
    print("[irena] rows per technology:", dict(sorted(by_tech.items())))


if __name__ == "__main__":
    main()
