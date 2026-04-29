# excess-capacity

Country-year panel of **excess manufacturing capacity** for Solar PV, Wind, Batteries, and EVs across 20 countries. Two formulas reported side by side:

    excess_capacity_oecd = Capacity − Production                   # OECD standard
    excess_capacity_user = Capacity − (Demand − Production)        # user-specified
    utilization          = Production / Capacity

See [methodology.md](methodology.md) for variable definitions, source mapping, year windows, and caveats.

## Run

    python build_panel.py

Optional filters:

    python build_panel.py --sector solar_pv --sector wind
    python build_panel.py --country CHN --country USA

Outputs:

- `outputs/excess_capacity_panel.json` — long-format panel (all rows)
- `outputs/excess_capacity_panel.csv` — same, CSV
- `outputs/coverage.md` — cell-fill rate per sector × decade × variable
- `outputs/anchor_checks.md` — 20-country sums vs published global headline figures; sanity bounds

## Adding a data drop

Every observation lives in a JSON file under `data/public/<source>/` (free source) or `data/manual/<source>/` (paywalled — hand-curate from the report). Example:

```json
[
  {
    "country": "China",
    "year": 2024,
    "sector": "solar_pv",
    "variable": "capacity",
    "value": 1100.0,
    "unit": "GW",
    "source": "IEA Renewables 2024, Table 3.2, p.84",
    "is_forecast": false,
    "notes": "",
    "priority": 0
  }
]
```

Run `build_panel.py` again — the loader picks up every `*.json` under those directories automatically. Higher `priority` wins when the same cell is reported by multiple drops; within the same priority, `data/manual/` beats `data/public/`.

## Conventions

- Python stdlib only (no pip deps).
- No runtime API calls; all data comes from versioned JSON drops.
- Country names normalized via `sources/_common.canonical_country` (ISO3 and common aliases accepted).
- Units auto-converted to the sector's canonical unit (GW, GWh, or million units).

## Status

- Pipeline skeleton: ✅
- Methodology doc: ✅
- Public JSON drops seeded with anchor values: in progress (see `data/public/`)
- Paywalled JSON drops: templates provided in `data/manual/<source>/TEMPLATE.json`; need hand-curation from report access

## Out of scope (see plan file)

- HTML scrollytelling deliverable
- Sub-national breakdowns
- Real bilateral trade integration
- Forecast modeling beyond published figures
