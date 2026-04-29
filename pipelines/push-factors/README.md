# push-factors

Country-year-technology panels for two push-factor variables in the NZIPL/BU
"Determinants of LCT FDI" study (Equation 1 of the paper):

- **`RenGen_{j,t,z}`** — renewable energy deployment (installed capacity, GW)
- **`TariffIndex_{j,t,z}`** — export tariff index (% MFN applied tariff facing j's exports in tech z)

Technologies (`z`): `solar_pv`, `wind` (onshore+offshore), `batteries`, `evs`.
Countries (`j`): 40 by default — edit `sources/_common.COUNTRIES` to widen.
Years (`t`): 2003–2025.

HS6 codes driving the tariff index (paper-supplied):

    854142, 854143   solar PV (HS 2017+)
    850231           wind generating sets
    850760, 850780   batteries (Li-ion + other accumulators)
    870380, 870390   electric + other motor vehicles

For pre-2017 years the tariff index falls back to HS 854140 (solar PV parent)
and HS 870390 alone (EVs). See `sources/_common.hs_for_tech` and `methodology.md`.

## Run

    # 1) Fetch raw data (caches to data/cache/)
    python fetch_irena.py          # ~10 s, IRENA IRENASTAT pxweb API
    python fetch_wits_tariffs.py   # ~1–5 min, WITS/TRAINS SDMX (one call per reporter)

    # 2) Build the panels
    python build_panels.py

Resumable: `fetch_wits_tariffs.py` skips reporters whose cache file already
exists. Delete `data/cache/wits/<ISO3>.json` to re-pull a single country, or
pass `--country CHN --country IND ...` to refresh specific ones.

To re-aggregate the per-country cache into the flat `wits_tariffs.json`
without hitting the network:

    python fetch_wits_tariffs.py --skip-api

## Outputs

    outputs/renewable_deployment_panel.{csv,json}
        country x year x tech  ->  capacity_gw
        Techs: solar_pv, onshore_wind, offshore_wind, wind (combined).
        Source: IRENA IRENASTAT Power Capacity & Generation (OnGrid+OffGrid summed).

    outputs/export_tariff_index_panel.{csv,json}            (exporter view)
        country x year x tech  ->  tariff_faced_simple_mean (v1 baseline)

    outputs/export_tariff_index_panel_destinations.{csv,json}  (destination view)
        reporter x year x tech  ->  tariff_mfn_simple_avg

    outputs/coverage.md              fill rate by tech x 5-year bucket
    outputs/methodology_summary.md   variable dictionary

## Conventions

- Python stdlib only (json, csv, argparse, urllib). No pip deps.
- On-disk API caches under `data/cache/` — pipelines are idempotent against the cache.
- Country list is ISO3-indexed; WITS uses ISO-numeric (see `_common.COUNTRIES`).

## Upgrading the tariff index to the paper's trade-weighted definition

The paper defines `TariffIndex_{j,t,z}` as the **trade-weighted** MFN tariff
imposed by destination markets on exporter j's goods in tech z:

    TariffIndex_{j,t,z} = sum_d  (w_{j,d,z,t} * tariff_{d,z,t})
    where w_{j,d,z,t} = j's exports to d in z at t  /  j's total exports in z at t

The `export_tariff_index_panel_destinations.*` output gives the right-hand-side
`tariff_{d,z,t}`. The missing ingredient is bilateral trade weights
`w_{j,d,z,t}`, which should come from CEPII BACI (free,
`https://www.cepii.fr/DATA_DOWNLOAD/baci/`). To layer it in:

1. Download the relevant BACI HS revision files (HS07 for 2007–2016,
   HS17 for 2017–2022, HS22 for 2023+).
2. Filter to the 7 HS6 codes in `sources._common.USER_HS_CODES`.
3. Aggregate j's exports to each d per (j, d, tech, year).
4. Join with `export_tariff_index_panel_destinations.csv` on (destination, year, tech)
   and compute the weighted mean per (j, year, tech).

This is a natural next sub-module (`fetch_baci.py` + extend `build_panels.py`)
that does not change the caches produced here.

## Out of scope

- Stationary battery deployment (not in IRENA; use IRENA battery storage
  reports or IEA EV Outlook fallback).
- EV stock (use IEA Global EV Outlook free dataset).
- Preferential-rate tariffs (TariffIndex in the paper uses MFN-applied; this
  pipeline follows that). WITS TRAINS supports preferential via a different
  `partner=<ISO_N>` call if needed later.
