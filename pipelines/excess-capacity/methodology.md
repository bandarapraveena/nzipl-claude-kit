# Methodology — Clean-tech Excess Capacity Panel

## Purpose

Extend the OECD Steel Outlook 2025 framing of "excess capacity" to four clean-tech sectors — Solar PV, Wind, Batteries, EVs — at a country-year level, for 20 countries.

## Formulas

Two metrics are reported side by side, per user direction.

- **OECD standard** (`excess_capacity_oecd`)

      Excess Capacity = Capacity − Production
      Utilization     = Production / Capacity

  Matches OECD Steel Committee methodology (gap between operational capacity and actual output).

- **User-specified** (`excess_capacity_user`)

      Excess Capacity = Capacity − (Demand − Production)
                      = Capacity − net_imports_proxy

  where `net_imports_proxy = Demand − Production` (positive when apparent domestic consumption exceeds domestic production). **Non-standard.** It treats the country as needing to cover its trade gap from capacity. Interpret with caution; see "Caveats" below.

Both are reported so readers can see the divergence. The per-row algebraic difference is `2·Production − Demand`.

## Variable definitions

Every sector has the same three variables — `capacity`, `production`, `demand` — in the unit column indicated.

| Sector | Capacity | Production | Demand | Unit |
|---|---|---|---|---|
| Solar PV | Annual nameplate module manufacturing capacity | Annual module shipments | Annual installations (capacity additions) | GW/yr |
| Wind | Annual nacelle assembly capacity | Annual nacelle shipments | Annual installations (capacity additions) | GW/yr |
| Batteries | Annual Li-ion cell manufacturing capacity | Annual cell production | EV demand + stationary storage demand | GWh/yr |
| EVs | Annual passenger-vehicle assembly capacity dedicated to EVs (BEV+PHEV) | Annual EV production | Annual EV sales | million units/yr |

### Definition notes

- **Solar "capacity"** = *module* capacity, not cell or wafer (those are separate upstream stages — can be added as a follow-up).
- **Wind "capacity"** = *nacelle assembly* (the choke point); blades & towers are typically more distributed and not the binding constraint.
- **Battery "capacity"** = *cell* manufacturing (not pack assembly, which is cheaper to site and less binding).
- **EV "capacity"** = assembly lines *producing* BEV+PHEV passenger vehicles. Where a plant is convertible between ICE and EV, IEA and national associations report EV-dedicated where available; otherwise total auto × EV production share is used (fallback flagged in `notes`).

## Country scope (20)

China (CHN), United States (USA), Germany (DEU), Japan (JPN), South Korea (KOR), India (IND), Australia (AUS), United Kingdom (GBR), France (FRA), Spain (ESP), Brazil (BRA), Mexico (MEX), Singapore (SGP), Vietnam (VNM), Thailand (THA), Malaysia (MYS), South Africa (ZAF), Romania (ROU), Poland (POL), Czech Republic (CZE).

## Year window (per sector)

| Sector | Start | End | Rationale |
|---|---|---|---|
| Solar PV | 2002 | 2025 | Global mfg <500 MW in 2002; IEA PVPS back-series available; country-level sparse 2002–2004 |
| Wind | 2002 | 2025 | GWEC reports start 2005; BTM Consult covers 2002–2004 for majors |
| Batteries | 2010 | 2025 | Modern Li-ion auto/ESS cell mfg began with Leaf/Volt era; BNEF tracking from ~2015 |
| EVs | 2010 | 2025 | Leaf/Model S launched 2010–2012; earlier BEV+PHEV near-zero |

2025 values are flagged `is_forecast=true` where announced/forecast rather than actual.

## Data sources (per sector × variable)

Every row in the output panel carries a plain-text `*_source` field pointing to the drop. The table below lists the **primary** source for each cell; secondary sources may override via a higher `priority` value in the drop.

