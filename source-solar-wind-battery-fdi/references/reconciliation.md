# Reconciliation

This task treats the **web source as the source of truth** and the Excel data (originally from fDi Markets) as a starting hypothesis. When they disagree, the cell is updated and highlighted yellow.

This is the inverse of the older fDi-Markets-as-ground-truth posture. If you find guidance elsewhere in this kit that says "trust the column data" or "do not modify A–O", treat it as superseded by this file.

## Highlight convention

Any A–O cell whose value was changed from the original gets a `PatternFill` with `start_color="FFFFFF00"` and `end_color="FFFFFF00"` (yellow). The fill stays on the cell permanently — it is the audit trail that distinguishes original fDi Markets data from reconciled values.

```python
from openpyxl.styles import PatternFill
YELLOW = PatternFill(start_color="FFFFFF00", end_color="FFFFFF00", fill_type="solid")
ws.cell(row=r, column=col_idx).fill = YELLOW
```

Do **not** highlight P–W cells; highlights are only for reconciled A–O values.

## Dedup pass (run once before sourcing)

Chinese-parent rows sometimes appear twice in the dataset — once with a `HAR####` Project ID (column B) and once with another ID (`Battery N.M`, `FDI######`, etc.). Drop the non-HAR duplicate.

**Match criterion** (all three must match):
- `Parent company` (column C) — case-insensitive, whitespace-trimmed
- `Destination city` (column G) — case-insensitive, whitespace-trimmed
- `Destination Country` (column F) — case-insensitive

**Filter:** only applies when `Company Country (HQ)` (column D) equals `China` (case-insensitive).

**Action:** delete the non-HAR row outright (do not just mark it). The HAR row is the kept canonical record.

If both candidate rows have HAR IDs, or neither does, dedup does **not** fire — leave both rows in place and note the unresolved pair in the batch log.

## Per-column reconciliation rules

Reconcile only when the source unambiguously contradicts the cell. Don't reconcile away precision (e.g., don't replace `Karawang` with `Indonesia`). When in doubt, leave the cell unchanged and prefix the relevant P–W URL with `[UNVERIFIED]`.

| Col | Field | Reconcile? | How |
|-----|-------|-----------|-----|
| A | Sector | No | Sector taxonomy is a Lab decision, not a source claim. |
| B | Project ID | No | fDi Markets / HAR ID is an identifier; do not change. |
| C | Parent company | Yes | If source uses canonical full name (e.g. `Contemporary Amperex Technology (CATL)` vs `CATL`), prefer the form used in source. Don't rewrite for spelling variants only. |
| D | Company Country (HQ) | Yes | If source HQ disagrees, update. (E.g. parent listed as a subsidiary in one country but HQ is elsewhere.) |
| E | Project Status | Yes | Most-current status from source wins: `Cancelled` > `Operational` / `Completed` > `Commenced` > `Announced`. If a 2025 article says cancelled and the cell says commenced, update to `Cancelled`. |
| F | Destination Country | Yes | Source disagrees → update. Rare. |
| G | Destination city | Yes | Source names a more specific city → update. Don't replace city with region. |
| H | Year Announced | Yes | Source has a precise announcement date and the year differs → update to source year. |
| I | Year Completed | Yes | Source confirms commissioning / production-start year and it differs → update. If source says "expected to start 2026" and column says 2024, update to 2026. |
| J | Technology | No | Lab taxonomy, not a source claim. |
| K | Industry activity | Yes | If source describes a different scope (e.g. `Pack assembly` vs `Cell manufacturing`), update. |
| L | Capital Investment (US$m) | **Yes — most common reconciliation target** | When the source reports a different USD figure, update column L to the source figure. See "Capital investment specifics" below. |
| M | Joint Venture (flag) | Yes | If source confirms a JV not in the cell, update flag to `1`. If source says it's a wholly-owned subsidiary and cell says JV=1, update to `0`. |
| N | Joint Venture Local | Yes | Mark `1` if source confirms a local (destination-country) partner. |
| O | Joint Venture Company | Yes | Update partner names to match source spelling and full list. |

