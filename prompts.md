# Prompts

A starter set of prompts to try with Claude Code once the kit is cloned. Paste, run, read the output. If something surprises you, append one line to `discoveries.md`.

All prompts assume you've opened Claude Code inside the kit repo so `CLAUDE.md`, the glossary, gotchas, and skill definitions are loaded.

---

## After 5 minutes: see the kit in action

These confirm context is loaded. Every answer should cite a specific file, term, or workaround from the kit.

### 1. Sanity check the glossary

```
What does the Lab mean by "play"? Answer in one sentence, then list the three
play deliverables and who they are for.
```

Expected: a one-sentence definition, then a table or list referencing Play Cards, Constraint Maps, and Chart Packs. If Claude paraphrases from a general definition of "play" (theatrical, sports) without citing the Lab's meaning, context is not loading. Check you're running Claude Code from inside the repo.

### 2. Surface a gotcha before you hit it

```
I'm about to pull Mexico manufacturing employment from DataMexico's /data
endpoint. What should I know first?
```

Expected: a warning that `/data` drops sectors 31-33 (Manufacturing) silently, with the `/stats/rca` + multi-month parameter workaround. Cites `gotchas.md`.

### 3. Translate a data source spec

```
Summarize what the kit says about accessing OEC. Include the three headers,
the response wrapper quirk, and the cube names relevant to Mexico.
```

Expected: Authorization header, X-API-KEY header, token query param, browser User-Agent requirement, `result.get("data", result)` pattern, and the two Mexico cubes (`trade_i_baci_a_22` with id `namex`, and `trade_s_mex_y_hs6`).

### 4. Turn a concept into a methodology

```
Explain relatedness density to someone who knows RCA but not complexity theory.
Use the Lab's definition, not a textbook one. Then tell me which state has the
highest relatedness density for Auto Supplier Upgrading.
```

Expected: The kit's definition ("mean proximity of a play's target products to a location's existing exports, forward-looking complement to RCA"). Claude may need to read from the NZIPL project's data if the answer requires state rankings - flag if it does.

### 5. Find the right deliverable for a question

```
A policy colleague wants to know which bottlenecks need to be unlocked to
make Mexico competitive in grid hardware. Which Lab deliverable answers this,
and what is in the finance annex?
```

Expected: Constraint Maps. Finance annex covers cost of capital, instruments, feasibility.

---

## After an hour: run something real

These exercise existing commands and skills. You'll need the actual data files (some live in `projects/nzipl/data/` outside this kit).

### 6. Apply the design system

```
Take the attached HTML chart and apply /nzipl-design. Output the revised HTML
with Archivo font, the dark CICE background, and the green brand accent.
```

Expected: The `/nzipl-design` skill runs. Output uses `#1A1B1E` body, `#25262B` cards, `#56a360` accent, Archivo at 600-700 for headings. Check that chart axis colors match the token list in the skill's references.

### 7. Enrich a small FDI batch

```
/enrich-fdi --file=../LCT-FDI/FDI_All_ToSource.xlsx --rows=1-5
```

Expected: Five rows filled in source columns (P-W) with URLs to confirming articles. Mix of trade publications (PV Magazine, electrive), press releases, government announcements. Check `tasks/enrich-fdi-progress.json` for the batch status.

### 8. Ask the kit to self-review

```
Read gotchas.md and tell me which gotchas would bite me first if I were
starting a Brazil pipeline from scratch. Rank them by likelihood of hitting
them in the first week.
```

Expected: OEC User-Agent header (first HTTP request), Mexico BACI ID pattern applied to Brazil (`nabra`?), Response wrapper (every OEC call), BOM encoding (any government CSV). Useful test because it forces Claude to reason about applicability, not just recite.

### 9. Draft a discovery entry

```
I just found that DataMexico's industrial_parks cube uses accent-free full
state names like "Coahuila de Zaragoza" while energy-infrastructure.json uses
short forms like "Coahuila." Write this as a discoveries.md entry following
the kit schema.
```

Expected: A correctly formatted one-line entry matching the schema in `discoveries.md` (date, author, finding, tags). Paste the output and you've made your first contribution.

### 10. Generate a play card summary

```
Using the files in projects/nzipl/data/, write a 3-sentence summary of
Mexico's EV Components play: its rank, RCA, and the top 3 states by
relatedness density.
```

Expected: Rank 2, RCA 2.51, $42.0B exports. Top states: Nuevo Leon (0.577), Tamaulipas (0.474), Chihuahua (0.410). Cites `nzipl_mex_play_scores.json` and `nzipl_state_relatedness_density.json`.

---

## After a week: contribute back

These produce artifacts that go into the kit. Treat the output as a draft to review and commit.

### 11. Add a gotcha you hit

```
I just spent two hours on [describe the issue]. Draft a gotchas.md entry in
the same style as the DataMexico /data entry: what fails, why, the workaround.
```

Expected: Three-paragraph entry, last paragraph is the copy-paste workaround. Review, edit for tone, append to `gotchas.md`, PR.

### 12. Draft a new command

```
I run [describe a recurring task] manually every week. Read
.claude/commands/enrich-fdi.md as a template and draft a new command file
for this task. Include: inputs, workflow steps, QA checklist, output format.
```

Expected: A new markdown file following the enrich-fdi structure. Usually 60-70% right; the QA checklist needs the most editing. Save to `.claude/commands/<name>.md`, test once, PR.

### 13. Propose a glossary addition

```
The Lab uses "binding constraint" in the constraint maps work but it's not in
the glossary. Write a glossary entry in the same style as the existing internal
terms. Pull from how it's used in the Lab's documents, not textbook economics.
```

Expected: One-line entry. Review, add to `glossary.md` under Internal Terms, PR.

### 14. Spot inconsistencies

```
Read CLAUDE.md, glossary.md, and gotchas.md. Flag any place where they
contradict each other or use the same term differently.
```

Expected: A list of inconsistencies. Low signal if everything is aligned; when it returns hits, they're worth fixing.

### 15. Draft a cross-country prompt

```
Imagine we add Brazil data to the kit next month. Draft three prompts I could
put in prompts.md "After 5 minutes" that would confirm Brazil context loaded
correctly. Model them on prompts 1-3.
```

Expected: Three prompts that reference a Brazil-equivalent of each existing prompt (e.g., SIDRA instead of DataMexico, RAIS instead of DENUE). Useful for onboarding the second country.

---

## If a prompt does something unexpected

1. Read what Claude produced.
2. Was it wrong, or was the kit wrong? Often it's the kit - a stale reference, a missing term, a gotcha we haven't captured.
3. If it's the kit, append to `discoveries.md`.
4. If it's Claude misreading the kit, note which file and line confused it. That's also a discovery.
