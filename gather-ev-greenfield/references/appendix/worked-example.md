# Worked example — LG Energy Solution Wrocław

End-to-end walkthrough of adding a single Tier-1 record. The goal is not the specific URLs (those evolve) but the *process* — what a Lab member does, in what order, and why. Read it once fully before your first batch.

The candidate: LG Energy Solution's battery cell plant in Wrocław, Poland. Europe's largest EV-battery cell facility in 2024. A useful training case because it has (a) a Korean parent with Korean-language primary sources, (b) a complex name history (LG Chem → LG Energy Solution), (c) multiple revised investment figures over time, and (d) rich independent coverage.

## Step 1 — Scope check

Before searching, confirm the candidate fits scope. Read the skill's "Do not use this skill for..." section. LG Wrocław is:

- Battery cell plant → `projectType: cell`, `sector: Batteries` ✓
- Not upstream mining or refining ✓
- Greenfield (built on former General Motors site but operationally new) ✓

Scope confirmed. Proceed.

## Step 2 — Seed the candidate

Open a blank record object. Fill in what you know from the initial prompt:

```
name: LG Energy Solution Wrocław
company: LG Energy Solution
country: POL
city: Wrocław
sector: Batteries
projectType: cell
```

Don't write anything else yet. You need evidence.

## Step 3 — Dedup check (critical)

Before any web search, run the dedup protocol from `references/dedup-protocol.md`.

1. **BNEF check.** Load `projects/nzipl/data/nzipl_bnef_projects.json`. BNEF is Mexico-only; Wrocław won't be there. Quick visual scan confirms: no match.
2. **FDI check.** Open `projects/nzipl/FDI_Combined.xlsx`. Search Battery rows with company `"LG"` and destination country Poland. This may return a row. If it does, capture the row number and tag the candidate `update-fdi`. If not, tag `new`.

For this walkthrough, assume FDI has a matching row (likely — LG Chem Wrocław is a famously large FDI event). Say it's row 147. Log:

```
sources.fdi_origin = "FDI_Combined.xlsx:row=147"
```

## Step 4 — Primary source hunt

Start at the company's own domain. Open `lgensol.com/en/press` and look for the original Wrocław announcement. The company spun off from LG Chem in December 2020, so:

- Pre-2020 → announcements live in LG Chem archives
- Post-2020 → LG Energy Solution's own IR page

You find an October 2017 LG Chem press release announcing 1.2 GWh capacity, $1.63B investment. Save the URL. This is one primary source.

Log to `aliases`: `["LGES Wroclaw", "LG Chem Wroclaw"]`. This catches the rename.

## Step 5 — Independent news source

Search Reuters for the 2017 announcement:

```
"LG Chem" Wroclaw battery factory 2017
```

Reuters piece from Oct 2017 confirms the announcement, quotes a named LG Chem executive, corroborates the investment figure. Save the URL. Two sources so far.

## Step 6 — Government / incentive filing

Poland publishes investment decisions via PAIH (Polish Investment and Trade Agency). Search:

```
site:paih.gov.pl "LG Chem" OR "LG Energy Solution" Wroclaw
```

You find a press release documenting Lower Silesia's regional economic development package and EU state-aid clearance. Save the URL. That's your third, independent, primary-ish source. **Three sources.**

Also useful: Lower Silesian Voivodeship's `umwd.dolnyslask.pl` for permit-level detail.

## Step 7 — Capacity and revised figures

The original 2017 figure was $1.63B. Current figures are much larger — capacity expanded through 2020, 2022, 2023 rounds. Find each revision:

- 2020 Reuters: expansion to 65 GWh, investment now $3.4B
- 2023 Electrive: expansion to 90 GWh, cumulative investment $5B

Build `investmentM_history`:

```json
"investmentM_history": [
  {"date": "2017-10-01", "valueM": 1630, "source": "https://www.lgchem.com/..."},
  {"date": "2020-06-01", "valueM": 3400, "source": "https://www.reuters.com/..."},
  {"date": "2023-01-01", "valueM": 5000, "source": "https://electrive.com/..."}
]
```

`investmentM` headline value: `5000` (most recent verifiable).

## Step 8 — Status and dates

From sources:
- `announced: "2017-10"` (source: LG Chem press release, month only)
- `prodStarted: "2018-Q1"` (source: Reuters; quarter-precision acceptable)
- `status: "Operating"` — *verify explicitly*. Find a 2024 piece on Electrive confirming active production. Without this, you'd have to downgrade to Tier 2 because the status × tier rule (`verification-protocol.md`) says Operating requires Tier 1.

## Step 9 — Coordinates

Wrocław facility is in the Kobierzyce industrial park. Get coordinates from:
- OpenStreetMap directly
- Wrocław city portal geodata
- Google Maps if the facility has a registered address

