# Net Zero Industrial Policy Lab -- Claude Code Context

Shared context for the NZIPL team. This file loads automatically in any Claude Code session opened from this repo.

## The Lab

The Net Zero Industrial Policy Lab at Johns Hopkins University identifies and sequences clean industrial opportunities for countries using economic complexity methods. Primary outputs are Play Cards, Constraint Maps, and Chart Packs delivered as interactive HTML scrollytelling and slide decks.

Website: netzeropolicylab.com
Platform: cice.netzeropolicylab.com (Clean Industrial Capabilities Explorer)

## Key Outputs

| Deliverable | Format | Description |
|-------------|--------|-------------|
| Play Cards | HTML scrollytelling (8 sections) | Target activities, inputs, standards, sequencing, finance architecture for a single play |
| Constraint Maps | HTML scrollytelling | Ranked bottleneck maps per play with finance annex |
| Chart Packs | HTML/PPTX | Standardized country-level visualization sets |
| Cross-country Comparators | HTML | Visual products comparing indicators across countries |
| Infrastructure Maps | HTML (Leaflet) | Interactive maps overlaying energy grid, RCA, supply chain, and investment data |

## Sprint Structure

Each country follows a 5-month production + 1-month QA cycle:

| Sprint | Output | Description |
|--------|--------|-------------|
| S0 | Play Selector | Data-driven ranking of 10 candidate plays using RCA, relatedness, trade volume |
| S1 | Play Cards (2-3) | Deep-dive per play: components, geography, trade, standards, sequencing, finance |
| S2 | Constraint Maps | Bottleneck analysis by category with finance annex |
| S3 | Platform Products | Cross-country comparators, methods notes |
| S4 | QA and Synthesis | Review, consistency checks, final packaging |

## Country Status

| Country | Status | Notes |
|---------|--------|-------|
| Mexico | Active (S1) | Top 3 plays: Auto Supplier Upgrading, EV Components, Grid Hardware |
| Brazil | Planned | Illustrative plays in concept note, no data work started |
| India | Planned | Illustrative plays in concept note, no data work started |

## Data Sources

| Source | Cube/Endpoint | Used For | Auth |
|--------|--------------|----------|------|
| OEC (oec.world) | `trade_i_baci_a_22` | RCA computation, bilateral trade (BACI 2022) | API key + browser User-Agent header |
| OEC Mexico | `trade_s_mex_y_hs6` | National + subnational exports/imports | Same |
| OEC USA | `trade_s_usa_state_m_hs` | US state-level trade | Same |
| OEC Canada | `trade_s_can_m_hs` | Canadian trade | Same |
| DataMexico | `economy_foreign_trade_mun` | Municipality-level HS4 exports | Public, no auth |
| DataMexico | `/stats/rca` (DENUE) | Manufacturing employment by state/industry | Public, multi-month parameter required |
| DataMexico | `industrial_parks` | AMPIP-registered industrial parks | Public |
| BNEF | Manual JSON | Green manufacturing project pipeline | Pre-compiled |
| OSM (earth-osm) | GeoJSON | Transmission lines, substations, generators | Public |
| WRI GPPD | JSON | Power plants (277 plants, 62K MW for Mexico) | Public, v1.3 |
| OpenDataSoft/INEGI | GeoJSON | Municipality boundaries | Public |

### OEC API Reference

- Base: `https://api-v2.oec.world/tesseract/data.jsonrecords`
- Auth: Three headers required:
  - `Authorization: Bearer <key>`
  - `X-API-KEY: <key>`
  - `token=<key>` as query param
- **Critical**: Also requires a browser-like `User-Agent` header (Cloudflare protection)
- Response: Records are inside a `data` key: use `result.get("data", result)` or `result["data"]`

### DataMexico API Reference

- Base: `https://api.datamexico.org/tesseract/`
- Endpoints: `/data` (cubes) and `/stats/rca` (specialization)
- No auth required
- **Critical**: The `/data` endpoint is missing manufacturing sectors (31-33). Use `/stats/rca` with multi-month parameter (e.g., `Month=20250522,20241126,20240523`) to get all sectors.

## Play Card Structure (8 Sections)

| Section | Content |
|---------|---------|
| Hero | Play name, key metric cards, one-sentence framing |
| 01 The Play | Horizontal grouped bars (exports/imports by category) |
| 02 Components | Category cards with mini RCA + state bars |
| 03 Geography | State x category heatmap (matrix + map toggle) |
| 04 Trade | Stacked bars (destinations, sources) |
| 05 Standards | HTML table of certification requirements |
| 06 Sequencing | Swimlane Gantt (4 phases, 0-72 months) |
| 07 Takeaways | 3x2 card grid |
| 08 Finance | Capex ranges, gap analysis, instrument heatmap, actor coordination |

## Pipeline Conventions

- **Language**: Python 3, stdlib only (json, argparse, urllib). No pip dependencies.
- **Output**: JSON files. All data embedded in HTML deliverables as `const DATA = {...}`.
- **Caching**: API responses cached locally (`*_cache.json`). Use `--skip-api` flags to reuse caches.
- **Self-contained**: HTML deliverables make no runtime API calls. Fully offline-capable.

## Design System

Use the `/nzipl-design` skill for all visual formatting. Key tokens:
- Dark theme: body `#1A1B1E`, cards `#25262B`
- Brand green: `#56a360` (accent), `#7fc77f` (links)
- Font: Archivo (headings 600-700, body 400)
- Attribution: "Net Zero Industrial Policy Lab | Johns Hopkins University | netzeropolicylab.com"

## Commands

| Command | Description |
|---------|-------------|
| `/enrich-fdi` | Enrich FDI dataset rows with per-row source URLs via web research. Reads xlsx, searches for confirming articles, writes URLs to source columns. |

## Tasks

| Task | File | Status |
|------|------|--------|
| FDI Source Enrichment | `tasks/enrich-fdi.md` | In progress (20/698 rows, top investments done) |

## References

- `glossary.md` -- Terms, acronyms, internal vocabulary
- `gotchas.md` -- Known data/API issues that cause silent failures
- `discoveries.md` -- Team-contributed findings (append here when you learn something)
- `CONTRIBUTING.md` -- How to add to this kit
