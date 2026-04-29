# Push-factor variable dictionary

Two country-year-technology panels for Equation 1 of the LCT FDI paper.

## `renewable_deployment_panel.csv` -- RenGen (j,t,z)

- **Definition**: installed electricity generation capacity of technology z
  in country j at end of year t, in gigawatts (GW).
- **Source**: IRENA IRENASTAT Power Capacity & Generation table
  (`Country_ELECCAP_*`), pulled via pxweb JSON API. Includes both OnGrid
  and OffGrid, summed to a single capacity figure per cell.
- **Techs emitted**: `solar_pv`, `onshore_wind`, `offshore_wind`, and a
  composite `wind` (= onshore + offshore) matching the paper's Wind
  category.
- **Out of scope (IRENA does not publish)**: stationary battery storage
  deployment, EV stock. For those, layer in IEA Global EV Outlook (free
  tables) and IRENA's separate Battery Storage report series.

## `export_tariff_index_panel.csv` -- TariffIndex (j,t,z)

- **Definition (paper)**: trade-weighted average MFN/applied tariff
  imposed by major import markets on country j's exports in technology z
  at year t. This is *destination-imposed* tariffs weighted by j's
  export shares.
- **v1 definition (this file)**: simple (unweighted) mean across all
  in-panel destinations of each destination's simple-average MFN tariff
  on the technology's HS6 codes. Column `weighting` = `unweighted
  (v1 baseline)`. Same value across j for a given (year, tech) cell --
  an honest *global tariff environment* baseline.
- **Upgrade path to paper definition**: multiply this destination panel
  by j's bilateral export shares from CEPII BACI HS6 data
  (`https://www.cepii.fr/DATA_DOWNLOAD/baci/`). See `methodology.md`.
- **Source**: WITS/UNCTAD TRAINS SDMX (TRN). `partner=000` (World),
  `datatype=reported` (fallback `aveestimated`). HS6 codes follow the
  user-supplied set (854142, 854143, 850231, 850760, 850780, 870380, 870390).
- **HS revision handling**: HS codes 854142, 854143 and 870380 only
  exist from HS 2017 onward. For years < 2017 the tariff index for
  solar_pv falls back to HS 854140 (parent) and for evs to HS 870390
  alone. The `hs_codes_used` column records which HS6s were averaged
  into each cell.

## Column dictionaries

### renewable_deployment_panel.csv
`country,iso3,year,tech,capacity_gw,source,notes`

### export_tariff_index_panel.csv (exporter-view)
`country,iso3,year,tech,tariff_faced_simple_mean,n_destinations,hs_codes_used,weighting,source,notes`

### export_tariff_index_panel_destinations.csv (destination panel)
`reporter_country,reporter_iso3,year,tech,hs_codes_used,tariff_mfn_simple_avg,n_hs_lines_underlying,nomen_code,datatype,source`
