# Verification protocol

This task adds citations to a row whose data already exists in columns A–O. The protocol below is the per-row evidence standard for those citations. Tier inflation is the most common failure.

## Per-cell evidence standard

Every URL written to P–W must satisfy all three:

1. **Tier A or Tier B domain** (see `sources.md`). Forbidden domains are validator-rejected.
2. **Disambiguates the facility.** Names the city / permit ID / groundbreaking date / JV brand from columns C–G — not just the company.
3. **Confirms the data point named in the column header** (HQ, status, city, amount, JV, dates, activity).
4. **Passes the page check.** `LCT-FDI/bin/source_check.py` finds the firm on the page, and the city, the amount (within 3% in USD, 5% after conversion) or the year for the location, amount and date columns. `MasterEdit` runs the same check and refuses a cell that fails, unless it carries `[UNVERIFIED] ` and a reason in `why=`. Run it on each candidate URL before composing the block.

A URL that satisfies (1) and (2) but doesn't confirm the specific data point goes in the column it *does* confirm. Don't smear one URL across columns it doesn't actually back up.

## Tier matrix (per row, not per cell)

A row's overall confidence is the strength of evidence behind its weakest cell.

| Tier | Required evidence | Min distinct citation URLs across P–W |
|------|-------------------|-----------------------------------------|
| 1 Confirmed | Primary (company PR / govt filing / SEC) + corroborator (permit / named-author trade) + independent news | 3 distinct URLs |
| 2 Likely | Company announcement + one top-tier independent, OR two independent named-author trade pieces | 2 distinct URLs |
| 3 Announced-only | Single source | 1 |

Syndication of one press release counts as **one source**, not three. A company PR + Reuters pickup + Electrive pickup = one piece of evidence. Use the most authoritative URL (company > Reuters > trade press).

## Status × tier (enforced by the workflow)

The status in column E sets the minimum row tier:

| Column E | Required row tier |
|----------|-------------------|
| `Operational` / `Completed` | 1 |
| `Under Construction` | 1 |
| `Cancelled` | 1 (a cancellation must be confirmed by an independent source, not just rumor) |
| `Announced` | 3 (any tier acceptable) |

If a row is marked `Completed` in column E but only one weak source can be found, leave column E unchanged and flag in the batch notes for follow-up. If a Tier A or strong Tier B source unambiguously contradicts column E (e.g. a 2025 announcement saying the project was cancelled), propose the status change in the proposals file per `reconciliation.md`; the owner applies it. Source > Excel, owner > skill.

## Disambiguation

Every URL must distinguish the specific facility — by city, permit ID, groundbreaking date, or assigned product line. Drop a citation when sources conflate sister plants. High-ambiguity operators:

- **Battery:** Ford+SK On (BlueOval cluster), GM+LGES (Ultium), Stellantis+Samsung SDI (StarPlus), BYD (dozens globally), CATL (25+ globally), Foxconn.
- **Solar.** First Solar (multi-state US footprint), JinkoSolar (multiple Chinese provinces + Florida + Vietnam), Trina Solar (China + Vietnam + Texas).
- **Wind.** Vestas (multiple European + US plants), Siemens Gamesa (offshore vs onshore vs blade plants), Goldwind (multiple Chinese sites).

If the article names the company but not the city, **do not** use it for column R. Either find a more specific article or leave R empty.

## Paywalls

Tier-1 citations allowed only if a free mirror exists. Cite the mirror URL. No mirror = source is invisible.

The fDi Markets database itself is paywalled and explicitly excluded as a citation — the entire purpose of this task is to *replace* fDi Markets with publicly citable sources. The string `fDi Markets (FT)` is the explicit fallback when no public Tier A / Tier B exists, and only after the search passes in `sources.md` have been exhausted.

## Conflicting sources

| Disagreement | Resolution |
|--------------|-----------|
| Two investment figures for column S | Propose L = the more authoritative figure (company > regulatory > government > trade press) in the proposals file, with the new S URL in the same `MasterEdit` block; note the older figure in the batch log. Until the owner applies it, S keeps a URL that states the current L, or `[UNVERIFIED] URL` with the reason. |
| Company says "Operational", independent says "delayed" | Cite the independent in Q with `[UNVERIFIED]` prefix; note in batch log. |
| Company says "Cancelled", independent says "Paused" | Trust company. |
| Different dates | Cite the most precise; if material gap, prefix `[UNVERIFIED]` and note. |
| fDi Markets row data (A–O) conflicts with public source | **Propose the change** in the proposals file; cite the source in the relevant P–W column once the owner has applied it. See `reconciliation.md` for per-column rules. |

Never silently average. Every A–O proposal is in the proposals file; every applied change is in `data_changes_log.csv`.

## Re-audit (secondary invocation)

When re-auditing rows already filled:

- Re-resolve every URL. 404 → replace with a Tier A/B alternative or fall back to `fDi Markets (FT)`.
- Forbidden-domain URL slipped through → replace immediately. Validator catches these.
- `[UNVERIFIED]` cells → re-search; promote (drop prefix) if confirmed, drop the citation if no better source surfaced.
- Log the audit in the progress JSON's `batches[]` with `kind: "audit"` and the row range.
