> **Note (2026-09-29):** the letters below describe the ORIGINAL 24-column layout. The LCT-FDI master now has 28 columns (Expansion after Capital Investment; Phase after Expansion; Joint Venture Local State after Joint Venture Local), so positions have shifted. Read and write columns **by header name**, through `LCT-FDI/bin/master_io.py`. No yellow highlighting.

# Schema

The xlsx has fixed columns A–W (logical labels; the master now has 28 columns, so write by header name). Columns A–O are project data from fDi Markets. This skill never writes them: a disagreement with a source becomes a proposal for the owner (see `reconciliation.md`). Columns P–W are citation URLs added by this task.

## Column map

| Col | Header | Type | Source target | Notes |
|-----|--------|------|---------------|-------|
| A | Sector | enum | — | One of `Battery`, `Solar`, `Wind`, `EV`. Drives which trade-press list applies (see `sources.md`). |
| B | Project ID | string | — | fDi Markets ID, e.g. `FDI76190`. |
| C | Parent company | string | **P** | Source must name the company. |
| D | Company Country (HQ) | string | **P** | Source must name HQ country. |
| E | Project Status | enum | **Q** | `Announced` / `Under Construction` / `Completed` / `Operational` / `Paused` / `Cancelled` / `Closed`. `Commenced` was retired 2026-10-01. |
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
- A resolvable URL (`https://...`), which `MasterEdit` reads before writing
- The literal string `fDi Markets (FT)` (fallback only — see SKILL.md)
- In S only, the literal string `Investment value not publicly disclosed` (the amount cell is then blank)
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
- **No fabricated URLs.** Every URL must resolve, and `MasterEdit` fetches every cited page before it writes: a page that does not name the firm, or does not state the amount, city or year it is cited for, is refused unless the cell is tagged `[UNVERIFIED] ` (see `LCT-FDI/DATA_EDITING.md`, *Source check*).
- **A–O cells are never written by this skill.** When a source contradicts a cell, the change goes into the batch's proposals file and the owner applies it through `MasterEdit`. See `reconciliation.md`.

## Example

Row 142: `Battery | FDI76190 | A123Systems | United States | Completed | China | Shanghai | 2009 | 2009 | Battery | Manufacturing | 20 | 1 | 1 | SAIC`

Acceptable filled state:

| P | Q | R | S | T | U | V | W |
|---|---|---|---|---|---|---|---|
| `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/...` | `https://reuters.com/... (year only)` | `https://reuters.com/... (year only)` | `https://reuters.com/...` |

If the only English-language hit is a Wikipedia page, and a Baidu search of `A123 上海 电池` plus a check of `a123systems.com` press archive both turn up nothing usable: write `fDi Markets (FT)` to all eight columns. **Do not** write the Wikipedia URL.
