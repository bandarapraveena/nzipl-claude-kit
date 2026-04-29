---
name: source-solar-wind-battery-fdi
description: "Enrich the Lab's clean-energy FDI dataset (Solar / Wind / Battery projects) with publicly citable source URLs. Use when the user asks to source, enrich, verify, or audit FDI rows. Primary invocation is batch enrichment: 'source the next 20 rows', 'enrich largest 50', 'audit rows 100–150'. Reads xlsx, finds rows missing citations in columns P–W, fills them with Tier A / Tier B URLs only — wikipedia.org, social media, and PR-wire-only sources are hard-rejected. Also dedups Chinese-parent rows (drops non-HAR ID when a HAR ID describes the same project) and reconciles A–O cells against source (preferring source; highlights changed cells in yellow). Validator at validate_fdi_sources.py."
---

# Source Solar / Wind / Battery FDI

Enrich a clean-energy FDI xlsx with per-row source URLs **and reconcile A–O cells against those sources.** The web source is the source of truth; the Excel data (originally from fDi Markets) is the starting hypothesis. When they disagree, update the Excel cell and highlight the change in yellow.

The defining principle: **prefer primary channels; never cite tertiary summaries.** This skill follows the same sourcing tiers as `/gather-ev-greenfield`. Wikipedia, social media, and self-published platforms are rejected even if they are the only result.

**Out of scope:** dedup against the EV greenfield JSON (separate workstream), creating new rows.

## Primary invocation: batch enrichment

> "Source the next 20 rows." "Enrich the largest 50 by capex." "Fill rows 200–250."

1. **Dedup pass** (run once per fresh xlsx, before sourcing) — drop Chinese-parent duplicates: where two rows describe the same project and `Company Country (HQ)` = `China`, and one row's `Project ID` starts with `HAR` while the other does not, **delete the non-HAR row**. The HAR ID is the kept canonical record. **Critical matching details (lessons learned):**
   - **City normalization must strip parentheticals.** "Erfurt" matches "Erfurt (Arnstadt)"; "Bayan Lepas" matches "Bayan Lepas (Penang)"; "Kulim" matches "Kulim (Hi-Tech Park)". Use `re.sub(r'\([^)]*\)', '', s).strip().lower()` before comparing cities.
   - **Company name matching must be fuzzy** (token-alias). "Contemporary Amperex Technology (CATL)" must match "CATL"; "Eve Energy" must match "EVE Energy". Tokenize each name lowercased, strip parentheticals/punctuation, drop common entity-suffix tokens (`co`, `ltd`, `corp`, `group`, `holding`, `technology`, `industrial`, `international`, `global`, `energy`, `new`, `inc`, `company`, `limited`) **and sector tokens** (`solar`, `battery`, `wind`, `pv`, `power`, `system(s)`, `material(s)`, `manufacturing`, `auto`, `motor(s)`, `cobalt`). Two names match if their remaining token sets intersect. (Sector tokens are critical — without dropping them, "JA Solar" falsely matches "QC Solar Corp".)
   - **Run dedup at least twice on a fresh dataset.** First pass with strict matching; second pass with looser city normalization typically catches additional duplicates that hide behind parenthetical city suffixes.
   - **Flag non-HAR/non-HAR potential duplicates** in the batch log even though the rule does not auto-drop them. Common pattern: same parent + city + country, both with fDi numeric IDs (e.g. R15/R37 VW Sagunto, R50/R80 VW Chattanooga, R52/R67 Umicore Nysa). One row is often a partial-figure or sub-component.
2. **Load state** — open the xlsx with `openpyxl`. Read `tasks/enrich-fdi-progress.json` to find `next_unsourced_row`.
3. **Pick the batch** — rows where columns P–W are all empty, sorted by user priority (`largest` by Capital Investment, `newest` by Year Announced, `sequential` by row number). Default batch size: 20.
4. **Verify each row** — gather sources per `references/verification-protocol.md`. Tier A primary preferred; Tier B trade press to corroborate. Forbidden domains never cited (see `references/sources.md`).
5. **Reconcile A–O against source** — when the source contradicts a cell in columns A–O, update the cell to match the source and apply a yellow `PatternFill` (`FFFFFF00`) to mark it as changed. The web source is preferred over the original fDi Markets data. See `references/reconciliation.md` for which fields are reconcilable and how to handle ambiguous cases. Capital Investment (column L) is the most common reconciliation target.
6. **Write + validate** — save the xlsx after each batch. Run `python3 validate_fdi_sources.py <file.xlsx>`. Exit non-zero = fix and re-run before reporting done.
7. **Log** — update `tasks/enrich-fdi-progress.json` (counters + new `batches[]` entry with notes on fallbacks and a list of A–O cells changed during reconciliation).

