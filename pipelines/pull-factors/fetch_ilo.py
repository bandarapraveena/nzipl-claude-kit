"""Fetch ILOSTAT labour-cost indicator(s) used for the LaborCost variable.

Primary indicator (rplumber CSV endpoint):
    LAC_XEES_ECO_NB_A — Mean nominal hourly labour cost per employee, by
                        economic activity. Local currency.

Classification of interest (`classif1`):
    ECO_ISIC4_C           Manufacturing (ISIC Rev.4 Section C)

Coverage is OECD-heavy and leaves major gaps (CHN, IND, JPN, KOR, VNM, IDN,
etc.). The `build_panel.py` orchestrator combines this with the WDI proxy
SL.GDP.PCAP.EM.KD (GDP per person employed, constant PPP$) for global
coverage — see methodology.md.

Endpoint:
    https://rplumber.ilo.org/data/indicator/?id=LAC_XEES_ECO_NB_A
       &ref_area=AAA+BBB+...&timefrom=2003&timeto=2025

CSV format returned:
    ref_area,source,indicator,classif1,time,obs_value,obs_status,
    note_classif,note_indicator,note_source

stdlib-only.
"""
from __future__ import annotations

import argparse
import csv
import io
import time
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    ISO3S,
    YEAR_END,
    YEAR_START,
    http_get_text,
    read_json,
    write_json,
)

ILO_BASE = "https://rplumber.ilo.org/data/indicator/"

INDICATORS: dict[str, str] = {
    "LAC_XEES_ECO_NB_A": "Mean nominal hourly labour cost per employee, by economic activity (local currency)",
}


def fetch_indicator(indicator: str, iso3_list: list[str],
                    batch: int = 15, sleep: float = 0.3,
                    retries: int = 2, backoff: float = 2.0) -> list[dict]:
    """Rplumber caps query complexity; batch countries to stay under that limit."""
    rows: list[dict] = []
    for i in range(0, len(iso3_list), batch):
        chunk = iso3_list[i:i + batch]
        url = (f"{ILO_BASE}?id={indicator}&ref_area={'+'.join(chunk)}"
               f"&timefrom={YEAR_START}&timeto={YEAR_END}")
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                text = http_get_text(url, timeout=120)
                break
            except Exception as e:
                last_err = e
                if attempt < retries:
                    time.sleep(backoff * (attempt + 1))
                    continue
                print(f"  WARN {indicator} {chunk[0]}..{chunk[-1]}: {last_err}")
                text = None
        if text is None:
            continue

        # ILO serves a UTF-8 BOM; strip it so DictReader sees "ref_area" not "\ufeffref_area".
        if text.startswith("\ufeff"):
            text = text.lstrip("\ufeff")
        reader = csv.DictReader(io.StringIO(text))
        for r in reader:
            val = r.get("obs_value", "").strip()
            if not val:
                continue
            try:
                obs = float(val)
            except ValueError:
                continue
            rows.append({
                "iso3": r["ref_area"],
                "year": int(r["time"]),
                "classif1": r.get("classif1", ""),
                "source": r.get("source", ""),
                "indicator": indicator,
                "value": obs,
            })
        time.sleep(sleep)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-api", action="store_true")
    ap.add_argument("--indicator", action="append")
    args = ap.parse_args()

    ilo_dir = CACHE_DIR / "ilo"
    ilo_dir.mkdir(parents=True, exist_ok=True)

    wanted = set(args.indicator) if args.indicator else set(INDICATORS)
    for code, label in INDICATORS.items():
        if code not in wanted:
            continue
        out = ilo_dir / f"{code}.json"
        if args.skip_api:
            if out.exists():
                rows = read_json(out)
                print(f"[ilo cache] {code}: {len(rows)} rows — {label}")
            else:
                print(f"[ilo cache] {code}: MISSING")
            continue
        t0 = time.time()
        rows = fetch_indicator(code, ISO3S)
        write_json(out, rows)
        dt = time.time() - t0
        by_country: dict[str, int] = {}
        for r in rows:
            by_country[r["iso3"]] = by_country.get(r["iso3"], 0) + 1
        print(f"[ilo] {code}: {len(rows)} rows across {len(by_country)} countries in {dt:.1f}s — {label}")


if __name__ == "__main__":
    main()
