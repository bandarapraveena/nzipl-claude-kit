# code-fdi-components

A Claude Code skill that codes the coarse `Technology` field of the Lab's FDI dataset
(`FDI_All_ToSource.xlsx` — Solar / Wind / Battery / EV) into two finer attributes per
project:

1. **Component** — the specific admissible component the plant makes (e.g. solar module,
   wind tower, Li-ion cell, EV vehicle assembly), with its HS6 code.
2. **Annual production capacity** — value + per-year unit, pulled from each row's source URLs.

It adds seven columns in place (`Component`, `Component HS6`, `Capacity Value`,
`Capacity Unit`, `Capacity Source`, `Coding Tier`, `Coding Notes`) and never touches the
original columns. A timestamped backup is written before every change.

This is an *enrichment* skill — it codes existing rows. It does **not** create rows
(that is `gather-ev-greenfield` / `gather-cleantech-greenfield`) and does **not** add
source URLs (that is `/enrich-fdi`).

## Quickstart

```bash
# from projects/nzipl/code-fdi-components/

# 0. once: back up the workbook + add the 7 coding columns
python3 data/fdi_coding.py init

# 1. code a batch of rows in a session (Claude reads each row's sources, classifies the
#    component, extracts the annual capacity) and write a batch JSON in the shape of
#    data/_sample_batch.json

# 2. validate + merge the batch by Project ID
python3 data/fdi_coding.py apply data/_sample_batch.json

# 3. validate the whole workbook + see coverage
python3 data/fdi_coding.py validate
```

`--xlsx PATH` overrides the default workbook (`../FDI_All_ToSource.xlsx`).

## What's here

| Path | Purpose |
|------|---------|
| `SKILL.md` | The skill: scope, the loop, the non-negotiable rules. Start here. |
| `references/component_taxonomy.json` | The admissible components per technology → HS6 + allowed capacity units. The spine. |
| `references/coding-protocol.md` | Step-by-step per-row procedure + capacity-unit cheat sheet + HS6 disambiguation rules. |
| `references/worked-examples.md` | 12 real codings (all 4 techs) with the lesson each teaches; the regression set. |
| `references/common-mistakes.md` | Pre-write checklist of recurring traps. |
| `data/fdi_coding.py` | `init` / `apply` / `validate` CLI. stdlib + openpyxl. |
| `data/_sample_batch.json` | Runnable 12-row example batch. |

## Requirements

Python 3.9+ and `openpyxl` (`pip install openpyxl`). No other dependencies.

## Notes baked into the taxonomy

- Two HS corrections from the source admissible-components image: solar inverter
  `854129 → 850440`, wind gearbox `870840 → 848340`.
- Battery materials all share the image key `850780` (which is really "other accumulators"),
  so components are classified by **text**, never by HS6. True customs codes are documented
  per component in the taxonomy for later standardization.
