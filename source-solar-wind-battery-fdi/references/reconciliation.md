# Reconciliation: what becomes a proposal

The web source outranks the Excel value, which came from fDi Markets and is a starting hypothesis. When they disagree, this skill **proposes** the change and the owner applies it. Nothing in columns A to O is written by this skill. If guidance elsewhere in the kit says to update a cell, or to apply a yellow fill, it is superseded by this file (2026-10-29).

## Proposals, not writes

Each batch has one proposals file, `LCT-FDI/outputs/proposals/<batch>.md`, in the format the owner reviews:

| Excel row | Project ID | Company | Field | Ours | What the source says | Proposed fix |
|---|---|---|---|---|---|---|

followed by a ready-to-run `MasterEdit` block per ten rows, with `why=` on every line. Mark a `DECISION` item wherever two readings are possible, give the options and a recommendation, and leave the choice. The owner says yes, possibly with changes; then the block runs. A proposal that changes an amount carries the new `Capital Investment (US$m)` and the new `Source (Amount)` in the same block, because `MasterEdit` checks the cited page against the amount as it will be after the edit.

Why this way: in the 2026-09 audit, 13 amounts had been overwritten from an article that carried a different figure (a funding round, a wind farm, an annual budget, a sister plant). The finder was also the judge. The proposals file gives the figure a second reader before it lands.

## Dedup pass (run once before sourcing)

Chinese-parent rows sometimes appear twice, once with a `HAR####` Project ID and once with another ID (`Battery N.M`, `FDI######`, ...). The HAR row is canonical.

**Match criterion** (all three): `Parent company` (fuzzy, see SKILL.md), `Destination city` (parentheticals stripped), `Destination Country`. **Filter:** `Company Country (HQ)` = China. **Action:** list the pair in the proposals file with the row to keep; the owner applies `drop_row` with the reason. If both rows have HAR IDs, or neither does, note the pair as unresolved.

## Per-column rules: what is proposable

Propose only when the source unambiguously contradicts the cell. Do not propose away precision (`Karawang` is better than `Indonesia`). When in doubt, leave the cell, and tag the relevant source cell `[UNVERIFIED] ` with the reason.

| Col | Field | Proposable? | How |
|-----|-------|-----------|-----|
| A | Sector | No | Lab taxonomy, not a source claim. |
| B | Project ID | No | An identifier. |
| C | Parent company | Yes | If the source uses the canonical full name (`Contemporary Amperex Technology (CATL)` vs `CATL`), prefer the source form. Not for spelling variants only. |
| D | Company Country (HQ) | Yes | The parent's headquarters, not an early JV partner's country (Volkswagen is Germany, not Sweden). |
| E | Project Status | Yes | Most current status wins: `Cancelled` > `Completed` / `Operational` > `Under Construction` > `Announced`. `Commenced` is retired (2026-10-01). A plant whose building is finished, even in trial production, is `Completed`. Built then closed: `Completed` + Operational `Ceased operations`. Built but halted: `Paused` with Year Completed. Cancelled before building: `Announced only`, Year Completed blank. Divestment with the plant still running: stays `Operational`. |
| F | Destination Country | Yes | Rare. |
| G | Destination city | Yes | A more specific city from the source. Never replace a city with a region. |
| H | Year Announced | Yes | The source gives a precise announcement date and the year differs. |
| I | Year Completed | Yes | The source confirms the commissioning or production-start year and it differs. "Expected to start 2026" against a cell of 2024: propose 2026. |
| J | Technology | No | Lab taxonomy. |
| K | Industry activity | Yes | The source describes a different scope (`Pack assembly` vs `Cell manufacturing`). |
| L | Capital Investment (US$m) | **Yes, the most common proposal** | See the owner's rules below. |
| M | Joint Venture (flag) | Yes | A JV the source confirms, or a wholly owned plant the cell calls a JV. |
| N | Joint Venture Local | Yes | A local (destination-country) partner the source confirms. |
| O | Joint Venture Company | Yes | Partner names as the source spells them, the full list. |

## The owner's rules for amounts (confirmed 2026-10-02)

