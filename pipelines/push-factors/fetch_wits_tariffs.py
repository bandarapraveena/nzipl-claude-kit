"""Fetch MFN tariffs from WITS/TRAINS SDMX for all countries x HS6 x years.

Each country's full (product × year) panel comes in a single SDMX-JSON call,
so a 40-country pull is ~40 HTTP calls. Cached per reporter under
  data/cache/wits/<ISO3>.json
and aggregated into
  data/cache/wits_tariffs.json         (one row per reporter/product/year)

Request shape (confirmed working 2026-04):
  GET https://wits.worldbank.org/API/V1/SDMX/V21/datasource/TRN/
         reporter/{ISO_N}/partner/000/product/{HS1;HS2;...}/year/ALL/
         datatype/reported?format=JSON

`partner=000` = World (i.e. MFN applied to imports from all partners).
`datatype=reported` returns actual reported MFN tariffs. We fall back to
`aveestimated` when `reported` is empty (404 NoRecordsFound).

stdlib-only.

Usage:
    python fetch_wits_tariffs.py                  # full pull + aggregate
    python fetch_wits_tariffs.py --skip-api       # read per-country cache only
    python fetch_wits_tariffs.py --country CHN    # refresh one country
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    COUNTRIES,
    FETCH_HS_CODES,
    YEAR_END,
    YEAR_START,
    http_get_json,
    read_json,
    write_json,
)

WITS_BASE = "https://wits.worldbank.org/API/V1/SDMX/V21/datasource/TRN"


def wits_url(iso_num: str, products: tuple[str, ...], datatype: str = "reported") -> str:
    prod_part = ";".join(products)
    return (
        f"{WITS_BASE}/reporter/{iso_num}/partner/000/product/{prod_part}"
        f"/year/ALL/datatype/{datatype}?format=JSON"
    )


def _parse_response(data: dict) -> list[dict]:
    """Flatten an SDMX-JSON WITS TRAINS response into observation rows.

    SDMX-JSON observation layout (verified):
        obs_array = [value, *attribute_indices_in_structure.attributes.observation_order]
    Relevant attributes: NOMENCODE (HS revision used), TARIFFTYPE, SUM_OF_RATES,
    MIN_RATE, MAX_RATE, TOTALNOOFLINES, NBR_MFN_LINES, NBR_PREF_LINES,
    OBS_VALUE_MEASURE.

    WITS quirk: the series-key slot order does NOT follow either the
    `dimensions.series` list order or the stated `keyPosition` values.
    Empirically, slot order is [FREQ, DATATYPE, PRODUCTCODE, PARTNER, REPORTER].
    We resolve the slot for each dim by testing which slot's value-index stays
    in-range for that dim across the whole series set. Falls back to the
    empirical order if resolution is ambiguous (e.g., all dims singleton).
    """
    dims_series = data["structure"]["dimensions"]["series"]
    dims_obs = data["structure"]["dimensions"]["observation"]
    attrs_obs = data["structure"]["attributes"]["observation"]

    def dim_vals(code: str) -> list[dict]:
        for d in dims_series + dims_obs:
            if d["id"] == code:
                return d["values"]
        return []

    reporters = dim_vals("REPORTER")
    partners = dim_vals("PARTNER")
    products = dim_vals("PRODUCTCODE")
    datatypes = dim_vals("DATATYPE")
    time_vals = dim_vals("TIME_PERIOD")

    series_dict = data["dataSets"][0]["series"]

    # Empirically-verified slot order for WITS/TRAINS SDMX-JSON:
    EMPIRICAL_ORDER = ("FREQ", "DATATYPE", "PRODUCTCODE", "PARTNER", "REPORTER")

    # Resolve slot indices by scanning actual key indices and matching to dim sizes.
    dim_by_id = {d["id"]: d for d in dims_series}
    n_dims = len(dims_series)
    key_values_per_slot: list[set[int]] = [set() for _ in range(n_dims)]
    for k in series_dict:
        for i, p in enumerate(k.split(":")):
            key_values_per_slot[i].add(int(p))

    slot_for: dict[str, int] = {}
    # First, use empirical order as the default mapping.
    for i, dim_id in enumerate(EMPIRICAL_ORDER):
        if dim_id in dim_by_id and i < n_dims:
            slot_for[dim_id] = i
    # Then verify: for each dim with len(values)>1, the slot it's mapped to
    # must have seen exactly that many distinct indices. If not, swap.
    for dim_id, slot in list(slot_for.items()):
        n_vals = len(dim_by_id[dim_id].get("values", []))
        seen = len(key_values_per_slot[slot])
        if n_vals > 1 and seen != n_vals:
            # Find a slot with matching cardinality and swap.
            for j, got in enumerate(key_values_per_slot):
                if len(got) == n_vals and j != slot:
                    # swap
                    other_dim = next((d for d, s in slot_for.items() if s == j), None)
                    slot_for[dim_id] = j
                    if other_dim is not None:
                        slot_for[other_dim] = slot
                    break

    rows: list[dict] = []
    for series_key, series in series_dict.items():
        parts = series_key.split(":")
        reporter_iso_n = reporters[int(parts[slot_for["REPORTER"]])]["id"]
        partner_iso_n = partners[int(parts[slot_for["PARTNER"]])]["id"]
        product = products[int(parts[slot_for["PRODUCTCODE"]])]["id"]
        datatype = datatypes[int(parts[slot_for["DATATYPE"]])]["id"]

        for t_idx_str, obs_arr in series["observations"].items():
            year = int(time_vals[int(t_idx_str)]["id"])
            value = obs_arr[0]
            if value is None:
                continue
            extra: dict[str, object] = {}
            for i, attr in enumerate(attrs_obs):
                pos = 1 + i
                if pos >= len(obs_arr):
                    continue
                ai = obs_arr[pos]
                if ai is None:
                    continue
                vals = attr.get("values") or []
                if not vals or ai >= len(vals):
                    continue
                extra[attr["id"]] = vals[ai]["name"]
            rows.append({
                "reporter_iso_num": reporter_iso_n,
                "partner_iso_num": partner_iso_n,
                "product": product,
                "year": year,
                "datatype": datatype,
                "tariff_pct": float(value),
                "nomen": extra.get("NOMENCODE"),
                "tariff_type": extra.get("TARIFFTYPE"),
                "n_tariff_lines": extra.get("TOTALNOOFLINES"),
                "n_mfn_lines": extra.get("NBR_MFN_LINES"),
                "n_pref_lines": extra.get("NBR_PREF_LINES"),
                "value_measure": extra.get("OBS_VALUE_MEASURE"),
            })
    return rows


def fetch_country(iso3: str, iso_num: str, products: tuple[str, ...],
                  retries: int = 2, sleep_on_fail: float = 2.0) -> list[dict]:
    """Pull one country's full product × year tariff matrix.

    Strategy: one batched call with datatype=reported. If WITS returns
    404 (NoRecordsFound) we retry once with datatype=aveestimated. Server 5xx
    triggers a small backoff + retry.
    """
    for datatype in ("reported", "aveestimated"):
        url = wits_url(iso_num, products, datatype=datatype)
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                data = http_get_json(url, timeout=180)
                rows = _parse_response(data)
                if rows:
                    return rows
                # Empty but no error -> try estimated fallback
                break
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code == 404:
                    # No records for this reporter under this datatype
                    break
                # 5xx -> backoff
                if 500 <= e.code < 600 and attempt < retries:
                    time.sleep(sleep_on_fail * (attempt + 1))
                    continue
                break
            except Exception as e:  # network flakes
                last_err = e
                if attempt < retries:
                    time.sleep(sleep_on_fail * (attempt + 1))
                    continue
                break
        if last_err and not isinstance(last_err, urllib.error.HTTPError):
            print(f"  WARN {iso3} ({datatype}): {last_err}")
    return []


def aggregate(per_country_dir: Path) -> list[dict]:
    flat: list[dict] = []
    for f in sorted(per_country_dir.glob("*.json")):
        rows = read_json(f)
        flat.extend(rows)
    return flat


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-api", action="store_true", help="No network; just re-aggregate cache.")
    ap.add_argument("--country", action="append", help="Refresh only these ISO3s (repeatable).")
    ap.add_argument("--sleep", type=float, default=0.3, help="Seconds between reporter calls.")
    args = ap.parse_args()

    wits_dir = CACHE_DIR / "wits"
    wits_dir.mkdir(parents=True, exist_ok=True)

    requested: set[str] | None = set(c.upper() for c in args.country) if args.country else None

    if not args.skip_api:
        for name, iso3, iso_num in COUNTRIES:
            if requested is not None and iso3 not in requested:
                continue
            out = wits_dir / f"{iso3}.json"
            if out.exists() and requested is None:
                # Skip already-cached countries on a plain re-run (resumable).
                continue
            t0 = time.time()
            rows = fetch_country(iso3, iso_num, FETCH_HS_CODES)
            write_json(out, rows)
            dt = time.time() - t0
            by_prod: dict[str, int] = {}
            for r in rows:
                by_prod[r["product"]] = by_prod.get(r["product"], 0) + 1
            print(f"[wits] {iso3} ({iso_num}): {len(rows)} rows in {dt:.1f}s  {by_prod}")
            time.sleep(args.sleep)

    flat = aggregate(wits_dir)
    write_json(CACHE_DIR / "wits_tariffs.json", flat)
    by_reporter: dict[str, int] = {}
    for r in flat:
        by_reporter[r["reporter_iso_num"]] = by_reporter.get(r["reporter_iso_num"], 0) + 1
    print(f"[wits] aggregated {len(flat)} rows from {len(by_reporter)} reporters -> data/cache/wits_tariffs.json")


if __name__ == "__main__":
    main()