| Sector | Capacity | Production | Demand |
|---|---|---|---|
| **Solar PV** | IEA *Renewables* (annual, 2015+); IEA PVPS *Trends in Photovoltaic Applications* (back-series); BNEF *Solar Manufacturer Capacity Tracker* [manual] | IEA *Renewables*; ITRPV; SolarPower Europe *Global Market Outlook*; IEA PVPS cell/module production back-series | IRENA *Renewable Capacity Statistics* (additions back to 2000); IEA PVPS installations |
| **Wind** | GWEC *Global Wind Report* (2005+); BTM Consult *World Market Update* (2002–2004); Wood Mackenzie *Global Wind Turbine OEM Market Share* [manual] | GWEC supply-side; Wood Mackenzie [manual]; BTM back-series | GWEC *Global Wind Report*; IRENA *Renewable Capacity Statistics* |
| **Batteries** | BNEF *Lithium-Ion Battery Supply Chain Ranking* [manual]; IEA *Global EV Outlook* (battery mfg by country) | BNEF [manual]; Benchmark Mineral Intelligence [manual] | IEA *Global EV Outlook* (auto + ESS split) |
| **EVs** | IEA *Global EV Outlook* (announced production capacity by country); national associations fallback (CAAM China, ACEA EU, KAMA Korea, JAMA Japan, ANFAVEA Brazil, AMIA Mexico) | IEA; OICA production statistics; national associations | IEA *Global EV Outlook*; EV-Volumes [manual] |

**[manual]** = paywalled source; requires a hand-curated JSON drop in `data/manual/<source>/<year>.json` with the citation in the row-level `source` string.

## Drop file format

A "drop" is a JSON file under `data/public/<source>/` or `data/manual/<source>/`. It is either a JSON list of row objects, or an object with a top-level `"rows"` key. Each row must carry:

```json
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
```

- `country` may be any recognized alias (ISO3, "USA", "UK", "Korea", etc.) — `_common.canonical_country` normalizes it.
- `unit` is free-text; the loader normalizes to the canonical unit (`GW`, `GWh`, or `million units`).
- `variable` must be one of `capacity`, `production`, `demand`.
- `priority` (default `0`) — higher wins when multiple drops report the same cell. Within the same priority, manual drops beat public drops.

## Output schema (long format)

See `build_panel.py::PANEL_COLUMNS`. One row per (country × year × sector) with nulls where data is missing. Emitted as both `outputs/excess_capacity_panel.json` and `outputs/excess_capacity_panel.csv`.

## Verification

`build_panel.py` emits two report files on every run:

1. `outputs/coverage.md` — cell-fill rate per sector × decade × variable. Expected sparsity (documented below) should match observed sparsity.
2. `outputs/anchor_checks.md` — 20-country sum vs known global headline figures, plus counts of rows violating `0 ≤ utilization ≤ 1.05` or `excess_capacity_oecd ≥ 0`.

Headline anchor points (for 2024 totals; our 20 countries should capture the large majority):

- Solar PV module mfg capacity: IEA — global >1,100 GW
- Wind installations: GWEC — global ~117 GW
- Li-ion cell capacity: IEA — global ~3,000 GWh
- EV sales: IEA — global ~17 million units

## Caveats (important)

1. **The user-specified formula is not standard.** `Capacity − (Demand − Production)` treats the net-import gap as something capacity must "cover." Use the OECD-standard column for cross-report comparability.
2. **`net_imports_proxy` is a residual, not a measured trade flow.** A true bilateral trade series requires UN COMTRADE or OEC HS-code mapping per sector, which is a separate enrichment.
3. **Wind nacelle capacity at country level is patchy.** GWEC reports regional totals; firm-level aggregation implies the assembly actually happens in the HQ country, which is increasingly false (e.g., Vestas plants in India, Siemens Gamesa in Brazil).
4. **EV capacity is an estimate.** Most public sources report vehicle production, not dedicated EV lines. Where only total auto capacity × EV share is available, the `notes` column flags it.
5. **Smaller markets** (Singapore, Czech, Romania, Vietnam, Malaysia, Thailand, South Africa) will have many missing cells for solar/wind *manufacturing* capacity (they are mostly *consumers*, not producers). Missing ≠ zero — the pipeline leaves them null, and downstream analysis should not impute.
6. **Pre-2010 solar/wind**: IEA PVPS and BTM data is the best back-series, but coverage is uneven at country level — some rows will stay null.
7. **Paywalled sources** (BNEF, WoodMac, Benchmark, EV-Volumes): pipeline accepts hand-curated JSON drops; it will never scrape.
