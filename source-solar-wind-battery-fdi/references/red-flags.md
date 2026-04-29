# Red flags

Signals that demote a candidate URL or cause the row to fall back to `fDi Markets (FT)`. Review before writing each citation.

## Evidence-quality flags

- **PR-wire-only.** Sources are only Business Wire / PR Newswire / GlobeNewswire / EIN Presswire with no independent pickup. → Require a Tier A or Tier B corroborator before citing. If none, fall back.
- **Three reproductions of one PR.** Company PR + Reuters pickup + Electrive pickup = one source with three URLs, not three independent sources. Pick the most authoritative URL; don't double-count.
- **"Industry sources" with company silence.** Named-author trade piece citing "sources familiar" + the company's own newsroom is silent. → Cite at most as Q (status) or W (activity) with `[UNVERIFIED]` prefix; do not cite as S (amount) or U/V (dates).
- **Satellite imagery without timestamp.** Can't distinguish 2022 from 2024 construction. → Optional strengthener only, never primary citation for U or V.
- **Local press conflicts with company filing.** Local paper says operating; company's 10-K says "expected to start 2026". → Trust the filing; cite the filing in Q. If column E disagrees with the filing, reconcile per `reconciliation.md` (update column E to match filing, yellow fill).

## Existence flags (apply when web search results are thin)

- **MOU-only.** "Signed an MOU", "intends to invest", no site, no permit, no update in 6+ months. → Acceptable only as Q (status) for `Announced` rows; not acceptable for S, R, U, V. If column E claims `Completed` based on this MOU only, reconcile column E down to `Announced` per `reconciliation.md`.
- **Stale announcement.** >18 months old, no construction / permit / hiring / equipment trail. → Acceptable as U (announcement date) only. If column E says `Completed` and stale evidence is the strongest available, fall back rather than reconcile (insufficient signal).
- **Politician announcement, no company confirmation.** Governor / minister announces Company X investing, company silent. → Cite at most as Q (status) with `[UNVERIFIED]` prefix; re-audit in 60 days.
- **Reverse announcement.** Local press claims investment; company's IR / 10-K mentions nothing. → Treat as rumor; skip as primary citation. Try the language-first search before falling back.
- **Shell-company SPV, no parent disclosure.** Operator is a local SPV, no parent named. → Don't use for P (parent + HQ); P requires the named parent. Acceptable for R if city is named.

## JV miscoding flags (recurring fDi data quality issues)

The fDi-source `Joint Venture Company` field is frequently mis-populated in ways that show up across many rows. Watch for and reconcile:

- **State / regional IPA listed as JV partner.** "Invest Kedah", "Hungarian Investment Promotion Agency", state econ-dev agencies, etc. are *not* JV partners — they're investment-attraction bodies. → Reconcile JV=0; clear partner name.
- **Customer / supply-agreement counterparty listed as JV partner.** A battery maker supplying modules to an OEM is a customer relationship, not a JV. (E.g. Toyota purchasing modules from LG Holland is not a JV.) → Verify with source whether the relationship is operating ownership; if just supply, JV=0.
- **Government investment fund / state aid listed as JV partner.** EU state-aid grants, sovereign-wealth-fund stakes (e.g. Morocco's CDG), DOE loans — these are financial backing, not JVs. Default JV=0 unless source explicitly describes a joint operating entity.
- **Long-established China JV missing partner.** When the parent column lists only the foreign partner of a well-known China JV, the Chinese partner is often missing. Verify and add. Common cases: SAIC Volkswagen, JAC-VW (Volkswagen Anhui), SK-EVE Yancheng, Ultium Cells (GM-LG), BlueOval SK (Ford-SK On).
- **JV brand listed as parent, partner missing.** Conversely, when the JV brand is in column C (e.g. "Ultium Cells", "StarPlus Energy", "BlueOval SK"), make sure both partners appear in column O.

## Post-bankruptcy / asset acquisition flag

When a parent goes bankrupt and another company acquires the site, the original-parent row is `Cancelled` even though the facility continues under new ownership. Examples encountered: Northvolt → Lyten (Heide, Gdansk, Skellefteå); Volvo+Northvolt → Volvo solo (Novo Energy Gothenburg, then shuttered).

→ **Action:** keep status `Cancelled` for the original-parent row; the new-parent operation is a separate row that this skill does not auto-create. Note the acquisition in the batch log so the dataset owner can decide whether to add a new row.

## Disambiguation flags

- **Generic "Company X expanding in Country Y".** No city, no permit, no groundbreaking date. → Not acceptable for R (must name the specific city). Acceptable only for P or W.
- **Sister-plant confusion.** Article describes a different plant of the same operator (e.g. Vestas Colorado vs Vestas Brighton; CATL Erfurt vs CATL Debrecen; First Solar Ohio vs First Solar Alabama). → Skip and re-search with the correct city in quotes.
- **JV branded multiple ways.** BlueOval SK = Ford + SK On; StarPlus = Stellantis + Samsung SDI; Ultium = GM + LGES. → Confirm the JV brand matches columns M–O before writing T.

## Sector-specific flags

### Battery / EV
- Cell repackaging vs cell manufacturing — pack-only assembly is a different scope from gigafactory cell production. Columns K (activity) wording matters; if the article describes pack assembly but column K says manufacturing, prefix `[UNVERIFIED]`.
- Phased expansion announced as new project — "BYD expands Hefei Phase 2 by 30 GWh" when Phase 1 already exists in the dataset. Do not write to T as a new JV.

### Solar
- Module assembly vs cell production vs wafer / ingot — these are different stages of the value chain. Verify K matches the article's described activity before citing W.
- Project capacity (MW of installed solar farm) vs manufacturing capacity (MW/year of module output) — easy to confuse. The dataset is FDI projects (manufacturing), not utility-scale installations. If the article describes a solar farm rather than a factory, do not cite — likely a different project type.

### Wind
- Tower / blade / nacelle / full turbine — separate manufacturing footprints. Vestas, Siemens Gamesa, GE often run dedicated blade plants distinct from nacelle assembly. Verify W against the article's described activity.
- Onshore vs offshore — different cost structures and geographies. Confirm the article's project matches the row's destination context.

## Cross-cutting: Chinese announcements

- Chinese-domestic media sometimes inflates or pre-announces. Require Tier A on the company's own site (catl.com, byd.com, gotion.com.cn, longi.com, jinkosolar.com, goldwind.com) in Chinese or English.
- Chinese-province government announcements sometimes precede official company commitment. → Cite at most as Q with `[UNVERIFIED]` until company confirms.
- Weibo / WeChat posts: forbidden domains regardless. Use only as lead generation.

## Process flags

- **Forbidden domain in search results.** Wikipedia, social, Medium dominate the top results. → Re-query with `site:` operator, language-first, or IPA portal (see `sources.md` "Search-tightening operators").
- **Date column without precise date.** Source gives only year for U or V. → Acceptable: write the URL with ` (year only)` appended.
- **No Tier A / Tier B after exhausted passes.** Company IR + Reuters + local-language + IPA portal all empty. → Write `fDi Markets (FT)`. Note in batch log which passes were attempted.
- **Currency not USD.** Article gives investment in EUR / CNY / KRW. → Cite the URL anyway; column L is already in USD per fDi Markets methodology, so the source corroborates the amount even if currency differs.

## When a red flag fires

1. Demote the citation (prefix `[UNVERIFIED]` or skip the column entirely).
2. Note the flag in the batch log if recurring.
3. If a new recurring pattern emerges, append a one-liner here so the next operator inherits the lesson.
