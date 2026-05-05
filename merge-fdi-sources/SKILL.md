---
name: merge-fdi-sources
description: "Second-pass enrichment for FDI projects. Merges sources from a curated list into the master FDI_All_ToSource.xlsx. Auto-detects between two supported curated formats: a China_FDI_<Tech>.xlsx (Chinese-parent rows, matched by HAR ID) and a Globa_FDI_<Tech>_Manual.xlsx (non-HAR rows, matched by FDI ID). Use when the user asks to 'apply China sources', 'merge the manual battery list', or runs any post-SKILL sourcing round. Honors strict precedence: SKILL-found URLs in FDI_All_ToSource win over curated URLs (even when tagged [UNVERIFIED]); curated URLs only replace cells that say 'fDi Markets (FT)'. Reconciles Capital Investment (column L) to whichever source is ultimately cited in column S. Optional stage-2 pass (`--stage2`) tops up column Q for rows that didn't meet first-best, then marks any still-uncited Source (Amount) cells with 'Investment value not publicly disclosed' so they remain count-regression eligible."
---

# Merge FDI Sources

Second-round sourcing skill. The first round (`/source-solar-wind-battery-fdi`) populates source URLs by web research. This skill takes a separately curated list and merges its URLs into the master file (`FDI_All_ToSource.xlsx`) where — and only where — the SKILL pass had to fall back to `fDi Markets (FT)`.

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
4. **Column L (Capital Investment) follows the cited S source.** When S is replaced and the curated row carries a different L value, update L to the curated value and highlight it. If the curated row's L is empty (None / `\` / `NA`), leave the existing L untouched.
5. **Empty-marker tokens mean no-source-available.** Treat as if absent (`\` for the China list, `NA` for the manual list).
6. **Empty master cells are not Rule 3 candidates.** This skill does not invent sources where neither file has one.

## Highlight convention

Every cell this skill writes to (column L or any of P–W) gets a yellow `PatternFill` (`FFFFFF00`), matching the convention from `/source-solar-wind-battery-fdi`. This makes the second-round merge visually distinguishable in review.

## Workflow

1. **Identify the curated file** (China or manual). The script auto-detects from ID prefix; pass `--layout` to force.
2. **For China inputs, confirm the sheet name.** Defaults to the active sheet, but a China workbook can have multiple tech sheets — pass `--sheet Battery` (or Solar/Wind) to be explicit.
3. **Load both workbooks.** Master in editable mode; curated with `data_only=True`.
4. **Build ID maps.**
   - Master: `{ID: [row_numbers]}` from sheet `All` (handles duplicates that survived dedup).
   - Curated: `{ID: row_number}`.
5. **For each ID present in both files, classify each source column (P–W):**
   - If master cell ≠ `fDi Markets (FT)` → **keep** (Rule 2).
   - If master cell = `fDi Markets (FT)` and curated cell is a real URL → **replace + highlight**.
   - If master cell = `fDi Markets (FT)` and curated cell is empty → **skip**.
   - If master cell is empty/None → **skip** (Rule 6).
6. **Reconcile L.** If S was replaced and curated L is a real number, update master L and highlight. If curated L is empty, leave master L alone even if S changed.
7. **Save the master file.** Run `validate_fdi_sources.py` from the sister skill — must exit 0.
8. **Report a per-row change log** (ID, row number, columns replaced, L delta).

## Batch sizing

- Default: process **all matching rows in the curated list**. The work is mechanical and rule-based; there's no per-row research budget.
- If the user asks to start small ("first 10 rows"), iterate **in master-row order** (not curated-row order — reviewers read the master top-to-bottom) and stop after N.

## Stage 2 — Verification & disclosure pass (`--stage2`)

After the stage-1 merge runs, the optional stage-2 pass tightens the dataset for downstream count-regression / disclosure use cases. Two sub-steps, scoped to a sector if `--sector battery` (or solar/wind) is passed:

### (a) Relaxed Q fill

For rows that have **not met first-best** (column S is not a credible URL — i.e. still `fDi Markets (FT)` or empty), top up column Q (`Source for Project Status`) from the curated file when the master Q cell is empty or `fDi Markets (FT)`.

This **relaxes Rule 6 for column Q only**: stage 1 won't write into an empty cell, but here we will, because Q is the prerequisite for the disclosure note in (b). Other columns continue to honor Rule 6.

### (b) Disclosure note on S

For rows where Q is now a credible URL **and** S is still `fDi Markets (FT)` or empty, set S to the literal:

```
Investment value not publicly disclosed
```

Rationale: the investment exists (Q is a real source for the project status) but the amount was never disclosed. Marking S this way distinguishes "we know this project exists, amount unknown" (count-regression eligible) from "we couldn't verify anything" (drop). Yellow highlight as usual.

The validator (`validate_fdi_sources.py`) recognizes this literal as valid in column S only.

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

## What this skill does NOT do

- **No web research.** It only moves URLs that already exist in the curated list. If both files lack an amount source for a project, the cell stays as `fDi Markets (FT)` (or empty). Web sourcing belongs to `/source-solar-wind-battery-fdi`.
- **No A–O reconciliation beyond column L.** The curated list's facts about parent / city / status / dates are not authoritative over master + SKILL source. Only L is reconciled, and only because Rule 4 ties it to S.
- **No new rows.** Only IDs already in `FDI_All_ToSource` are touched. Curated IDs absent from the master are reported but not added.
- **No de-dup.** That's the responsibility of `/source-solar-wind-battery-fdi`.

## Reference implementation

`merge_fdi_sources.py` is a runnable reference. Invocation:

```bash
# China list (HAR IDs)
python3 merge_fdi_sources.py \
  --master /path/to/FDI_All_ToSource.xlsx \
  --curated /path/to/China_FDI_Battery.xlsx \
  --sheet Battery \
  [--limit 10]

# Global manual list (FDI IDs)
python3 merge_fdi_sources.py \
  --master /path/to/FDI_All_ToSource.xlsx \
  --curated /path/to/Globa_FDI_Battery_Manual.xlsx \
  [--limit 10]
```

It auto-detects the layout, prints the change log to stdout, writes the master in place, and reports any curated IDs missing from the master (warning only — does not block the save). After it returns, run the sister validator:

```bash
python3 source-solar-wind-battery-fdi/validate_fdi_sources.py /path/to/FDI_All_ToSource.xlsx
```

## Done

- All Rule-3 candidates in the requested batch are replaced.
- Column L reconciled where S was replaced and the curated row provided a number.
- If `--stage2` was set: relaxed Q-fill applied for non-first-best rows in scope, and disclosure note applied to S where Q is now credible.
- Yellow highlight applied to every changed cell.
- `validate_fdi_sources.py` exits 0 (recognizes `Investment value not publicly disclosed` in column S).
- Change log includes: rows updated, rows skipped (curated lacks the source), curated IDs with no master match, and (if stage 2) per-row Q fills and S disclosure-note assignments.
