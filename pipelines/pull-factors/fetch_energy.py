"""Fetch Eurostat industrial electricity prices for the EnergyCost variable.

Eurostat dataset `nrg_pc_205` — "Electricity prices for non-household consumers,
bi-annual data (from 2007 onwards)". We request the industrial consumption band
MWH2000-19999 (a standard IEA/OECD industrial benchmark) excluding taxes,
priced in EUR per kWh.

Coverage: EU27 + EEA + UK + Turkey + candidate countries (~32 useful
national geos). Non-EU countries in our 40-country set (US, CN, IN, JP, KR, etc.)
are NOT covered by this dataset — the build_panel.py orchestrator documents
them as EnergyCost=null rather than imputing.

API: JSON-stat 2.0
    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_205
        ?format=JSON&lang=EN
        &currency=EUR&tax=X_TAX&unit=KWH&nrg_cons=MWH2000-19999

Bi-annual observations (2007-S1 .. 2025-S2) are averaged within year to produce
an annual series.

Cache: data/cache/eurostat/nrg_pc_205.json (raw JSON-stat response)

stdlib-only.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    ISO2_BY_ISO3,
    ISO3_BY_ISO2,
    YEAR_END,
    YEAR_START,
    http_get_json,
    read_json,
    write_json,
)

EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DATASET = "nrg_pc_205"

# Band MWH2000-19999 ≈ medium-large industrial consumer (IB benchmark).
# Excluding all taxes + levies (X_TAX), EUR per kWh.
QUERY = {
    "format": "JSON",
    "lang": "EN",
    "currency": "EUR",
    "tax": "X_TAX",
    "unit": "KWH",
    "nrg_cons": "MWH2000-19999",
}

# Eurostat uses "EL" for Greece and "UK" for the United Kingdom in geo dim.
# Our COUNTRIES table stores UK as ISO2="UK" to match Eurostat (GBR is not in
# ISO 3166-1 alpha-2; the real code is GB). No alias needed for UK.
# Greece is not in our 40-country set; EL is filtered out naturally.
EUROSTAT_GEO_ALIASES: dict[str, str] = {}


def build_url() -> str:
    parts = [f"{k}={v}" for k, v in QUERY.items()]
    return f"{EUROSTAT_BASE}/{DATASET}?" + "&".join(parts)


def parse_jsonstat(data: dict) -> list[dict]:
    """Flatten JSON-stat 2.0 response to rows: {iso2, iso3, year, price_eur_per_kwh}.

    JSON-stat value keys are flat indices into the size vector.
        flat_idx = g * len(time) + t    (geo is the outer dim; time is innermost)
    """
    dims = data["id"]  # order of dimensions
    sizes = data["size"]
    # Build per-dim index lookup
    def idx_map(dim: str) -> dict[int, str]:
        cat = data["dimension"][dim]["category"]["index"]
        return {v: k for k, v in cat.items()}

    geo_by_idx = idx_map("geo")
    time_by_idx = idx_map("time")

    # Compute stride for each dim (row-major, innermost last).
    strides = [1] * len(dims)
    for i in range(len(dims) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    geo_pos = dims.index("geo")
    time_pos = dims.index("time")

    raw = data.get("value", {})
    rows: list[dict] = []
    # Flat indices may be a dict of string-keyed sparse entries OR a list.
    if isinstance(raw, dict):
        items = ((int(k), v) for k, v in raw.items())
    else:
        items = enumerate(raw)

    # We normalize bi-annual codes ("2007-S1") to the integer year.
    # Multiple periods per (geo, year) are averaged in a post-pass.
    buckets: dict[tuple[str, int], list[float]] = {}
    for flat_idx, val in items:
        if val is None:
            continue
        # Decode per-dim index
        geo_idx = (flat_idx // strides[geo_pos]) % sizes[geo_pos]
        time_idx = (flat_idx // strides[time_pos]) % sizes[time_pos]
        geo_code = geo_by_idx[geo_idx]
        time_code = time_by_idx[time_idx]
        # time_code looks like "2019-S1" or "2019" — split on "-" to get year.
        try:
            year = int(time_code.split("-")[0])
        except ValueError:
            continue
        buckets.setdefault((geo_code, year), []).append(float(val))

    for (geo_code, year), vals in sorted(buckets.items()):
        if year < YEAR_START or year > YEAR_END:
            continue
        iso2 = EUROSTAT_GEO_ALIASES.get(geo_code, geo_code)
        iso3 = ISO3_BY_ISO2.get(iso2)
        if iso3 is None:
            continue
        rows.append({
            "iso3": iso3,
            "iso2": iso2,
            "year": year,
            "price_eur_per_kwh": round(sum(vals) / len(vals), 5),
            "n_semesters": len(vals),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-api", action="store_true")
    args = ap.parse_args()

    euro_dir = CACHE_DIR / "eurostat"
    euro_dir.mkdir(parents=True, exist_ok=True)

    raw_path = euro_dir / f"{DATASET}.json"
    out_path = euro_dir / "energy_price_industrial_annual.json"

    if not args.skip_api:
        t0 = time.time()
        data = http_get_json(build_url(), timeout=180)
        write_json(raw_path, data)
        print(f"[eurostat] {DATASET}: {len(data.get('value', {}))} cells cached in {time.time()-t0:.1f}s")
    else:
        data = read_json(raw_path)

    rows = parse_jsonstat(data)
    write_json(out_path, rows)
    by_country: dict[str, int] = {}
    for r in rows:
        by_country[r["iso3"]] = by_country.get(r["iso3"], 0) + 1
    print(f"[eurostat] {len(rows)} country-year rows across {len(by_country)} countries -> {out_path.name}")
    print(f"  covered (in 40-country set): {sorted(by_country.keys())}")
    missing = sorted(set(ISO2_BY_ISO3) - set(by_country))
    print(f"  NOT covered (Eurostat geo scope): {missing}")


if __name__ == "__main__":
    main()
