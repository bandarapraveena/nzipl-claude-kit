---
description: Enrich FDI project rows with source URLs by searching the web for confirming articles. Reads an xlsx file, finds rows missing sources, and fills citation columns via web research.
---

# FDI Source Enrichment

You are enriching an FDI (Foreign Direct Investment) dataset with per-row source URLs. The data originates from fDi Markets (Financial Times) and needs independent verification links.

## Input

The user will specify:
- **File path**: an `.xlsx` file with FDI project data
- **Batch size**: how many rows to process (default: 20)
- **Priority**: "largest" (by investment), "newest" (by year), or "sequential" (row order)

## Column Map

| Col | Header | What to source |
|-----|--------|---------------|
| A | Sector | (context only) |
| B | Project ID | (context only) |
| C | Parent company | Source in **P** |
| D | Company Country (HQ) | Source in **P** |
| E | Project Status | Source in **Q** |
| F | Destination Country | Source in **R** |
| G | Destination city | Source in **R** |
| H | Year Announced | Source in **U** (extract MM/DD/YYYY) |
| I | Year Completed | Source in **V** (extract MM/DD/YYYY) |
| K | Industry activity | Source in **W** |
| L | Capital Investment (US$m) | Source in **S** |
| M-O | Joint Venture fields | Source in **T** |

Target columns (P-W) should contain URLs to news articles, press releases, or official announcements that confirm the data point.

## Workflow

### 1. Read the file

```python
import openpyxl
wb = openpyxl.load_workbook(file_path)
ws = wb.active
```

Identify rows where columns P-W are all empty. Sort by the user's priority.

### 2. For each row in the batch

**Construct a search query** from the row data:
```
"{Parent company}" {Technology} {manufacturing OR plant OR factory} {City} {Country} {Year}
```

**Search the web** using the WebSearch tool. Look for:
- Company press releases
- Trade publication articles (PV Magazine, Windpower Monthly, Electrive, etc.)
- Reuters, Bloomberg, or local business press
- Government investment announcements

### 3. Evaluate results

For each search result, check which columns it confirms:
- Does the article name the company and its HQ country? -> P
- Does it confirm the project status (completed, announced, cancelled)? -> Q
- Does it name the specific city and country? -> R
- Does it state the investment amount? -> S
- Does it mention ownership shares or JV partners? -> T
- Does it give an announcement date? -> U (format as MM/DD/YYYY)
- Does it give a completion date? -> V (format as MM/DD/YYYY)
- Does it describe the industry activity (manufacturing, R&D, etc.)? -> W

**One article often covers multiple columns.** Write the same URL to all columns it confirms.

### 4. Handle gaps

If the initial search finds nothing:
- Try a broader query: just `"{Company}" {Country} {Technology}`
- Try the company's investor relations or press page directly
- If still nothing, write `fDi Markets (FT)` as the fallback source for all columns

If a search confirms some columns but not others:
- Do a targeted follow-up: e.g., `"{Company}" {City} investment $` for amount
- Leave unconfirmed columns empty for now (don't fabricate sources)

### 5. Write results

Write URLs back to the xlsx using openpyxl. Save after each batch.

**Never modify columns A-O.** Only write to P-W.

### 6. Log progress

After each batch, report:
- Rows processed: N
- Rows fully sourced (all P-W filled): N
- Rows partially sourced: N
- Rows with no results: N
- Next unsourced row number for the next batch

## Quality rules

- Every URL must be a real, resolvable link. Never fabricate or guess URLs.
- If an article is behind a paywall, the URL is still valid as a citation.
- Prefer primary sources (company press releases, government announcements) over secondary coverage.
- For dates in U and V: if the article gives only a year, write the URL and note "year only" in parentheses.
- Mark any uncertain attribution with `[UNVERIFIED]` prefix: `[UNVERIFIED] https://...`
- If the web search returns results about a different company or project with a similar name, do not use them.

## Example

Row: `Battery | FDI76190 | A123Systems | United States | Completed | China | Shanghai | 2009 | 2009 | Battery | Manufacturing | 20 | 1 | 1 | SAIC`

Search: `"A123Systems" battery manufacturing Shanghai China 2009`

Result article: Reuters piece confirming A123Systems opened a Shanghai plant in 2009 with SAIC as JV partner, $20M investment.

Write to row:
- P: `https://reuters.com/article/...` (confirms company + HQ)
- Q: `https://reuters.com/article/...` (confirms "completed")
- R: `https://reuters.com/article/...` (confirms Shanghai, China)
- S: `https://reuters.com/article/...` (confirms $20M)
- T: `https://reuters.com/article/...` (confirms SAIC JV)
- U: `https://reuters.com/article/...` (announcement date from article)
- V: `https://reuters.com/article/...` (completion date from article)
- W: `https://reuters.com/article/...` (confirms "Manufacturing")