## Capital investment specifics

Column L is the most common reconciliation target. When updating:

- **Use the source's USD figure** as-stated. If source uses local currency, convert at the announcement-date FX rate. Annotate the conversion in the batch log.
- **If multiple sources give different figures**, prefer in this order: company press release > regulatory filing > government / IPA announcement > named-author trade press > wire pickup. Pick the most recent figure when sources are otherwise tied.
- **If the project is multi-phase**, prefer the figure that matches the phase described in columns G/H/I. Do not replace a phase-specific figure with a total-project figure (or vice versa). If the cell currently has a total but the source describes phase 1, leave it and prefix the S column URL with `[UNVERIFIED]`.
- **Cell coloring** — apply yellow `PatternFill` to L when changed.
- **Always cite the source** in column S that justifies the new L value. The S URL is the audit trail for the L change.

## Common reconciliation patterns (lessons from R2–R91)

After ~90 rows of reconciliation work, these patterns recur frequently enough to look for proactively:

### Pattern A: Year Completed = fDi capex year, not commissioning year

The single most common reconciliation. The dataset's `Year Completed` is often the fDi-recorded capex / transaction-completion year, **not** the operational / production-start year. When sources unambiguously give a production-start year (or "production targeted YYYY"), reconcile column I to that year.

Examples encountered: R3 CATL Debrecen (2022→2026), R23 CALB Sines (2023→2027), R24 CATL+Stellantis Zaragoza (2024→2026), R28 CATL Arnstadt (2018→2022), R34 EVE Debrecen (2023→2026), R39 Samsung Seremban (2022→2024), R40 Gotion Kenitra (2024→2026), R41 Siro Gemlik (2021→2023), R42 AESC Navalmoral (2024→2026), R45 AESC Douai (2021→2025), R47 Hailiang Gresik (2023→2025), R48 SEMCORP Debrecen (2020→2025), R49 Gotion Göttingen (2021→2023), R58 AESC Sunderland (2021→2025), R62 EVE Phase 2 Kulim (2024→2027), R63 AESC Ibaraki (2021→2024), R66 VW Resende (2020→2021), R73 Hailiang Tangier (2024→2027), R74 Tenpower Selangor (2022→2025), R77 Sunwoda Nyíregyháza (2023→2025), R83 Tinci Houston (2023→2027), R84 Senior Tech Eskilstuna (2021→2025), R87 Pylontech Italy (2023→2025), R88 Samsung SDI Xi'an Phase 2 (2021→2023), R90 Hithium Mesquite (2024→2025).

**Heuristic:** if the dataset's Year Completed equals or is one year after Year Announced, suspect this pattern. Search press for actual production-start year.

### Pattern B: Capital Investment scope ambiguity

The dataset's L value may represent a different scope than the headline figure in press. Several sub-patterns:

- **One partner's share of a JV** rather than total project. R24 ($2.165B = CATL's ~50% of €4.1B JV with Stellantis), R36 ($1.4B = one party's half of $2.8B Volvo+Northvolt commitment), R81 ($250M = Ganfeng's half of $500M JV).
- **One phase of multi-phase project** rather than total. R40 Gotion Kenitra Phase 1 ($1.3B vs $6.5B over 5 phases), R83 Tinci Texas ($102.5M Texas-only vs $250M dataset-aggregate possibly including other Tinci US plans).
- **Manufacturing slice vs integrated value chain.** R5 Halmahera ($6B = full nickel-to-cell), R17 CATL Karawang ($3B for cell mfg vs $6B for whole Indonesia Battery Integration Project).
- **Original announcement vs de-scoped final.** R2 LG Indonesia ($9.8B original 2020 vs $7.7-8.5B at 2025 cancellation).

**Action:** if your search-confirmed figure differs from the dataset by 30%+, look for these scope explanations *before* reconciling. Sometimes the dataset is right at its scope and the press is right at a different scope. When unclear, prefix S with `[UNVERIFIED]` rather than reconciling.

