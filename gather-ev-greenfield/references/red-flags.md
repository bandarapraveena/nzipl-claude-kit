# Red flags

Signals that demote or drop a candidate. Review before writing each record.

## Existence flags

- **MOU-only** — "signed an MOU", "intends to invest", no site, no permit, no update in 6+ months. → Tier 3, status `Announced`. If 12+ months stale: mark `Cancelled`.
- **Stale announcement** — >18 months old, no construction / permit / hiring / equipment trail. → `Paused` or `Cancelled`; Tier 2 or 3.
- **PR-wire-only** — only sources are Business Wire / PR Newswire / GlobeNewswire. → Tier 3 max; require independent coverage.
- **Politician announcement, no company confirmation** — governor/minister announces Company X investing, company silent. → Tier 3 at most; re-verify in 60 days.
- **Shell-company SPV, no parent disclosure** — operator is a local SPV, no parent named. → Drop unless parent confirmed; `origin` requires the parent.
- **Reverse announcement** — announcement says Company X will build in Country Y; company's own IR / 10-K mentions nothing. → Treat as rumor. Tier 3 or drop.

## Scope flags

- **Upstream mining / refining** — lithium brine, nickel or cobalt mining, graphite processing, lithium carbonate/hydroxide refining, precursor chemistry. → Drop. Out of scope.
- **Brownfield mis-labeled as greenfield** — same site as existing plant, "Phase 2"/"expansion"/"capacity addition" language. → `countAsNew: false`, or update existing record's `investmentM_history`.
- **Cell repackaging only** — imports cells, assembles packs. Scope-valid, but `projectType: pack`, not `cell`. Capacity in `packs/year`.
- **Non-EV** — consumer electronics, grid-storage without EV OEM supply, military. → Drop.

## Duplicate flags

- **Rebrand/rename not caught by dedup** — CATL = 宁德时代 = Contemporary Amperex; BYD = 比亚迪 = FinDreams; Stellantis = PSA+FCA; SVOLT = spin-off from Great Wall Motor. → Check `aliases` of existing records; update rather than insert.
- **Phased expansion as new project** — "VW expands Salzgitter Phase 2 by 40 GWh" when Phase 1 is already recorded. → Update `investmentM_history` + `targetProduction` on existing record.
- **JV branded multiple ways** — BlueOval SK (Ford+SK On), StarPlus (Stellantis+Samsung SDI), Ultium (GM+LGES). → Record once under JV brand; put partner names in `aliases`.

## Evidence-quality flags

- **Three reproductions of one PR** — company PR + Reuters pickup + Electrive pickup = one source with three URLs. Fails Tier 1 "three independent sources" requirement.
- **"Industry sources" with company silence** — named-author trade piece citing "sources familiar" + company declined. → Tier 3 max; re-verify in 90 days.
- **Satellite imagery without timestamp** — can't distinguish 2022 from 2024 construction. → Optional strengthener only, never primary.
- **Local press conflicts with company filing** — local paper says operating; company's 10-K says "expected to start 2026". → Trust the filing; downgrade status.

## Process flags

- **Wrong status × tier** — validator catches. Fix tier or status.
- **Unsourced numeric claim** — `targetProduction: 50` but `sources.targetProduction` missing. → Source it or remove the field.
- **Currency not USD** — `investmentM` in ambiguous units. → Convert at announcement-date FX; annotate in `investmentM_history.original`.
- **Imprecise date with no annotation** — `announced: "2023"` when source has month. → Use most precise form the source supports.

## Cross-cutting: Chinese announcements

- Chinese-domestic media sometimes inflates or pre-announces. Require Tier A on the company's own site (catl.com, byd.com, gotion.com) in Chinese or English.
- Chinese-province government announcements sometimes precede official company commitment. → Tier 3 until company confirms.
- Weibo / WeChat posts without corroboration: aspirational only, Tier 3 max.

## When a red flag fires

1. Demote tier, reclassify status, or drop.
2. Log the flag in batch notes if using training-mode task file.
3. If a recurring new pattern, append to `appendix/common-mistakes.md`.