## Secondary invocations

| Ask | Do |
|-----|----|
| "Source row N" | Single-row: same workflow, batch of 1. |
| "Re-audit filled rows" | Sample rows already filled; re-resolve URLs; replace any forbidden-domain or 404 citations. Update `verifiedDate` in batch notes. |
| "Source largest N" | Priority `largest`, batch of N. |
| "Source rows in country X" | Filter by column F (Destination Country); same workflow. |

## Workflow constraints

- **Reconcile A–O against source.** When the cited source contradicts a cell in columns A–O, update the cell to match the source and apply a yellow `PatternFill` (`FFFFFF00`). Source > Excel. Capital Investment (column L) is the most frequently reconciled field. See `references/reconciliation.md` for per-column rules.
- **Never cite** `wikipedia.org`, `grokipedia.com`, `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com`, `medium.com`. The validator hard-rejects these.
- **Never write a non-URL value** to P–W except the explicit fallback `fDi Markets (FT)`. Empty cells are preferred over forbidden citations.
- **Disambiguate the facility.** Every URL must distinguish the specific city / permit / JV brand named in columns C–G. Generic "Company X expanding in Country Y" is not a valid R citation.
- **Syndication of one PR is one source.** Don't double-count company PR + Reuters pickup + Electrive pickup.
- **Language-first for non-English parents.** Korean / Japanese / Chinese / German / French / Spanish / Portuguese — search local engine first; details in `references/sources.md`.
- **Run the validator after every batch.** Fix forbidden URLs and malformed dates; don't write through them.

## File structure

```
source-solar-wind-battery-fdi/
├── SKILL.md                        ← You are here
├── validate_fdi_sources.py         ← Run before every save
└── references/
    ├── schema.md                   ← Column map A–W + value formats + highlight convention
    ├── sources.md                  ← Tier A primaries + forbidden-domain list + language playbook
    ├── verification-protocol.md    ← Tier matrix + status × tier rule + paywall rule
    ├── reconciliation.md           ← When and how to update A–O cells from source
    └── red-flags.md                ← PR-wire-only, MOU, stale, reverse-announcement signals
```

## Reading budget

Three files, ~15 minutes:
1. `references/schema.md` — column map A–W, what URL goes where, date formatting, yellow-highlight convention
2. `references/verification-protocol.md` — tier matrix + status × tier rule
3. `references/reconciliation.md` — which A–O cells to update from source, dedup rule for Chinese-parent HAR pairs

`sources.md` and `red-flags.md` are referenced on demand mid-batch.

## Defaults

| Decision | Default |
|----------|---------|
| Batch size | 20 |
| Priority | `largest` (by Capital Investment, column L) |
| Date format (U, V) | MM/DD/YYYY; year-only sources annotated `(year only)` |
| Paywalled sources | Allowed only with free mirror; cite the mirror |
| Fallback | `fDi Markets (FT)` only when no Tier A/B exists after local-language + IR + IPA passes |
| Uncertain attribution | Prefix `[UNVERIFIED] ` |
| Status × tier | `Completed` / `Operational` → Tier 1 required; `Announced` → any tier |

## Related

- `/gather-ev-greenfield` — separate workstream that builds a global EV greenfield JSON. Same sourcing standard, different output. Do not couple to it.
- `nzipl-design` — apply when rendering this dataset.

## Done

- Dedup pass run (Chinese-parent HAR/non-HAR duplicates resolved).
- Target row count sourced.
- A–O cells reconciled against source where they conflicted (changed cells filled yellow).
- `python3 validate_fdi_sources.py <file.xlsx>` exits 0.
- `tasks/enrich-fdi-progress.json` updated with new batch entry, totals, and a list of A–O cells changed during reconciliation.
- Rows that fell back to `fDi Markets (FT)` are noted in the batch entry's `notes` field with the search passes attempted.
