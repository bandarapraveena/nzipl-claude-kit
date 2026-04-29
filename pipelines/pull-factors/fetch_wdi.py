"""Fetch World Bank WDI indicators used for MarketSize and a productivity
proxy for LaborCost.

Indicators (all free, no auth):
    NY.GDP.MKTP.CD        GDP, current US$
    NY.GDP.MKTP.KD        GDP, constant 2015 US$
    NY.GDP.PCAP.CD        GDP per capita, current US$
    NY.GDP.PCAP.PP.KD     GDP per capita, PPP (constant 2021 $int'l)
    SP.POP.TOTL           Population, total
    SL.GDP.PCAP.EM.KD     GDP per person employed (constant 2021 PPP $) — LaborCost productivity proxy
    NV.IND.MANF.ZS        Manufacturing, value added (% GDP)
    NV.IND.MANF.CD        Manufacturing, value added (current US$)

WDI REST: one call per indicator, batched across all countries via
semicolon-separated ISO3 list.

    https://api.worldbank.org/v2/country/USA;CHN;DEU/indicator/<CODE>?format=json&per_page=20000&date=2003:2025

Cache: data/cache/wdi/<INDICATOR>.json — raw API response list.
stdlib-only.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    ISO3S,
    YEAR_END,
    YEAR_START,
    http_get_json,
    read_json,
    write_json,
)

WDI_BASE = "https://api.worldbank.org/v2"

INDICATORS: dict[str, str] = {
    "NY.GDP.MKTP.CD":   "GDP, current US$",
    "NY.GDP.MKTP.KD":   "GDP, constant 2015 US$",
    "NY.GDP.PCAP.CD":   "GDP per capita, current US$",
    "NY.GDP.PCAP.PP.KD":"GDP per capita, PPP (constant 2021 intl$)",
    "SP.POP.TOTL":      "Population, total",
    "SL.GDP.PCAP.EM.KD":"GDP per person employed (const 2021 PPP $)",
    "NV.IND.MANF.ZS":   "Manufacturing, value added (% of GDP)",
    "NV.IND.MANF.CD":   "Manufacturing, value added (current US$)",
}


def wdi_url(indicator: str, iso3_list: list[str]) -> str:
    countries = ";".join(iso3_list)
    return (
        f"{WDI_BASE}/country/{countries}/indicator/{indicator}"
        f"?format=json&per_page=30000&date={YEAR_START}:{YEAR_END}"
    )


def fetch_indicator(indicator: str, iso3_list: list[str],
                    retries: int = 2, backoff: float = 2.0) -> list[dict]:
    """WDI paginates; per_page=30000 covers 40*23 = 920 rows with room to spare."""
    url = wdi_url(indicator, iso3_list)
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            data = http_get_json(url, timeout=120)
            if not isinstance(data, list) or len(data) < 2 or data[1] is None:
                return []
            return data[1]
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
                continue
    if last_err:
        print(f"  WARN {indicator}: {last_err}")
    return []


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-api", action="store_true",
                    help="Don't hit the network; verify cache only.")
    ap.add_argument("--indicator", action="append",
                    help="Pull only these indicators (repeatable).")
    args = ap.parse_args()

    wdi_dir = CACHE_DIR / "wdi"
    wdi_dir.mkdir(parents=True, exist_ok=True)

    wanted = set(args.indicator) if args.indicator else set(INDICATORS)

    for code, label in INDICATORS.items():
        if code not in wanted:
            continue
        out = wdi_dir / f"{code}.json"
        if args.skip_api:
            if out.exists():
                rows = read_json(out)
                print(f"[wdi cache] {code}: {len(rows)} rows — {label}")
            else:
                print(f"[wdi cache] {code}: MISSING")
            continue
        t0 = time.time()
        rows = fetch_indicator(code, ISO3S)
        write_json(out, rows)
        dt = time.time() - t0
        non_null = sum(1 for r in rows if r.get("value") is not None)
        print(f"[wdi] {code}: {len(rows)} rows ({non_null} non-null) in {dt:.1f}s — {label}")


if __name__ == "__main__":
    main()
