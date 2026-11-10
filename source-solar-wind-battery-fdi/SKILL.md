---
name: source-solar-wind-battery-fdi
description: "Enrich the Lab's clean-energy FDI dataset (Solar / Wind / Battery / EV projects) with publicly citable source URLs. Use when the user asks to source, enrich, verify, or audit FDI rows. Primary invocation is batch enrichment: 'source the next 10 rows', 'enrich largest 50', 'audit rows 100-150'. Reads the master, finds rows missing citations in the source columns, fills them with Tier A / Tier B URLs only (wikipedia.org, social media and PR-wire-only sources are hard-rejected), and every URL is page-checked by MasterEdit before it is written. Disagreements between a source and the project data become proposals for the owner; the skill never writes columns A to O. Validator at validate_fdi_sources.py."
---

# Source Solar / Wind / Battery FDI

Enrich the clean-energy FDI master with per-row source URLs, and propose corrections to the project data (columns A to O) when the sources disagree with it. The web source outranks the original fDi Markets value, and the owner decides what changes. This skill writes URLs; it never writes project data.

> **Writing to the LCT-FDI master (`FDI_All_ToSource.xlsx`): rules since 2026-09-29, extended 2026-10-29**
> - Column letters in this skill (A to O, L, P to W) are logical labels from the original 24-column layout, not positions. The master has 28 columns (Expansion, Phase, Joint Venture Local State were added). Address columns by header name.
> - Every write goes through `LCT-FDI/bin/master_io.py` (`MasterEdit`). It backs up the file, refuses any cell change you did not request, rejects edits that add validator errors, and logs to `data_changes_log.csv`. Never write the file with openpyxl or pandas.
> - **Every cited page is read before the cell is written.** `MasterEdit` fetches each URL (`LCT-FDI/bin/source_check.py`) and refuses a source cell whose page does not name the firm, or, for the amount, city and date columns, does not state the value. A page that fails can be written only with the `[UNVERIFIED] ` prefix and a `why=`. Check before you compose: `python3 ../LCT-FDI/bin/source_check.py <Project ID> "<column>" <url>`. The rules and limits of the check are in `LCT-FDI/DATA_EDITING.md`, section *Source check*.
> - **This skill never changes columns A to O.** A disagreement between the source and the cell goes into the batch's proposals file (step 6 below). The owner says yes; then `MasterEdit` applies it with the reason in `why=`.
> - No cell highlighting. The reason lives in `why=`, the verdict in `data_changes_log.csv` and `source_evidence.csv`.
> - `fDi Markets (FT)` capex estimates are kept as amounts. Reject only the $39.9m placeholder. Prefer a public figure when you find one.
> - An amount with no source: leave the cell blank and set Source (Amount) to exactly `Investment value not publicly disclosed`.
> - Acquisitions (including minority stakes, and ICE-to-EV plant retooling) count as FDI; BESS factories are Battery; a whole-value-chain figure that cannot be split stays on the project in full.
> - Never take an amount or URL from a neighbouring row. Every URL must be about this row's firm and this plant; `bin/validate_master.py` (rules R12, R13, R15) flags cross-firm URLs.

The defining principle: **prefer primary channels; never cite tertiary summaries.** This skill follows the same sourcing tiers as `/gather-ev-greenfield`. Wikipedia, social media and self-published platforms are rejected even if they are the only result.

**Out of scope:** dedup against the EV greenfield JSON (separate workstream), creating new rows, changing project data.

## Primary invocation: batch enrichment

> "Source the next 10 rows." "Enrich the largest 50 by capex." "Fill rows 200 to 250."

