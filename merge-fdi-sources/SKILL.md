---
name: merge-fdi-sources
description: "Second-pass enrichment for FDI projects. Merges sources from a curated list into the master FDI_All_ToSource.xlsx. Auto-detects between two supported curated formats: a China_FDI_<Tech>.xlsx (Chinese-parent rows, matched by HAR ID) and a Globa_FDI_<Tech>_Manual.xlsx (non-HAR rows, matched by FDI ID). Use when the user asks to 'apply China sources', 'merge the manual battery list', or runs any post-SKILL sourcing round. Honors strict precedence: SKILL-found URLs in FDI_All_ToSource win over curated URLs (even when tagged [UNVERIFIED]); curated URLs only replace cells that say 'fDi Markets (FT)'. Reconciles Capital Investment (column L) to whichever source is ultimately cited in column S. Optional stage-2 pass (`--stage2`) tops up column Q for rows that didn't meet first-best, then marks any still-EMPTY Source (Amount) cells with 'Investment value not publicly disclosed' (fDi Markets (FT) estimates are kept) so they remain count-regression eligible. Writes only through LCT-FDI/bin/master_io.py (MasterEdit), which page-checks every URL; curated URLs whose page does not state the value are held back and reported, never merged."
---

# Merge FDI Sources

Second-round sourcing skill. The first round (`/source-solar-wind-battery-fdi`) populates source URLs by web research. This skill takes a separately curated list and merges its URLs into the master file (`FDI_All_ToSource.xlsx`) where — and only where — the SKILL pass had to fall back to `fDi Markets (FT)`.

## Write path (2026-10-29)

`merge_fdi_sources.py` saves nothing itself. It decides which cells change under the precedence rules, then hands the edits to `LCT-FDI/bin/master_io.py` (`MasterEdit`), which backs up the master, refuses any change it was not asked for, fetches every cited page and refuses a source cell whose page does not state the value, runs `bin/validate_master.py`, and logs each change to `data_changes_log.csv` and each verdict to `source_evidence.csv`. The master must therefore sit in its LCT-FDI checkout, with `bin/` beside it.

So that one bad curated URL does not abort a bulk merge, the script first runs the same page check (`bin/source_check.py`) on every curated URL it would merge and **holds back** the cells that fail: a page that does not name the firm or state the amount, city or year, or a share figure on a row that is not a JV. A held-back cell stays as it was (`fDi Markets (FT)`), and when the amount source is held back the amount is not changed either. Held-back cells are printed and written to `outputs/merge_heldback_<batch>.csv` beside the master, for a reader to fix in the curated list or write by hand with `[UNVERIFIED] ` and a reason. Pages that cannot be fetched are merged and listed (`--strict` holds them back too). `--dry-run` previews everything and writes nothing. `--no-page-check` exists for a batch verified by hand and is not the default.

Letters L and P–W in this document are logical labels for Capital Investment and the eight Source columns; the script finds them in the master by header name, because positions shift whenever the master gains a column. No cell highlighting: the reason for each change is in `why=` in the change log.

## Supported curated inputs (auto-detected)