### Pattern C: JV miscoding

Recurring miscodings encountered:

- **State / regional IPAs and economic-dev agencies are NOT JV partners.** Examples wrongly listed: Invest Kedah (R31 EVE Kulim — they're the Kedah state IPA), Hungarian Investment Promotion Agency variants. Reconcile JV=0, clear partner name.
- **Customer / supply relationships are NOT JV partners.** Examples wrongly inferred: Toyota in R16 LG Holland (Toyota is a module supply customer, not a JV partner). Leave JV=0.
- **Government investment funds taking a stake** (e.g. CDG Morocco at R40, EU state aid grants) are usually backers/investors, not JV partners. Default JV=0 unless source explicitly calls it a joint venture with operating responsibility.
- **Long-established JVs in China get marked JV=0** because the parent name in column C is the foreign partner alone. Verify and add the Chinese partner. Examples: R19 VW Anting (added SAIC), R20 SK Yancheng (added EVE Energy), R53 VW Hefei (added JAC Motors), R69 NEC Sunderland (added Nissan), R14 Ultium Spring Hill (added GM — was wrongly listed as LG-only).

### Pattern D: Destination city — region vs facility

The dataset sometimes lists a region/state instead of the actual facility city, or a major city instead of the suburb where the facility actually is. Examples: R32 Birmingham → Coventry (UK); R47 Morowali → Gresik (Indonesia — both nickel-region hubs, easy to confuse); R55 Kulim → Penang (Malaysia); R74 Kuala Lumpur → Selangor (Malaysia); R86 Kuala Lumpur → Kulim (Malaysia).

**Heuristic:** when sourcing Malaysian, Indonesian, or UK rows, double-check the city against the source's groundbreaking/MIDA/IPA notice.

### Pattern E: Post-bankruptcy asset acquisition (Northvolt/Lyten pattern)

When the original parent goes bankrupt and another company acquires the assets, the original project is `Cancelled` even though the site continues under new ownership. Examples: R8 Northvolt Heide (Lyten took over assets), R36 Volvo-Northvolt Novo Energy (shuttered), R91 Northvolt Gdansk (Lyten acquired).

**Action:** keep status `Cancelled` for the original-parent row; the acquirer's project is a new entry (not auto-created by this skill). Note the acquisition in the batch log.

### Pattern F: HQ country errors

Less common but real. R44 had Volkswagen listed as Sweden HQ (wrong — Wolfsburg, Germany). The dataset's `Company Country (HQ)` should be the parent's headquarters, not the location of an early JV partner.

## When NOT to reconcile

- Source value is older than cell value and cell value is plausible — leave the cell, cite the older source in P–W with `[UNVERIFIED]` only if needed for disambiguation.
- Source is a single Tier B article with no corroboration and the cell value matches multiple other Tier A/B sources — keep the cell.
- The disagreement is between project scope definitions (e.g., source describes the broader integrated project, cell describes the manufacturing slice) — keep the cell, document the scope difference in the batch log.
- Source is paywalled and no free mirror confirms the disagreement — keep the cell.
- The cell change would be cosmetic (whitespace, capitalization, "Inc" vs "Inc.") — leave it.

## Batch logging

For every reconciliation, record in the batch entry's `notes`:

```
R{row}: changed col {L} from {old_value} → {new_value} (source: {url})
R{row}: changed col {E} from {old_status} → {new_status} (source: {url})
```

This makes it possible to undo a reconciliation later if the source turns out to be wrong.

## Order of operations within a batch

1. Dedup pass (only on the first batch of a fresh xlsx).
2. Pick batch rows (same selection rules as before).
3. For each row: gather sources → write P–W URLs → reconcile A–O cells against source → apply yellow fill to changed cells.
4. Save xlsx.
5. Run validator (operates on P–W only, ignores A–O highlighting).
6. Update progress JSON.