1. **Dedup pass** (once per fresh file, before sourcing). Find Chinese-parent duplicates: two rows describe the same project, `Company Country (HQ)` = `China`, one `Project ID` starts with `HAR` and the other does not. The HAR row is the canonical record. Matching details that matter:
   - **City normalization must strip parentheticals.** "Erfurt" matches "Erfurt (Arnstadt)"; "Bayan Lepas" matches "Bayan Lepas (Penang)". Use `re.sub(r'\([^)]*\)', '', s).strip().lower()` before comparing cities.
   - **Company name matching must be fuzzy** (token-alias). "Contemporary Amperex Technology (CATL)" must match "CATL"; "Eve Energy" must match "EVE Energy". Tokenize lowercased, strip parentheticals and punctuation, drop entity-suffix tokens (`co`, `ltd`, `corp`, `group`, `holding`, `technology`, `industrial`, `international`, `global`, `energy`, `new`, `inc`, `company`, `limited`) **and sector tokens** (`solar`, `battery`, `wind`, `pv`, `power`, `system(s)`, `material(s)`, `manufacturing`, `auto`, `motor(s)`, `cobalt`). Two names match if the remaining token sets intersect. Without dropping sector tokens, "JA Solar" falsely matches "QC Solar Corp".
   - **Run the pass twice**, strict first, then with the looser city normalization.
   - **Flag non-HAR pairs too** (same parent, city, country, both with fDi numeric IDs: R15/R37 VW Sagunto, R50/R80 VW Chattanooga, R52/R67 Umicore Nysa). One is often a partial figure or a sub-component.
   - **Action:** list every pair in the proposals file with the row to keep. The owner applies `drop_row`. Never delete a row from this skill.
2. **Load state.** Read the master with pandas, read-only. Ground truth for what is sourced is `python3 audit_fdi_sources.py <file>`; `tasks/enrich-fdi-progress.json` is the operator log, and it has drifted from the file before.
3. **Pick the batch.** Rows with empty source cells, in the user's priority (`largest` by Capital Investment, `newest` by Year Announced, `sequential` by row). Default ten rows. Within a row, source the amount first: it is where an error costs most and where the page check is strictest.
4. **Verify each row** per `references/verification-protocol.md`. Tier A primary preferred; Tier B trade press to corroborate. Forbidden domains never cited (`references/sources.md`). Red flags in `references/red-flags.md`.
5. **Check, then write the URLs.** Run `source_check.py` on each candidate URL for the cell it will go in. Write the batch as one `MasterEdit` block (`batch=`, `who=`, a `why=` per cell). A FAIL refuses the whole block: replace the URL, or tag it `[UNVERIFIED] ` with the reason in `why=`. Do not switch the check off.
6. **Propose corrections to A to O.** For every cell the sources contradict, add a line to `outputs/proposals/<batch>.md` in the owner's format (*Row · Ours · What the source says · Proposed fix*), with a ready-to-run `MasterEdit` block per ten rows and a `DECISION` item wherever two readings are possible. `references/reconciliation.md` says which cells are proposable and how to read scope. Nothing in this file touches the master until the owner says yes. When a proposal changes the amount, put the new `Capital Investment (US$m)` and the new `Source (Amount)` in the same block: the page check reads the amount as it will be after the edit.
7. **Validate.** `python3 ../LCT-FDI/bin/validate_master.py` (0 errors) and `python3 validate_fdi_sources.py <file>` (exit 0).
8. **Log before the next batch.** Append the batch to `tasks/enrich-fdi-progress.json` and to the quality flags document now, with the fallbacks, the `[UNVERIFIED]` cells and the proposals written. A session that runs out of budget mid-batch then leaves a log, not a gap.

## Secondary invocations

| Ask | Do |
|-----|----|
| "Source row N" | Single-row: same workflow, batch of 1. |
| "Re-audit filled rows" or "check country X" | `python3 ../LCT-FDI/bin/check_source_alignment.py --countries "X" --snippets`, then read every FAIL / SHARE / unfetchable page and propose fixes in batches of ten. Replace forbidden-domain and dead citations. |
| "Source largest N" | Priority `largest`, batch of N. |
| "Source rows in country X" | Filter by Destination Country; same workflow. |

## Workflow constraints