- **Currency.** The column is US$m. A USD figure in the source is used as stated. Otherwise convert at the **FRED annual average for the year of the figure** (AEXUSEU, AEXCHUS, AEXKOUS, AEXINUS and the rest). For currencies FRED does not publish (IDR, VND, HUF, PLN, TRY, EGP, MAD and others) use **World Bank PA.NUS.FCRF** (official rate, period average) for that year. For a 2026 figure with no annual average yet, use the latest full year and say so in `why=`. Record the rate in `why=`. A EUR or CNY figure that equals the cell digit for digit is the signature of a currency error: propose the converted figure.
- **Joint ventures.** The amount is the foreign partners' share; all foreign partners count (Amplify: EVE 10% + Daimler 30% = 40%). All partners foreign: the total. A local partner contributes: the foreign share only. Split unknown: the full amount.
- **Government money.** Subtract it only when the source says the government pays a share of the stated total (Koura: DOE $100m of $406.58m, so $306.58m). State aid reported separately is not subtracted (Northvolt Heide, ProLogium).
- **Unsplittable figures.** A figure covering several plants or phases stays whole on one row, and the sibling rows carry `Investment value not publicly disclosed` (Stellantis Windsor C$3.6bn, Magna $790m, Honda $700m). When the source does split it, use this row's component (Graphite One Ohio $2bn, not the $5bn with the Alaska mine).
- **Scope.** If a confirmed figure differs from the cell by 30% or more, look for a scope explanation first (one partner's share, one phase, the manufacturing slice of an integrated project, an original announcement against a de-scoped final). The cell may be right at its scope and the press right at another. When unclear, tag `[UNVERIFIED]` instead of proposing.
- **fDi-origin rows** whose cited article states no figure: relabel the amount source `fDi Markets (FT)` and keep the estimate.
- **Authority order** when sources disagree: company press release > regulatory filing > government or IPA announcement > named-author trade press > wire pickup. Most recent wins a tie.

## Recurring patterns (from rows R2 to R91, April 2026, and the 2026-10 country checks)

### Pattern A: Year Completed is the fDi capex year, not the commissioning year

The single most common proposal. Examples: CATL Debrecen (2022 to 2026), CALB Sines (2023 to 2027), CATL Arnstadt (2018 to 2022), Samsung Seremban (2022 to 2024), Gotion Kenitra (2024 to 2026), AESC Sunderland (2021 to 2025), Hithium Mesquite (2024 to 2025). **Heuristic:** when Year Completed equals or is one year after Year Announced, search the press for the production-start year.

### Pattern B: the amount is a different scope

One partner's share of a JV (CATL Zaragoza $2.165B = half of the EUR 4.1B JV); one phase (Gotion Kenitra Phase 1 $1.3B of $6.5B over five phases); the manufacturing slice against the integrated chain (CATL Karawang $3B cells against $6B for the whole Indonesia Battery Integration Project); an original announcement against the de-scoped final (LG Indonesia $9.8B in 2020, $7.7 to 8.5B at the 2025 cancellation). Apply the owner's scope rule above.

### Pattern C: JV miscoding

State and regional IPAs are not JV partners (Invest Kedah at EVE Kulim). Customers are not JV partners (Toyota at LG Holland). Government funds and state aid are backers, not partners (CDG Morocco at Gotion Kenitra). Long-established China JVs get JV=0 because only the foreign partner is in column C: add the Chinese partner (SAIC at VW Anting, EVE at SK Yancheng, JAC at VW Hefei, GM at Ultium Spring Hill).

### Pattern D: region instead of facility city

Birmingham to Coventry; Morowali to Gresik; Kulim to Penang; Kuala Lumpur to Selangor. Check Malaysian, Indonesian and UK rows against the groundbreaking or IPA notice.

### Pattern E: post-bankruptcy acquisition

The original parent's row stays `Cancelled` even when the site continues under new ownership (Northvolt Heide and Gdansk to Lyten; Volvo-Northvolt Novo Energy shuttered). The acquirer's project is a new row, which this skill does not create; note it in the proposals file.

### Pattern F: HQ country

Rare but real: Volkswagen listed as Sweden. The HQ is the parent's, not an early partner's.

### Pattern G: a figure that is not capex (2026-10 checks)

A Series D round (StoreDot $80m), a supply contract (Alstom GBP 18m), an annual country budget (Gamesa Rs700 crore per year), a wind farm's cost on the turbine maker's row (Nordex R$1.3bn), an HQ office on a plant row (Vestas Portland), a government contract that financed a site (Orbia $8.4m DoD). A page that names the firm and a figure has not thereby stated the investment. Cite Source (Amount) only when the page ties the figure to this plant.

## When not to propose

- The source value is older than the cell value and the cell value is plausible.
- A single Tier B article against a cell that several Tier A/B sources support.
- The disagreement is one of scope definitions: keep the cell, note the scope in the batch log.
- The source is paywalled and no free mirror confirms the disagreement.
- The change is cosmetic (whitespace, capitalization, `Inc` against `Inc.`).

## Order of operations within a batch

1. Dedup pass (first batch of a fresh file only), pairs listed as proposals.
2. Pick the batch rows.
3. For each row: gather sources, run `source_check.py` on each candidate URL, then write the source cells through `MasterEdit`.
4. Write the proposals file for every A to O disagreement found.
5. Run `validate_master.py` and `validate_fdi_sources.py`.
6. Update the progress JSON and the quality flags document before the next batch.
