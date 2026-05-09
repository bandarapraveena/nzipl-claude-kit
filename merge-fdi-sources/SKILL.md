---
name: merge-fdi-sources
description: "Second-pass enrichment for FDI projects. Merges sources from a curated list into the master FDI_All_ToSource.xlsx. Auto-detects between two supported curated formats: a China_FDI_<Tech>.xlsx (Chinese-parent rows, matched by HAR ID) and a Globa_FDI_<Tech>_Manual.xlsx (non-HAR rows, matched by FDI ID). Use when the user asks to 'apply China sources', 'merge the manual battery list', or runs any post-SKILL sourcing round. Honors strict precedence: SKILL-found URLs in FDI_All_ToSource win over curated URLs (even when tagged [UNVERIFIED]); curated URLs only replace cells that say 'fDi Markets (FT)'. Reconciles Capital Investment (column L) to whichever source is ultimately cited in column S. Optional stage-2 pass (`--stage2`) tops up column Q for rows that didn't meet first-best, then marks any still-uncited Source (Amount) cells with 'Investment value not publicly disclosed' so they remain count-regression eligible. Optional stage-3 pass (`--stage3`) performs cross-ID-class dedup (HAR vs FDI vs Manual) and adds a Project Stage column that numbers same-company / same-city / close-year rows as phases of one project."
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

### (b) Disclosure note on S — and clear L

For rows where Q is now a credible URL **and** S is still `fDi Markets (FT)` or empty, set S to the literal:

```
Investment value not publicly disclosed
```

**Also clear column L (Capital Investment)** on the same row. Rationale: the original L value came from the fDi Markets export and was implicitly attributed to FT via `S = "fDi Markets (FT)"`. Once we disown the amount source via the disclosure note, L can no longer be credibly cited as that number, so we drop it to keep L and S consistent. The cleared L is reported in the change log.

The investment exists (Q is a real source for the project status) but the amount is unknown. Marking S this way distinguishes "we know this project exists, amount unknown" (count-regression eligible) from "we couldn't verify anything" (drop). Yellow highlight on both S and the cleared L.

The validator (`validate_fdi_sources.py`) recognizes the disclosure literal as valid in column S only.

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

## Stage 3 — Cross-source dedup & phasing pass (`--stage3`)

After stage-1 (and optionally stage-2), the stage-3 pass tightens the master against double-counting that survives the merge. It is run **after** any stage-1/2 sourcing pass, because it relies on column S being settled (a Manual row with a real S URL beats an FDI row whose S is still `fDi Markets (FT)`). Two sub-steps; both write a per-row change log.

### (a) Cross-ID-class dedup

Project IDs in `FDI_All_ToSource` come in three classes:

| Class | Example | Origin |
|-------|---------|--------|
| HAR    | `HAR0010`, `HARSOL128`, `HARW003`, `HAREV0050` | Curated China list (HAR-prefixed). Authoritative for Chinese-parent rows. |
| FDI    | `FDI237070`                                    | fDi Markets export. Broad coverage, lower per-row verification. |
| Manual | `Battery2.1`, `Solar88.1`, `New_DE_TR1`, `EV1` | Hand-entered rows added to the master before/after merges. |

The same project can appear under more than one class. Stage-3 detects and resolves these.

**Match key (normalized):**
- `Parent company` → lower-case alphanumeric, then substring match either direction (handles `Greatwall Motor` ↔ `Great Wall Motor`, `GAC` ↔ `GAC Aion`).
- `Destination Country` → exact normalized.
- `Year Announced` within ±1 year.
- `Capital Investment (US$m)` within 5% (treat one-side-missing as no-match for that criterion).

A pair is **exact (4/4)** when all four criteria match, **partial (3/4)** when company+country match plus either year or investment.

**Resolution rules (apply in order, scoped per technology so EV stays separate from Battery, etc.):**

1. **HAR vs non-HAR exact (4/4).** Drop the non-HAR row. Keep the HAR row. The HAR list is the curated authority; treat it as canonical when amount and year line up.
2. **HAR vs non-HAR partial (3/4).** Keep both. Attach a cell comment to the non-HAR `Project ID` cell pointing at the HAR counterpart and listing the discrepancy (e.g. `POTENTIAL DUPLICATE of HAREV0050. BYD Hungary 2023: HAR=$4500m vs non-HAR=$4200m`). Author this comment as `Dedup check`.
3. **HAR-with-`New_*` Manual partner.** When a HARW (or HARSOL / HAREV) row has a `New_<co>_<country>1`-style Manual sibling in the same company+country, drop the `New_*` row in favor of HAR. Confirm with the user before running this on borderline cases — `New_*` rows in *different* cities or with *different* amounts may be genuinely separate projects.
4. **Manual vs FDI duplicates within the same technology.**
   - If the Manual row has a credible `Source (Amount)` (a URL, not the empty-marker tokens or `fDi Markets (FT)`), **keep the Manual row, drop the FDI row(s)**. The Manual entry is the curated record; the FDI rows are the original-source phase splits.
   - If the Manual row's `Source (Amount)` is empty, `fDi Markets (FT)`, or a free-text note like `Investment value not publicly disclosed` (no URL), **drop the Manual row, keep the FDI row(s)**. Without a citation, the FDI export is the better-attributed entry.
   - When a single Manual row matches multiple FDI rows (common when fDi Markets split a project into expansion phases), all matching FDI rows are dropped together.