Lat/lng: `51.0843, 16.9253`. Source: city geoportal. (Within 5 km of Wrocław city center, passes the `checklist.md` test.)

## Step 10 — Jobs

Announced jobs target: 10,000 (multiple Reuters pieces, Invest Wrocław portal). Current: roughly 8,000 (Electrive 2024 report). Some uncertainty between sources — use the most recent verifiable figure.

## Step 11 — Assign tier

Count independent sources (excluding `fdi_origin` and `bnef_origin` — those are dedup receipts, not citations):

- LG Chem 2017 press release (primary)
- Reuters 2017 (independent news)
- PAIH Poland 2017 (government)
- Reuters 2020 (independent news, revision)
- Electrive 2023 (trade press, revision)
- Electrive 2024 (trade press, status)

Six independent URLs across `sources.*`. Well past the three-source Tier 1 minimum. Primary source present. Status "Operating" supported by 2024 coverage.

**Tier 1.** ✓

## Step 12 — Checklist run

Open `references/checklist.md` and walk every item. Critical ones to verify:

- [x] `id = EV-POL-0001` (first Poland record, zero-padded)
- [x] `region = "Europe"`
- [x] `postIRA = false` (announced 2017, pre-IRA)
- [x] `status = Operating` allowed at Tier 1
- [x] `productionUnits = "GWh/year"` because `targetProduction` is set
- [x] `license = "CC-BY-4.0"`
- [x] `verifiedBy = "A. Rojas"` (your name)
- [x] `verifiedDate = "2026-04-24"`
- [x] Three+ distinct citation URLs populated

## Step 13 — Red-flag sweep

Open `references/red-flags.md`. For Wrocław, all flags clear:

- Not MOU-only: actual operating plant with groundbreaking in 2017
- Not stale-announcement vaporware: news coverage spans 7+ years
- Not single-source PR-wire: multiple independent named-author pieces
- No shell-company obfuscation: LG Energy Solution is the direct operator
- Rename handled via `aliases`

## Step 14 — Write record

Append to `projects/nzipl/data/nzipl_ev_greenfield_global.json`. Use a tool that preserves readable indentation. Re-read the file after write to verify it parses.

## Step 15 — Update progress

Edit `tasks/ev-greenfield-poland-progress.json`:

```json
{
  "task": "EV Greenfield Poland",
  "total_target": 20,
  "candidates_found": 1,
  "tier1": 1,
  "tier2": 0,
  "tier3": 0,
  "dropped": 0,
  "dedup_new": 0,
  "dedup_update_fdi": 1,
  "next_candidate": "Stellantis-LGES Gliwice (investigating)",
  "last_updated": "2026-04-24",
  "last_operator": "A. Rojas",
  "batches": [
    {
      "date": "2026-04-24",
      "records_added": 1,
      "notes": "LG Energy Solution Wrocław. Matched FDI row 147. Tier 1. Used 2017 LG Chem PR, Reuters, PAIH, and 2023/2024 Electrive for revision history."
    }
  ]
}
```

## Step 16 — Log discoveries

Two findings worth a one-liner in `discoveries.md`:

```
- 2026-04-24 | A. Rojas | PAIH Poland publishes investment decisions with EU state-aid clearance detail; great Tier-A source for Polish projects [ev-greenfield]
- 2026-04-24 | A. Rojas | Korean company name history matters: LG Chem → LG Energy Solution spin-off Dec 2020; always include both in aliases [ev-greenfield]
```

If a fellow Lab member extends this to Samsung SDI or SK On, they'll know.

## What took time vs. what was mechanical

Read this next-steps summary critically: it's the part most new Lab members underestimate.

- **Mechanical (~20 min):** the schema fields, the dedup lookup, the checklist, the write.
- **Judgment-heavy (~40 min):** deciding the status based on 2024 evidence, reconciling the three investment figures into `investmentM_history`, confirming the rename chain, checking whether the FDI row is the same project or a related LG Chem facility.

Your first records will take 2+ hours each. By record 10 you'll be at 45 minutes. By record 20, 20-30 minutes each with a pair-review bottleneck.

## Where to stop

The record is done when the checklist passes. Don't keep searching for more sources — diminishing returns kick in at four or five citations. Move to the next candidate. Weekly re-verification (per `verification-protocol.md`) catches anything that changes.

## If this were Tier 2 instead

Same record, fewer sources: imagine only the 2017 LG Chem PR and one Reuters piece. Two sources, both at announcement time, no government filing.

- Cannot be Tier 1 (need three sources including a primary + corroborator + independent).
- Cannot be `Operating` at Tier 2 (status × tier rule).
- Must change status to `Planned` or `Announced`, and log tier 2.

Re-verify in 60 days — by then a government filing or trade-press groundbreaking piece often surfaces and you can upgrade.
