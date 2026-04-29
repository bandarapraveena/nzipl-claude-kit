---
name: gather-ev-greenfield
description: "Grow and maintain the Lab's global EV FDI dataset. Use when the user asks to gather, verify, audit, or extend EV greenfield manufacturing records — gigafactories, cell/pack/cathode/anode/separator/electrolyte plants, EV assembly, motor/inverter/charger/recycling facilities — anywhere in the world. Primary invocation is gap-filling: 'add N records', 'fill gaps', 'verify next 10 announcements'. Also handles single-record verification and stale-record audits. Scope excludes upstream mining and refining. Writes to projects/nzipl/data/nzipl_ev_greenfield_global.json, enforced by projects/nzipl/data/validate_ev_record.py."
---

# Gather EV FDI

Maintain a global, publicly-citable dataset of EV greenfield manufacturing investments. The skill is dataset-first: it reads what's already written, identifies gaps, and appends verified records. Cross-border (`origin ≠ country`) records are tagged `isFDI: true`; domestic investments are tagged `isFDI: false`. Both are in scope.

**Out of scope:** lithium/nickel/cobalt mining, refining, precursor chemistry, graphite processing.

## Primary invocation: gap-fill

> "Add 20 EV FDI records." "Fill the next 15 gaps." "Extend with recently-announced projects."

1. **Load state** — read `projects/nzipl/data/nzipl_ev_greenfield_global.json` and `projects/nzipl/data/ev_fdi_seed.json` (~150 canonical candidates).
2. **Pick gaps** — candidates in the seed list not yet in the global JSON, prioritized by `investmentM` and country coverage (avoid over-indexing on any single country unless the user asks). If seed is exhausted or user wants fresh projects, search trade press for the last 12 months.
3. **Verify** — for each candidate, gather sources per `references/verification-protocol.md`. Minimum 1 URL; Tier 1 needs 3 distinct non-receipt URLs.
4. **Write + validate** — append records to the global JSON. Run `python3 projects/nzipl/data/validate_ev_record.py <global.json>`. Exit non-zero = fix and re-run before reporting done.

## Secondary invocations

| Ask | Do |
|-----|----|
| "Verify this announcement" | Single-record: dedup, verify, write one record. |
| "Audit stale Tier 1 records" | Sample records with `verifiedDate < 90 days ago`; re-check sources; demote or update. |
| "Gather N records for <country>" | Country-scoped gap-fill: pick seed candidates with `country = <ISO-3>`, verify, write. |
| "Add the <Company> plant in <City>" | Start from that candidate; dedup against global; verify; write. |

## Workflow constraints

- **Never cite** `wikipedia.org`, `grokipedia.com`, `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com`, `medium.com`. The validator hard-rejects these.
- **Never dedup against** `FDI_Combined.xlsx`. That's the separate `/enrich-fdi` workstream. Dedup targets are (a) the global JSON itself and (b) `nzipl_bnef_projects.json` (Mexico snapshot from BloombergNEF).
- **Batch search queries.** One search per 3–5 candidates, not per candidate. Group by company or country.
- **Write lean.** Required fields only; leave optional fields empty when not confirmable. Partial-correct beats speculative-complete.
- **Run the validator after every batch.** Fix errors; don't write through them.

## File structure

```
.claude/skills/gather-ev-greenfield/
├── SKILL.md                                  ← You are here
└── references/
    ├── schema.md                             ← JSON schema + example
    ├── sources.md                            ← Tier A primaries + forbidden-domain list
    ├── verification-protocol.md              ← Tier matrix + status×tier rule
    ├── red-flags.md                          ← Vaporware / duplicate signals
    └── appendix/
        ├── search-playbook.md                ← Country-specific query templates (optional)
        ├── worked-example.md                 ← Training walkthrough
        └── common-mistakes.md                ← Append when you find a new recurring error

projects/nzipl/data/
├── nzipl_ev_greenfield_global.json           ← The dataset (array of records)
├── ev_fdi_seed.json                          ← ~150 canonical candidates (starting pool)
├── validate_ev_record.py                     ← Run before every write
└── nzipl_bnef_projects.json                  ← Mexico snapshot (dedup target, not citation source)
```

## Reading budget

Two files, ~15 minutes:
1. `references/schema.md` — fields, enums, example record
2. `references/verification-protocol.md` — tier matrix + status×tier rule

Everything else is referenced on demand.

## Defaults

| Decision | Default |
|----------|---------|
| Currency | USD millions, FX at announcement date |
| License | `CC-BY-4.0` per record |
| Paywalled sources | Allowed only with free mirror; cite the mirror |
| `isFDI` | Auto-derived: `origin ≠ country` |
| `region` | Auto-derived from `country` ISO-3 |
| `postIRA` | Auto-derived: `announced >= '2022-08-16'` |
| Status × tier | `Operating` / `Under Construction` / `Closed` → Tier 1 required; `Rumored` → Tier 3 required |
| Tier-1 min citations | 3 distinct non-receipt URLs |

## Related

- `/enrich-fdi` — separate workstream for the proprietary fDi Markets spreadsheet. Do not couple to it.
- `nzipl-design` — apply when rendering this dataset.

## Training-mode (optional)

Invoke when the user says "training" or `target_count ≤ 20`: use `tasks/ev-greenfield-TEMPLATE.md`, pair-review the first 5 records, log findings to `discoveries.md`. Production gap-fill skips all this.

## Done

- Target record count hit.
- `python3 projects/nzipl/data/validate_ev_record.py projects/nzipl/data/nzipl_ev_greenfield_global.json` exits 0.
- New records distributed across countries (not all one country) unless the user asked for a country-scoped batch.
