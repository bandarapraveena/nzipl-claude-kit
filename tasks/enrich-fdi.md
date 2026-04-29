# Task: Enrich FDI Dataset with Source URLs

## What this task is

The `FDI_Combined.xlsx` dataset contains 698 clean energy FDI projects (Battery, Solar, Wind) originally sourced from fDi Markets (Financial Times). Columns A-O have project data. Columns P-W need per-row URLs to news articles or press releases that independently verify each data point.

This matters because fDi Markets is a proprietary database. For any published analysis, we need publicly citable sources rather than a database citation.

## How to run it

From a Claude Code session in the `nzipl-claude-kit/` directory (or any directory that inherits this kit's CLAUDE.md):

```
/source-solar-wind-battery-fdi
```

Claude will ask you for:
1. The file path (default: `../FDI_Combined.xlsx`)
2. Batch size (default: 20 rows)
3. Priority order (largest investments first is recommended)

Each batch takes 5-15 minutes depending on web search speed. Plan for 35+ batches to cover all 698 rows.

## What "done" looks like

Every row has at least one URL in columns P-W. Ideal: all 8 columns filled. Realistic: 5-6 columns filled for most rows, with some gaps for old or small projects where press coverage doesn't exist.

Rows with no web-findable sources get `fDi Markets (FT)` as fallback attribution.

## How to QA

After each batch:

1. **Run the validator.** `python3 source-solar-wind-battery-fdi/validate_fdi_sources.py FDI_Combined.xlsx`. Exits non-zero if any P–W cell contains a forbidden domain (Wikipedia, social, Medium) or a malformed value. Fix and re-run before marking the batch done.

2. **Spot-check 10% of URLs.** Open them in a browser. Confirm:
   - The URL resolves (not a 404)
   - The article names the **specific city** from column G (disambiguation requirement — see `source-solar-wind-battery-fdi/references/verification-protocol.md`)
   - The claimed data point (amount, date, location) actually appears in the article

3. **Check date formats.** Columns U and V should be MM/DD/YYYY. If the source only gives a year, the cell should contain the URL with "(year only)" appended.

4. **Verify A-O untouched.** Run a diff or checksum on the original columns to confirm no project data was modified.

5. **Review [UNVERIFIED] tags.** These indicate Claude found a plausible but not definitive match. Decide whether to accept, search further, or remove.

## Edge cases

| Situation | What to do |
|-----------|-----------|
| Project from 2007 with no web presence | Use `fDi Markets (FT)` as source for all columns |
| Article confirms some columns but not others | Fill confirmed columns, leave others for next pass |
| Multiple articles cover the same project | Use the most authoritative source (company PR > news > blog) |
| Cancelled or suspended projects | Search for cancellation announcements specifically |
| JV projects (M=1) | Look for JV announcement press releases; these often name partners and shares |
| Investment amount differs between sources | Use fDi Markets amount in column L; note discrepancy in S as `[AMOUNT DIFFERS] URL` |
| Company has been acquired or renamed | Search under both old and new names |

## Extending to other datasets

The `/source-solar-wind-battery-fdi` command works on any xlsx with the same column structure. To adapt for a different dataset:

1. Update the column map in the command if headers differ
2. Adjust the search query template for the domain (e.g., add sector-specific publication names)
3. The QA process remains the same

## Progress tracking

Live state is in `tasks/source-solar-wind-battery-fdi-progress.json`. After each session, update that file:
- Top-level counters: `rows_processed`, `rows_fully_sourced`, `rows_partially_sourced`, `rows_no_result`
- `next_unsourced_row` (so the next operator knows where to start)
- Append a new entry to the `batches` array

Note any patterns in `discoveries.md`.
