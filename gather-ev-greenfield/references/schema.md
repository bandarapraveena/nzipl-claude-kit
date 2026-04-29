# Schema reference

Output file: `projects/nzipl/data/nzipl_ev_greenfield_global.json` (array of record objects).
Validator: `projects/nzipl/data/validate_ev_record.py`.

## Required typed fields (14)

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | `EV-<ISO3>-<NNNN>` (e.g., `EV-DEU-0001`). Zero-padded, sequential per country. |
| `name` | string | Canonical facility name as the operator uses it. |
| `company` | string | Current majority operator. |
| `origin` | ISO-3 | Parent HQ country. |
| `country` | ISO-3 | Destination country. |
| `city` | string | Primary municipality. |
| `lat` | float | WGS84, within 5 km of `city`. |
| `lng` | float | WGS84. |
| `sector` | enum | `Batteries` \| `EVs` \| `Charging`. |
| `projectType` | enum | `cell` \| `pack` \| `cathode` \| `anode` \| `separator` \| `electrolyte` \| `recycling` \| `vehicle_assembly` \| `motor` \| `inverter` \| `charger`. |
| `status` | enum | `Operating` \| `Under Construction` \| `Planned` \| `Announced` \| `Paused` \| `Cancelled` \| `Closed` \| `Rumored`. |
| `announced` | string | `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`. |
| `investmentM` | number | Total capex, USD millions, FX at announcement date. |
| `sources` | object | Field-keyed URL map (see below). |

## Required small fields

| Field | Notes |
|-------|-------|
| `verificationTier` | `1` \| `2` \| `3`. See `verification-protocol.md`. |
| `verifiedBy` | Lab member name. |
| `verifiedDate` | `YYYY-MM-DD`. |

## Auto-derived (validator fills or verifies)

| Field | Derivation |
|-------|-----------|
| `isFDI` | `origin != country`. Cross-border = `true`. |
| `region` | From `country` ISO-3 via continent lookup (North America / Europe / East Asia / ...). |
| `postIRA` | `announced >= '2022-08-16'`. |
| `license` | Default `CC-BY-4.0` if omitted. |

The validator errors when any of these is present but inconsistent with the derivation.

## Optional fields (fill when confirmable)

| Field | Type | Notes |
|-------|------|-------|
| `aliases` | string[] | Rename history + shorthand. Dedup uses these. |
| `product` | string | Free-text specifics (chemistry, model, capacity). |
| `prodStarted` | string | ISO-8601. |
| `targetProduction` | number | Annual throughput. **Requires `productionUnits`.** |
| `productionUnits` | enum | `vehicles/year` \| `GWh/year` \| `packs/year` \| `tonnes/year` \| `chargers/year`. Per year, never cumulative. |
| `targetJobs` | int | Announced hiring target. |
| `investmentM_history` | array | `[{"date": "YYYY-MM-DD", "valueM": N, "source": "URL", "original": "€XB"}]`. Most recent value lives in `investmentM`. |
| `countAsNew` | bool | Default `true`. `false` for phased expansion that shouldn't double-count. |

## The `sources` object

```json
"sources": {
  "company":          "https://www.tesla.com/giga-berlin",
  "investmentM":      "https://www.electrive.com/2024/08/05/...",
  "announced":        "https://www.tesla.com/giga-berlin",
  "prodStarted":      "https://www.electrive.com/2022/03/22/...",
  "lat_lng":          "https://www.tesla.com/giga-berlin",
  "status":           "https://www.electrive.com/2026/03/02/...",
  "bnef_origin":      "nzipl_bnef_projects.json:id=304"
}
```

**Rules (enforced):**
- One public URL per sourced field. Non-receipt keys must start with `http(s)://`.
- Forbidden domains: `wikipedia.org`, `grokipedia.com`, `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com`, `medium.com`.
- Composite geocoding uses `lat_lng` (one key, not separate `lat`/`lng` URL keys).
- Dedup receipts: `bnef_origin` only. **No `fdi_origin`.**
- If a field isn't sourced, omit the key. Don't fabricate URLs.

**Tier minimums (distinct citation URLs, excluding receipts):**
- Tier 1 → ≥3
- Tier 2 → ≥2
- Tier 3 → ≥1

## Example

```json
{
  "id": "EV-DEU-0001",
  "name": "Tesla Gigafactory Berlin-Brandenburg",
  "aliases": ["Giga Berlin"],
  "company": "Tesla",
  "origin": "USA",
  "country": "DEU",
  "city": "Grünheide",
  "lat": 52.400,
  "lng": 13.825,
  "sector": "EVs",
  "projectType": "vehicle_assembly",
  "product": "Model Y",
  "status": "Operating",
  "announced": "2019-11-12",
  "prodStarted": "2022-03-22",
  "investmentM": 5500,
  "targetProduction": 500000,
  "productionUnits": "vehicles/year",
  "isFDI": true,
  "region": "Europe",
  "postIRA": false,
  "license": "CC-BY-4.0",
  "verificationTier": 1,
  "verifiedBy": "A. Rojas",
  "verifiedDate": "2026-04-24",
  "sources": {
    "company":          "https://www.tesla.com/giga-berlin",
    "investmentM":      "https://www.electrive.com/2024/08/05/tesla-wants-to-expand-grunheide-under-certain-conditions/",
    "announced":        "https://www.tesla.com/giga-berlin",
    "prodStarted":      "https://www.electrive.com/2022/03/22/tesla-starts-delivering-model-ys-from-grunheide/",
    "targetProduction": "https://www.euronews.com/next/2023/07/21/tesla-aims-to-double-production-capacity-in-german-gigafactory-targeting-1-million-evs-ann"
  }
}
```

## Run the validator

```bash
python3 projects/nzipl/data/validate_ev_record.py projects/nzipl/data/nzipl_ev_greenfield_global.json
```

Exit 0 = clean. Non-zero = fix and re-run. The validator replaces manual checklist walks.
