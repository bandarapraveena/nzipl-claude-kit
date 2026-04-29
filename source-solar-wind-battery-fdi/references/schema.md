# Schema

The xlsx has fixed columns A–W. Columns A–O are project data (originate from fDi Markets, **reconcilable against source** — see `reconciliation.md`). Columns P–W are citation URLs added by this task.

## Column map

| Col | Header | Type | Source target | Notes |
|-----|--------|------|---------------|-------|
| A | Sector | enum | — | One of `Battery`, `Solar`, `Wind`. Drives which trade-press list applies (see `sources.md`). |
| B | Project ID | string | — | fDi Markets ID, e.g. `FDI76190`. |
| C | Parent company | string | **P** | Source must name the company. |
| D | Company Country (HQ) | string | **P** | Source must name HQ country. |
| E | Project Status | enum | **Q** | `Announced` / `Under Construction` / `Operational` / `Completed` / `Cancelled`. |
| F | Destination Country | string | **R** | Must appear in source. |
| G | Destination city | string | **R** | Must appear in source — disambiguation requirement. |
| H | Year Announced | int (year) | **U** | Cite article that gives announcement date; format MM/DD/YYYY in U. |
| I | Year Completed | int (year) | **V** | Cite article confirming commissioning / opening; MM/DD/YYYY in V. |
| J | (reserved) | — | — | Skip. |
| K | Industry activity | string | **W** | E.g. `Manufacturing`, `R&D`, `Assembly`. |
| L | Capital Investment (US$m) | number | **S** | Source must state amount in USD or convertible currency. |
| M–O | Joint Venture fields (partner names, ownership %) | string / number | **T** | One URL covering the JV structure suffices. |
| P | Source: Company + HQ | URL | written | |
| Q | Source: Status | URL | written | |
| R | Source: Destination city + country | URL | written | |
| S | Source: Investment amount | URL | written | |
| T | Source: JV / ownership | URL | written | |
| U | Source: Announcement date (MM/DD/YYYY) | URL or URL+annotation | written | |
| V | Source: Completion date (MM/DD/YYYY) | URL or URL+annotation | written | |
| W | Source: Industry activity | URL | written | |

## Cell value formats

**P, Q, R, S, T, W** — exactly one of:
- A resolvable URL (`https://...`)
- The literal string `fDi Markets (FT)` (fallback only — see SKILL.md)
- The empty string (preferred over a forbidden-domain citation)

**U, V (date columns)** — exactly one of:
- A URL
- A URL followed by ` (year only)` if the article gives no day/month
- A URL followed by ` MM/DD/YYYY` if the precise date is needed alongside the citation
- `fDi Markets (FT)`
- Empty

**Uncertainty marker.** Any cell may be prefixed with `[UNVERIFIED] ` if the attribution is plausible but the article doesn't unambiguously confirm the data point. Validator does not reject these but they should be re-audited.

## Hard constraints

- **One URL per cell.** If multiple articles confirm the same data point, pick the most authoritative (Tier A > Tier B). Do not concatenate URLs.
- **The same URL may appear across multiple columns** — a single comprehensive article often confirms P, Q, R, S simultaneously. Write it to all columns it confirms.
- **No forbidden domains.** Validator rejects: `wikipedia.org`, `grokipedia.com`, `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com`, `medium.com`.
- **No fabricated URLs.** Every URL must resolve. Do not guess plausible-looking paths.
- **A–O cells are reconcilable** — when source contradicts a cell, update the cell to match the source and apply yellow `PatternFill` (`FFFFFF00`). Source > Excel. See `reconciliation.md` for per-column rules.

## Highlight convention

Yellow fill (`FFFFFF00`) on any A–O cell = "reconciled from source; differs from the original fDi Markets value." Cells without fill are unchanged. P–W cells are never highlighted regardless of state.

```python
from openpyxl.styles import PatternFill
YELLOW = PatternFill(start_color="FFFFFF00", end_color="FFFFFF00", fill_type="solid")
ws.cell(row=r, column=col_idx).fill = YELLOW
```

## Example

Row 142: `Battery | FDI76190 | A123Systems | United States | Completed | China | Shanghai | 2009 | 2009 | Battery | Manufacturing | 20 | 1 | 1 | SAIC`

Acceptable filled state:

| P | Q | R | S | T | U | V | W |
|---|---|---|---|---|---|---|---|
| `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/... (year only)` | `https://reuters.com/... (year only)` | `https://reuters.com/...` |

If the only English-language hit is a Wikipedia page, and a Baidu search of `A123 上海 电池` plus a check of `a123systems.com` press archive both turn up nothing usable: write `fDi Markets (FT)` to all eight columns. **Do not** write the Wikipedia URL.