5. **Conflict resolution.** A cell can be implicated by more than one rule (e.g. `FDI198973` matches both a sourced Manual row *and* an unsourced Manual row). Rule 4-keep-Manual takes precedence: if any Manual partner has a credible source, the FDI row is dropped, regardless of what the unsourced Manual row would have triggered. The unsourced Manual row is then dropped under rule 4-drop-Manual on its own merits.
6. **Stale comments.** When stage-3 keeps a row but earlier stages had attached a "POTENTIAL DUPLICATE" comment to it, clear that comment after the partner row is dropped. The comment is no longer informative.

Stage-3 dedup writes the change log as a CSV next to the master:
- `duplicate_flags_manual_vs_fdi.csv` — Manual ↔ FDI pairs scored 3 or 4.
- `duplicate_flags_phases.csv` — phasing clusters from sub-step (b).

These CSVs are read-only artifacts for review; the script does not consume them.

### (b) Phasing column — `Project Stage`

Add a single new column `Project Stage` to sheet `All`, immediately to the right of the existing last column (typically becomes column **Y** when the master has 24 columns). Header style copies from the neighboring header; data-cell style copies from the neighboring data column. Set width to 14.

**Cluster rule.** Group rows by normalized `Parent company` + `Destination Country` + `Destination city` (all three required — rows with any of those three missing are not clustered). Within each group:

1. Sort rows by `Year Announced` (parse 4-digit substrings out of strings if the cell isn't already numeric — the master mixes int and string-typed years).
2. Walk the sorted list. Open a new chain at row 1; extend the current chain when the next row's year is within **5 years** of the previous row's year. A gap > 5 years closes the current chain and opens a new one.
3. Rows with no year join the single existing chain in their group if there is exactly one; otherwise they form their own chain.
4. Within each chain of length ≥ 2, write stage numbers `1, 2, 3, …` chronologically. Chains of length 1 leave the cell blank.

Stage numbers are an annotation, not a deduplication: phased rows stay in the file. Downstream count-regression code can decide whether to collapse chains.

### (c) Cell-level cleanup

Stage-3 also applies these passes (idempotent — safe to run repeatedly):

- Replace the literal token `\ ` (backslash-space) anywhere in string cells with the empty string, then strip surrounding whitespace. Empty strings become `None`. The `\` token is the China-list empty marker that some merges leave behind in city / source columns.
- Strip trailing whitespace from `Technology` values (the master has historically carried both `Wind` and `Wind ` — collapse to `Wind`).

### Sort after stage 3

After dedup deletions and the new column, **re-sort the sheet** with the existing key (`Technology` asc, then HAR-first, then `Capital Investment` desc) so rows stay in canonical order. Preserve all cell styles and comments through the rewrite — see the helpers used elsewhere in this kit (`snap_color`, `snap_font`, `snap_fill`, `snap_border`, `snap_alignment`, `snap_comment`, `restore_*`). Do **not** use `copy.deepcopy` on openpyxl style objects — it recurses through the style proxy and overflows.

### Highlights

- New `Project Stage` cells: no highlight (stage numbers are not source claims).
- Cells whose value changed via the `\ `-strip pass: no highlight (cleanup, not a source change).
- Rows dropped: gone from the file; logged to stdout and to the dedup CSV.

### Invocation

```bash
# Full pipeline (stage 1 + 2 + 3) on a curated battery list
python3 merge_fdi_sources.py --master FDI_All_ToSource.xlsx \
  --curated China_FDI_Battery.xlsx --sheet Battery \
  --stage2 --stage3 --sector battery

# Stage 3 only, after stages 1/2 already ran
python3 merge_fdi_sources.py --master FDI_All_ToSource.xlsx --stage3 --sector battery
```

When `--stage3` is invoked without a `--curated` flag, the stage-1/stage-2 passes are skipped and dedup runs against the existing master state alone.

### Two-curated-file workflow

When a sector has both a China list (HAR) and a manual list (FDI / non-HAR), run stage-1/stage-2 on each file separately, then run stage-3 **once** at the end. Running stage-3 between merges risks deleting a non-HAR row before its sourced Manual sibling has been imported, leaving the dataset thinner than intended.

### Manual review hooks

Stage-3 is the most opinionated of the three stages — the cross-ID-class rules can over- or under-delete on edge cases. Before saving, the script prints a confirmation prompt listing every dropped ID and the partner that beat it. In `--auto` mode the prompt is skipped; otherwise the user can paste a comma-separated **keep list** to veto specific drops. The kept rows stay; the comment from rule 2/6 is left in place so the override is auditable.

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
- If `--stage3` was set: cross-ID-class duplicates resolved per the rules above; `Project Stage` column written; `\ ` cleanup applied; sheet re-sorted; dedup CSVs emitted alongside the master.
- Yellow highlight applied to every changed cell (stage 1 + 2 only — stage 3 deletions are reported, not highlighted).
- `validate_fdi_sources.py` exits 0 (recognizes `Investment value not publicly disclosed` in column S).
- Change log includes: rows updated, rows skipped (curated lacks the source), curated IDs with no master match, (if stage 2) per-row Q fills and S disclosure-note assignments, and (if stage 3) per-row drops with partner ID and per-row stage assignments.