| Input | Match key | Source columns (curated) | Capital col | Empty marker |
|-------|-----------|--------------------------|-------------|--------------|
| `China_FDI_<Tech>.xlsx` (sheet = `Battery` / `Solar` / `Wind` / …) | `HAR*` IDs in col 1 | 15-22 (P-W, contiguous) | 11 | `\` |
| `Globa_FDI_<Tech>_Manual.xlsx` (single sheet) | `FDI*` IDs in col 1 | 18, 19, 20, 21, 22, 23, 24, **26** (skips 25 = Tech source) | 13 | `NA` |

Detection runs on the first 200 rows of column 1 — whichever prefix dominates wins. Override with `--layout china|manual` if needed.

## Master file (target)

| File | Sheet | Role |
|------|-------|------|
| `FDI_All_ToSource.xlsx` | `All` | Columns A–O = facts, P–W = source URLs, X = operational. ID is column B. |

## Precedence rules (apply to both inputs)

1. **Column S (Source for Amount) is the priority cell.** All other source columns are secondary.
2. **SKILL URL beats curated URL — including `[UNVERIFIED]` SKILL URLs.** Do not replace a real URL (or `[UNVERIFIED] <url>`) in `FDI_All_ToSource` with a curated URL.
3. **Exception: cells equal to `fDi Markets (FT)` are replaceable.** If the curated list has a real URL for that cell, replace it. Applies to any of P–W, not just S.
4. **Column L (Capital Investment) follows the cited S source.** When S is replaced and the curated row carries a different L value, update L to the curated value (printed in the change log; no highlighting). If the curated row's L is empty (None / `\` / `NA`), leave the existing L untouched.
5. **Empty-marker tokens mean no-source-available.** Treat as if absent (`\` for the China list, `NA` for the manual list).
6. **Empty master cells are not Rule 3 candidates.** This skill does not invent sources where neither file has one.

## Workflow

1. **Identify the curated file** (China or manual). The script auto-detects from ID prefix; pass `--layout` to force.
2. **For China inputs, confirm the sheet name.** Defaults to the active sheet, but a China workbook can have multiple tech sheets — pass `--sheet Battery` (or Solar/Wind) to be explicit.
3. **Load both workbooks.** Master read through openpyxl and changed in memory only (stage 2 sees stage 1's result); curated with `data_only=True`.
4. **Build ID maps.**
   - Master: `{ID: [row_numbers]}` from sheet `All` (handles duplicates that survived dedup).
   - Curated: `{ID: row_number}`.
5. **For each ID present in both files, classify each source column (P–W):**
   - If master cell ≠ `fDi Markets (FT)` → **keep** (Rule 2).
   - If master cell = `fDi Markets (FT)` and curated cell is a real URL → **page-check, then replace**; a FAIL holds the cell back.
   - If master cell = `fDi Markets (FT)` and curated cell is empty → **skip**.
   - If master cell is empty/None → **skip** (Rule 6).
6. **Reconcile L.** If S was replaced and curated L is a real number, update master L; the page check reads the amount as it will be after the edit. If curated L is empty, leave master L alone even if S changed. If S was held back, L does not change.
7. **Hand the edits to `MasterEdit`.** It writes, validates and logs; `--dry-run` stops before the write. Then run `validate_fdi_sources.py` from the sister skill, which must exit 0.
8. **Report a per-row change log** (ID, row number, columns replaced, L delta) and the held-back list with each page verdict.

## Batch sizing

- Default: process **all matching rows in the curated list**. The work is mechanical and rule-based; there's no per-row research budget.
- If the user asks to start small ("first 10 rows"), iterate **in master-row order** (not curated-row order — reviewers read the master top-to-bottom) and stop after N.

## Stage 2 — Verification & disclosure pass (`--stage2`)

After the stage-1 merge runs, the optional stage-2 pass tightens the dataset for downstream count-regression / disclosure use cases. Two sub-steps, scoped to a sector if `--sector battery` (or solar/wind) is passed:

### (a) Relaxed Q fill

For rows that have **not met first-best** (column S is not a credible URL — i.e. still `fDi Markets (FT)` or empty), top up column Q (`Source for Project Status`) from the curated file when the master Q cell is empty or `fDi Markets (FT)`.

This **relaxes Rule 6 for column Q only**: stage 1 won't write into an empty cell, but here we will, because Q is the prerequisite for the disclosure note in (b). Other columns continue to honor Rule 6.

### (b) Disclosure note on S — and clear L

For rows where Q is now a credible URL **and** S is still `fDi Markets (FT)` or empty, set S to the literal:

```
Investment value not publicly disclosed
```

**Also clear column L (Capital Investment)** on the same row. Rationale: the original L value came from the fDi Markets export and was implicitly attributed to FT via `S = "fDi Markets (FT)"`. Once we disown the amount source via the disclosure note, L can no longer be credibly cited as that number, so we drop it to keep L and S consistent. The cleared L is reported in the change log.

The investment exists (Q is a real source for the project status) but the amount is unknown. Marking S this way distinguishes "we know this project exists, amount unknown" (count-regression eligible) from "we couldn't verify anything" (drop). Cells that already say `fDi Markets (FT)` are left alone: fDi capex estimates are kept (only the $39.9m placeholder is rejected), so this pass only fills an EMPTY S.

The validator (`validate_fdi_sources.py`) recognizes the disclosure literal as valid in column S only. The relaxed Q fill goes through the page check like any other URL; the disclosure note and the cleared L carry no URL and are written as they are.

### Two-curated-file workflow

When both China and manual lists apply (e.g. battery), invoke the skill twice with `--stage2` on each call. The relaxed Q fill is union-friendly (each pass tries its own curated file); the disclosure note pass is idempotent.

```bash
# Stage 1 + Stage 2 with manual list
python3 merge_fdi_sources.py --master FDI_All_ToSource.xlsx \
  --curated Globa_FDI_Battery_Manual.xlsx --stage2 --sector battery

