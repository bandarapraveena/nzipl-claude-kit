# Common mistakes

Append-only log of mistakes Lab members have made while gathering EV greenfield records. Follows the same pattern as `discoveries.md` at the kit root — one line per entry, most recent at the top. Read before each batch. Add a line every time you discover you made (or nearly made) a mistake, so the next researcher doesn't repeat it.

## Format

```
- YYYY-MM-DD | Name | One-line description of the mistake and how to avoid it [tags]
```

Tags: `[tier]`, `[dedup]`, `[scope]`, `[source]`, `[schema]`, `[currency]`, `[locale]`.

## Seed entries (from protocol design)

These are mistakes worth anticipating before the first real batch. Delete or expand as real patterns emerge.

- 2026-04-24 | Gilberto | Tier 2 inflation: counting three URLs that are all reproductions of one press release as "three sources". Require that at least one source be independently authored (not derived). [tier] [source]
- 2026-04-24 | Gilberto | Using the largest announced investment figure instead of the most recent — some projects are revised downward after initial announcements. Track all revisions in investmentM_history. [currency]
- 2026-04-24 | Gilberto | Confusing MWh storage capacity with annual GWh throughput. targetProduction is per-year, not cumulative nameplate. [schema]
- 2026-04-24 | Gilberto | Writing parent HQ country (origin) as destination country. Example: Tesla is USA, but Tesla Giga Berlin's country is DEU. [schema]
- 2026-04-24 | Gilberto | Skipping Korean / Chinese / Japanese sources for projects with Asian parents. The English press lags — usually by days to weeks. Use the search-playbook language queries. [locale] [source]
- 2026-04-24 | Gilberto | Treating a Phase 2 expansion as a new record instead of updating the existing record's investmentM_history and targetProduction. Check coordinates and existing records before creating new ones. [dedup]
- 2026-04-24 | Gilberto | Marking a project "Operating" based on a single 2024 trade-press mention. Status "Operating" requires explicit confirmation (company PR, annual report, or named-author piece describing current production). [tier]
- 2026-04-24 | Gilberto | Recording an MOU as status "Planned" at Tier 1. MOUs are Tier 3, status "Announced" at most. Require a permit filing or groundbreaking date for higher status. [tier] [scope]
- 2026-04-24 | Gilberto | Citing paywalled FT/Bloomberg articles without finding the Reuters/Nikkei free mirror. The public-citable policy requires public URLs. [source]
- 2026-04-24 | Gilberto | Using a fabricated URL when a search returns nothing. Leave the field empty rather than inventing a citation. [source]
- 2026-04-24 | Gilberto | Forgetting to update aliases when a company renames (LG Chem → LG Energy Solution, FCA+PSA → Stellantis, Contemporary Amperex → CATL). The dedup protocol depends on this. [dedup]
- 2026-04-24 | Gilberto | Treating pack assembly plants as cell factories. They're scope-valid but go under projectType: pack, not cell — critical for capacity math. [scope] [schema]
- 2026-04-24 | Gilberto | Germany batch: initially assigned postIRA=true to pre-Aug-2022 projects (Northvolt Heide 2022-03, VW Salzgitter 2021-03, Ford Cologne 2021-02, BMW Leipzig 2022-06). The IRA signing date is 2022-08-16; earlier announcements must have postIRA=false regardless of project location. Automate postIRA derivation from announced field. [schema]
- 2026-04-24 | Gilberto | Initially wrote Mercedes eCampus, Porsche V4Smart, Microvast, Valmet Kirchardt, Kedali at Tier 2/3 while leaving status=Operating or Under Construction. Violates the status×tier matrix: Operating/Under Construction/Closed require Tier 1. Fix either tier (add more sources) or status (downgrade to Paused/Planned), not just leave the violation. Always run the validator before closing the batch. [tier] [schema]
- 2026-04-24 | Gilberto | FDI row "CATL Kirchardt" is Valmet Automotive's plant (CATL minority stake). Naming a record after the dominant FDI header without checking the operator produces an inaccurate `company` field. Always identify the operator from Tier A source before copying the FDI row's Parent company. [dedup] [schema]

## Promotion

When a mistake keeps appearing (three+ entries of the same pattern), promote it to `references/red-flags.md` as a permanent red flag and remove the log entries. Use a PR per `CONTRIBUTING.md`.

## What NOT to log here

- One-off typos in a specific record (fix the record, move on)
- Tool-specific frustrations unrelated to methodology (log in `discoveries.md` or `gotchas.md`)
- Pattern observations that aren't actionable mistakes (those go in `discoveries.md`)
