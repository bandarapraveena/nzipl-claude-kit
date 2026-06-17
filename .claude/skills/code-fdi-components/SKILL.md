---
name: code-fdi-components
description: "Code the coarse TECHNOLOGY field of the Lab's FDI dataset (FDI_All_ToSource.xlsx — Solar / Wind / Battery / EV) into two finer attributes per project: (1) the specific admissible COMPONENT the plant makes (solar module/cell/inverter/mounting; wind turbine/nacelle/blade/tower/gearbox; battery cell/cathode/anode/separator/electrolyte/current-collector; EV vehicle/e-motor/inverter/e-axle/charger) with its HS6, and (2) the component's ANNUAL PRODUCTION CAPACITY (value + unit) pulled from each row's source URLs. Use when the user asks to code, classify, enrich, or add component / subcomponent / production-capacity columns to the FDI dataset, or to 'add the technology subcomponent'. Adds 7 columns in place via data/fdi_coding.py. Out of scope: building new FDI records from scratch (use gather-ev-greenfield / gather-cleantech-greenfield) and adding source URLs (that is /enrich-fdi)."
---

# Code FDI Components

The FDI dataset (`FDI_All_ToSource.xlsx`, 794 rows) tags every project with a coarse
`Technology` — Solar, Wind, Battery, or EV. This skill adds depth: for each row it
codes **which specific component** the plant makes (from a fixed admissible shortlist)
and **how much of that component it can produce per year**, reading the source URLs
already in the row plus targeted search. It is a *coding/enrichment* skill — it
enriches existing rows, it does not create them.

**Relationship to sibling workstreams (do not confuse):**
- `gather-ev-greenfield` / `gather-cleantech-greenfield` — build *new* records from scratch into JSON datasets. This skill never creates rows.
- `/enrich-fdi` — adds *source URLs* (columns P–W) to the same workbook. This skill consumes those URLs; it does not add them.

## What it writes

Seven columns appended **in place** to `FDI_All_ToSource.xlsx` (original columns untouched; a timestamped backup is written before every change):

| Column | Meaning |
|--------|---------|
| `Component` | The admissible component (canonical name from the taxonomy) or `Other / out-of-shortlist`. |
| `Component HS6` | Best single HS-2022 customs code for that component (6-digit string). |
| `Capacity Value` | Annual production capacity, numeric. Blank when not findable. |
| `Capacity Unit` | Per-year unit (`GWh/year`, `GW/year`, `tonnes/year`, `vehicles/year`, `towers/year`, …). |
| `Capacity Source` | URL the capacity figure came from. |
| `Coding Tier` | `1` component+capacity both sourced · `2` component clear, capacity inferred/single-source · `3` component uncertain or capacity absent. |
| `Coding Notes` | Multi-component flag, out-of-shortlist reason, ramp stage, re-tag suggestion. |

## The loop

```bash
# 0. ONCE — back up the workbook and add the 7 columns (idempotent):
python3 data/fdi_coding.py init

# 1. Code a batch of rows (you do the judgment — see below), writing a batch JSON.
# 2. Validate + merge the batch into the workbook by Project ID:
python3 data/fdi_coding.py apply path/to/batch.json
#    (refuses to write if any row fails validation; backs up first)

# 3. Validate the whole workbook + see coverage:
python3 data/fdi_coding.py validate
```

`data/_sample_batch.json` is a runnable 12-row example covering all four technologies and every hard case.

## Coding a row (summary — full procedure in `references/coding-protocol.md`)

1. **Read the row's source URLs** (the `Source (...)` columns). The company PR and the trade-press article usually carry the component and the capacity. Search only if they don't.
2. **Classify the COMPONENT from text, never from an HS6 code.** Match the plant's product to the admissible shortlist for its `Technology` in `references/component_taxonomy.json`. If nothing fits, use `Other / out-of-shortlist` and say what it actually makes in `Coding Notes`.
3. **Extract ANNUAL capacity** of that component — value + per-year unit. Use the component's typical unit (cells → GWh/year, modules → GW/year, materials → tonnes/year, towers → towers/year, vehicles → vehicles/year). If only a phased or full-ramp figure exists, record it and note which.
4. **Tier it** (1/2/3) and write `Coding Notes`.
5. Add the row to the batch JSON.