# Stage 1 + Stage 2 with China list
python3 merge_fdi_sources.py --master FDI_All_ToSource.xlsx \
  --curated China_FDI_Battery.xlsx --sheet Battery --stage2 --sector battery
```

## Stage 3 (retired 2026-10-29)

Earlier versions of this file described a `--stage3` pass: cross-ID-class dedup with row drops and cell comments, a `Project Stage` column, a `\ ` cleanup and a re-sort. The script has no `--stage3`, the master's schema has no `Project Stage` column (the validator's R00 rejects one), and row drops, comments and re-sorts bypass `MasterEdit`. Dedup is now a proposal: the sourcing skill lists candidate pairs in its proposals file (`source-solar-wind-battery-fdi/references/reconciliation.md`) and the owner applies `drop_row` with a reason. The match key stage 3 used is still the right one for those proposals:

- `Parent company` normalized to lower-case alphanumerics, substring match either way (`Greatwall Motor` and `Great Wall Motor`; `GAC` and `GAC Aion`);
- `Destination Country` exact; `Year Announced` within one year; `Capital Investment (US$m)` within 5% (a missing side does not match);
- HAR against non-HAR, exact on all four: propose keeping the HAR row. Three of four: propose keeping both, with a note on the discrepancy;
- Manual against FDI in the same technology: propose keeping the row whose `Source (Amount)` is a real URL, and when one Manual row matches several FDI phase rows, all of them together.

## What this skill does NOT do

- **No web research.** It only moves URLs that already exist in the curated list. If both files lack an amount source for a project, the cell stays as `fDi Markets (FT)` (or empty). Web sourcing belongs to `/source-solar-wind-battery-fdi`.
- **No A–O reconciliation beyond column L.** The curated list's facts about parent / city / status / dates are not authoritative over master + SKILL source. Only L is reconciled, and only because Rule 4 ties it to S.
- **No new rows.** Only IDs already in `FDI_All_ToSource` are touched. Curated IDs absent from the master are reported but not added.
- **No de-dup.** Candidate pairs are proposals in `/source-solar-wind-battery-fdi`; the owner drops rows.
- **No direct writes.** Every cell goes through `MasterEdit`; a curated URL whose page does not state the value is held back, not merged.

## Reference implementation

`merge_fdi_sources.py` is a runnable reference. Invocation:

```bash
# Preview first: decisions, page verdicts, held-back cells, validator counts; nothing written
python3 merge_fdi_sources.py \
  --master /path/to/LCT-FDI/FDI_All_ToSource.xlsx \
  --curated /path/to/China_FDI_Battery.xlsx --sheet Battery \
  --dry-run [--limit 10]

# Then write, named in the change log
python3 merge_fdi_sources.py \
  --master /path/to/LCT-FDI/FDI_All_ToSource.xlsx \
  --curated /path/to/China_FDI_Battery.xlsx --sheet Battery \
  --who "Praveena" --batch merge_china_battery_2026-11

# Global manual list (FDI IDs): same flags, no --sheet
```

It auto-detects the layout, prints the change log and the held-back list to stdout, hands the edits to `MasterEdit` (backup, diff guard, page check, validator, `data_changes_log.csv`, `source_evidence.csv`), and reports any curated IDs missing from the master (a warning; it does not block the write). After it returns, run the sister validator:

```bash
python3 source-solar-wind-battery-fdi/validate_fdi_sources.py /path/to/FDI_All_ToSource.xlsx
```

## Done

- All Rule-3 candidates in the requested batch are replaced, or listed as held back with the page verdict.
- Column L reconciled where S was replaced and the curated row provided a number.
- If `--stage2` was set: relaxed Q-fill applied for non-first-best rows in scope, and disclosure note applied to S where Q is now credible.
- `MasterEdit` reported the write (or `--dry-run` reported what it would write) with 0 new validator errors; `data_changes_log.csv` and `source_evidence.csv` carry the batch.
- `validate_fdi_sources.py` exits 0 (recognizes `Investment value not publicly disclosed` in column S).
- Change log includes: rows updated, cells held back, rows skipped (curated lacks the source), curated IDs with no master match, and (if stage 2) per-row Q fills and S disclosure-note assignments.
