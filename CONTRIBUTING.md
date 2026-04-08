# Contributing to the NZIPL Claude Kit

This kit is the team's shared knowledge layer for Claude Code. It gets smarter as people use it and contribute back.

## Quick contributions (no PR needed)

**Add a discovery.** When you find a data quirk, API behavior, or methodology insight that would save someone else time, append a line to `discoveries.md`:

```
- 2026-04-15 | Your Name | One-line description of what you found
```

Push directly to main. Keep it to one line. Include enough context that someone who hasn't seen the issue can understand it.

## Structured contributions (PR)

**Add a glossary term.** If you're using a term that isn't in `glossary.md` and a colleague might not know it, add it via PR. Follow the existing table format.

**Promote a discovery to gotchas.md.** If a discovery in `discoveries.md` is significant enough to be a permanent reference (it affects pipeline correctness or causes silent failures), write it up in `gotchas.md` with a heading, explanation, and workaround. Submit as PR.

**Update the design skill.** If you find a pattern that should be part of the design system (a new chart type, a component variant, a responsive pattern), submit a PR to the relevant file in `.claude/skills/nzipl-design/references/`.

**Update CLAUDE.md.** If the Lab's methodology, data sources, or deliverable structure changes, update the shared context via PR. Keep it factual and concise.

## What not to add

- Personal preferences or workflow habits (keep those in your own memory)
- Project-specific data or file paths (those belong in project-level CLAUDE.md files)
- Sensitive information (API keys, credentials, contract details)
- Speculative methodology changes (discuss first, document after decision)

## Review cadence

Gilberto reviews discoveries.md periodically and promotes significant entries to gotchas.md or glossary.md. If you think something should be promoted urgently, tag it in your discovery line:

```
- 2026-04-15 | Your Name | [URGENT] Pipeline breaks if you use single-month DENUE queries
```
