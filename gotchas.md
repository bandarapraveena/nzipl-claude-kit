# Known Gotchas

Data and API issues that cause silent failures. Each entry documents a problem that was discovered the hard way. Check here before debugging a pipeline or deliverable.

## OEC API

### HS6 ID padding
OEC uses padded IDs (e.g., `16850760` or `17870829`). To extract the actual HS6 code: `str(oec_id)[-6:]`. The leading digits are internal OEC prefixes.

### Mexico BACI ID
Mexico's country identifier in `trade_i_baci_a_22` is `namex`, not `mexxx` or `mex`. This is a BACI convention, not OEC-specific.

### 870839 (braking systems) missing from BACI 2022
HS6 code 870839 has no data in the `baci_a_22` cube. Workaround: fall back to `baci_a_02` cube with year=2024.

### Response wrapper
OEC API returns records inside a `data` key. Always use `result.get("data", result)` or `result["data"]` to extract the actual records. Forgetting this returns the metadata wrapper instead of trade data.

### Bot protection
OEC sits behind Cloudflare. Requests without a browser-like `User-Agent` header get blocked silently (empty responses or 403). Always include: `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`.

### BOM encoding
CSV files from external sources (government portals, INEGI) may have a BOM character at the start. Use `encoding='utf-8-sig'` when reading with Python.

## DataMexico API

### `/data` endpoint missing manufacturing
The `/data` endpoint drops sectors 31-33 (Manufacturing), 43, 51, 54 from DENUE results. This is silent -- you get data back, but manufacturing is missing. **Workaround**: Use `/stats/rca` with a multi-month parameter (e.g., `Month=20250522,20241126,20240523`). Single-month queries also fail to meet thresholds.

### HS4 drilldown naming
DataMexico uses `HS4` (not `Product 4 Digit`) as the drilldown name for municipality trade data. HS4 IDs include a chapter prefix (e.g., `20702` = chapter 2 + HS4 0702). Extract last 4 digits for the actual HS4 code.

## Geographic Data

### State name normalization
GeoJSON files and data JSONs use different state names for 4 Mexican states. Build a normalization map:
- Coahuila / Coahuila de Zaragoza
- Michoacan / Michoacan de Ocampo
- Queretaro / Queretaro de Arteaga
- Veracruz / Veracruz de Ignacio de la Llave

### Industrial parks state names
DataMexico uses accent-free full names (e.g., "Coahuila de Zaragoza"). Pipelines that join parks to other datasets need 3 separate state name maps: one for energy profiles, one for RCA/DENUE data, and one for special cases like "Estado de Mexico" vs "Mexico" in RCA data.

## D3 / Browser

### Headless screenshots
Content more than ~8000px down the page renders black in headless browser screenshots. Workaround: clone the target slide to the top of the DOM before screenshotting.

### `const` redeclaration
If a draw function already declares a `const` variable in scope, do not redeclare it. JavaScript will throw a SyntaxError. Reuse the existing variable or use a different name.

### D3 transitions in headless
Transitions do not fire in headless preview environments. Use `.interrupt()` and set attributes directly for verification.

## FDI Data (fDi Markets)

### Investment figures include multi-phase totals
fDi Markets often reports the total projected investment across all phases of a project, not just the initial commitment. Press releases typically cite the initial phase only. Example: LG/GM Spring Hill listed as $3.2B in fDi Markets, but press releases cite $2.3B initial + $275M expansion = $2.575B. When sourcing column S, flag discrepancies with `[UNVERIFIED]` and note both figures.

### Duplicate rows for project phases
Some projects appear as multiple rows in FDI_Combined (e.g., CATL Debrecen rows 79 and 84 with $8.2B and $8.6B). These represent different phases or revised estimates of the same project, not separate investments. Source both rows but note the relationship.

### Project IDs are not always fDi Markets format
Most rows use `FDI{digits}` IDs from fDi Markets, but some use custom IDs (e.g., `Battery 17.1`). These were likely added manually and may have thinner source coverage.

### Cancelled/suspended projects need cancellation-specific sources
For projects with status "Cancelled" or "Suspended", the original announcement URL confirms the project existed but not that it was cancelled. Search specifically for cancellation news (e.g., "Northvolt Heide cancelled" or "LG Indonesia battery exit").