- **Propose, never reconcile.** A source that contradicts a cell in A to O produces a proposal line, not a write. `references/reconciliation.md` has the per-column rules and the recurring scope traps.
- **Never cite** `wikipedia.org`, `grokipedia.com`, `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com`, `medium.com`. The validators hard-reject these.
- **Never write a non-URL value** to a source column except `fDi Markets (FT)` and, in Source (Amount), `Investment value not publicly disclosed`. Empty cells are preferred over forbidden citations.
- **Disambiguate the facility.** Every URL must distinguish the specific city / permit / JV brand named in the row. Generic "Company X expanding in Country Y" is not a valid location citation; the page check fails it.
- **Syndication of one PR is one source.** Do not count company PR + Reuters pickup + Electrive pickup as three.
- **Language-first for non-English parents.** Korean / Japanese / Chinese / German / French / Spanish / Portuguese: search the local engine first; details in `references/sources.md`.
- **Strip tracking from URLs.** `utm_source=chatgpt` and similar tags mark a URL copied from a chat answer rather than read. Strip the tag, read the page, then decide. `validate_master.py` warns on them.
- **One batch, one MasterEdit block, one log entry.** Ten rows, then the log, then the next ten.

## File structure

```
source-solar-wind-battery-fdi/
├── SKILL.md                        <- You are here
├── validate_fdi_sources.py         <- Format gate: forbidden domains, malformed cells. Run after every batch
├── audit_fdi_sources.py            <- Ground truth: which rows are fully / partly / not sourced
└── references/
    ├── schema.md                   <- Column map A to W + value formats
    ├── sources.md                  <- Tier A primaries + forbidden-domain list + language playbook
    ├── verification-protocol.md    <- Tier matrix + status x tier rule + paywall rule + page check
    ├── reconciliation.md           <- What becomes a proposal, how to read scope, the owner's rules
    └── red-flags.md                <- PR-wire-only, MOU, stale, wrong-figure, wrong-plant signals
```

The page check itself lives in the master's repo: `LCT-FDI/bin/source_check.py`, documented in `LCT-FDI/DATA_EDITING.md`.

## Reading budget

Four files, about 15 minutes:
1. `references/schema.md`: column map, what URL goes where, date formatting (letters are logical labels; write by header name)
2. `references/verification-protocol.md`: tier matrix, status x tier rule, the page check
3. `references/reconciliation.md`: what becomes a proposal, the dedup rule, the owner's rules on FX, JV shares, government money and unsplittable figures
4. `LCT-FDI/DATA_EDITING.md`, section *Source check*: what the gate refuses and how to get through it honestly

`sources.md` and `red-flags.md` are referenced on demand mid-batch.

## Defaults

| Decision | Default |
|----------|---------|
| Working file | `../LCT-FDI/FDI_All_ToSource.xlsx` |
| Batch size | 10 |
| Priority | `largest` (by Capital Investment) |
| Page check | On. `MasterEdit(check_sources=True)`; never `False` from this skill |
| Proposals | `../LCT-FDI/outputs/proposals/<batch>.md` |
| Date format (U, V) | MM/DD/YYYY; year-only sources annotated `(year only)` |
| Paywalled sources | Allowed only with a free mirror; cite the mirror |
| Fallback | `fDi Markets (FT)` only when no Tier A/B exists after local-language + IR + IPA passes |
| Uncertain attribution | Prefix `[UNVERIFIED] ` and say why in `why=` |
| Status x tier | `Completed` / `Operational` need Tier 1; `Announced` any tier |

## Related

- `/gather-ev-greenfield`: separate workstream that builds a global EV greenfield JSON. Same sourcing standard, different output. Do not couple to it.
- `/merge-fdi-sources`: second-pass merge of a curated list into cells that still say `fDi Markets (FT)`.
- `nzipl-design`: apply when rendering this dataset.

## Done

- Dedup pairs listed in the proposals file (none deleted by this skill).
- Target row count sourced, every URL through the page check (OK, or `[UNVERIFIED]` with a reason).
- Proposals file written for every A to O disagreement found, with `DECISION` items marked.
- `python3 ../LCT-FDI/bin/validate_master.py` reports 0 errors; `python3 validate_fdi_sources.py <file>` exits 0.
- `tasks/enrich-fdi-progress.json` and the quality flags document updated before the next batch began.
- Rows that fell back to `fDi Markets (FT)` listed in the batch entry's `notes` with the search passes attempted.
