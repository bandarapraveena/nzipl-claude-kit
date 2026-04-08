# Discoveries

Team-contributed findings about data sources, APIs, methodology, and tooling. When you learn something that would save a colleague time, append it here.

If a discovery is significant enough to become a permanent reference, it will be promoted to `gotchas.md` or `glossary.md` during periodic reviews.

## Format

```
- YYYY-MM-DD | Author | One-line finding
```

## Log

- 2026-04-07 | Gilberto | DataMexico /data endpoint silently drops manufacturing sectors 31-33; use /stats/rca with multi-month parameter instead
- 2026-04-07 | Gilberto | OEC requires browser User-Agent header (Cloudflare); requests without it return empty responses or 403
- 2026-04-07 | Gilberto | Mexico BACI country ID is "namex" not "mexxx" in trade_i_baci_a_22
- 2026-04-07 | Gilberto | HS6 870839 (braking systems) missing from baci_a_22; fall back to baci_a_02 with year=2024
- 2026-04-07 | Gilberto | Municipality HS4 IDs in DataMexico include chapter prefix (e.g., 20702); extract last 4 digits for actual HS4 code
- 2026-04-08 | Gilberto | FDI enrichment: one web search per row covers 5-7 of 8 source columns; don't search per-column
- 2026-04-08 | Gilberto | FDI enrichment: sort by investment size descending; projects >$1B have near-100% press coverage, <$100M drops off sharply
- 2026-04-08 | Gilberto | FDI enrichment: Battery post-2020 covered by electrive, InsideEVs, Battery-News; Solar by PV Magazine, PV Tech, Renewables Now; Wind coverage thinner
- 2026-04-08 | Gilberto | FDI enrichment: fDi Markets investment figures sometimes include projected multi-phase totals; press releases cite initial phase only (e.g., LG/GM Spring Hill: $3.2B fDi vs $2.575B press)
- 2026-04-08 | Gilberto | FDI enrichment: Column T (ownership share) and V (completion date) are hardest to source; skip on first pass if initial search misses them