## Non-negotiable rules

- **`Capital Investment (US$m)` is NOT capacity.** The single most common error. No annual capacity figure → leave `Capacity Value` blank, tier 3. Never back-convert dollars or "supports N vehicles" into capacity.
- **Classify by text, not HS6.** The image shortlist assigns `850780` to six different battery materials and `850780` is really "other accumulators" — a code can never tell cathode from anode. Read the project description.
- **Integrated complexes are multi-component.** Code the primary component the row's *actor* builds, set the multi-component note, and never attach another company's or another site's capacity to the row.
- **GW (power) ≠ GWh (energy).** Solar/wind components are GW/MW; battery cells are GWh. A `GWh` figure on a Solar or EV row almost always means a misfiled battery plant — flag it for re-tag in `Coding Notes`.
- **Capacity is always per-year**, nameplate throughput of the component. Never cumulative, never installed base, never the whole multi-model plant total when only part is the coded component.
- **Two HS corrections from the source image are baked into the taxonomy:** solar inverter `854129 → 850440`; wind gearbox `870840 → 848340`. The validator accepts the corrected customs code or the image's shortlist key.
- **Forbidden capacity-source domains:** wikipedia, grokipedia, linkedin, reddit, twitter/x, facebook, instagram, medium. The validator hard-rejects these.
- **Always go through `fdi_coding.py`** (it backs up and validates). Never hand-edit the workbook's coding cells.

## File structure

```
code-fdi-components/
├── SKILL.md                              ← You are here
├── README.md                             ← Quickstart
├── data/
│   ├── fdi_coding.py                     ← init / apply / validate CLI (stdlib + openpyxl)
│   └── _sample_batch.json                ← Runnable 12-row worked batch (all 4 techs)
└── references/
    ├── component_taxonomy.json           ← THE taxonomy: per-tech components → HS6 + units. Read this.
    ├── coding-protocol.md                ← Step-by-step per-row procedure + capacity-unit cheat sheet
    ├── worked-examples.md                ← The 12 grounded codings with the lesson each teaches
    └── common-mistakes.md                ← Recurring traps as a pre-write checklist

Target workbook: projects/nzipl/FDI_All_ToSource.xlsx   (default --xlsx)
Backups:         projects/nzipl/backups/FDI_All_ToSource.<timestamp>.xlsx
```

## Reading budget

Two files, ~10 minutes:
1. `references/component_taxonomy.json` — the admissible components, HS6, and allowed units per technology.
2. `references/coding-protocol.md` — how to pick the component and the capacity unit, and the disambiguation rules.

`worked-examples.md` and `common-mistakes.md` are referenced on demand.

## Defaults

| Decision | Default |
|----------|---------|
| Workbook | `projects/nzipl/FDI_All_ToSource.xlsx` (override with `--xlsx`) |
| Backup | Automatic, timestamped, into `backups/`, before every `init`/`apply` |
| `Component HS6` | Corrected HS-2022 customs code; the image shortlist key is also accepted |
| Capacity period | Per-year only |
| Scope | Manufacturing rows get a real component; R&D / Logistics / Design rows → `Other / out-of-shortlist`, note the activity |
| Out-of-shortlist | `Component = "Other / out-of-shortlist"`, `in_shortlist`-style reason in `Coding Notes`; capacity still recorded if disclosed |
| Batch size | 15–25 rows per pass; prioritize by `Capital Investment` and technology coverage |

## Done

- `python3 data/fdi_coding.py validate` exits 0 (warnings are advisory; violations are not).
- Coded rows distributed across technologies, not all one tech, unless the user scoped a single tech.
- Every Tier-1 row has a `Capacity Value`, `Capacity Unit`, and `Capacity Source`.
- Out-of-shortlist and multi-component rows carry an explanatory `Coding Notes`.
- GWh-on-Solar/EV-row re-tag flags surfaced (or resolved) rather than ignored.
