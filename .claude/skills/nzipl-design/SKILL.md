---
name: nzipl-design
description: "Apply the NZIPL/CICE design system to HTML deliverables (scrollytelling, dashboards, interactive maps), PPTX slide decks, and data visualizations. Based on the Clean Industrial Capabilities Explorer (cice.netzeropolicylab.com): Mantine v7 dark theme, Archivo font, green brand accent (#56a360), dark body background (#1A1B1E). Use whenever creating or formatting deliverables for NZIPL/JHU, or when the user mentions NZIPL style, CICE style, play cards, constraint maps, scrollytelling, or any visualization that should match the Lab's design system. Also trigger for 'like the play cards', 'in the Lab style', or 'CICE-style'. Covers D3.js and Chart.js chart styling, Leaflet map theming, PPTX slide layout, and the full token system."
---

# NZIPL Design System Skill

This skill applies the Net Zero Industrial Policy Lab visual identity to deliverables. The design system is derived from the CICE (Clean Industrial Capabilities Explorer) at cice.netzeropolicylab.com: Mantine v7 dark color scheme, Archivo typeface, green brand palette.

## When to use this skill

Apply this system to any deliverable produced for NZIPL or that the user wants styled in the Lab's visual language. The three primary output formats are:

1. **HTML scrollytelling** (play cards, constraint maps, briefing dashboards)
2. **HTML interactive maps** (Leaflet-based infrastructure/choropleth overlays)
3. **PPTX slide decks** (presentations, briefings, summaries)

## How to use this skill

### Step 1: Identify the output format

| User says | Format | Reference to read |
|-----------|--------|-------------------|
| "play card", "scrollytelling", "briefing page" | HTML scrollytelling | `references/html-patterns.md` |
| "dashboard", "interactive dashboard" | HTML dashboard | `references/html-patterns.md` |
| "map", "infrastructure map", "choropleth" | HTML Leaflet map | `references/html-patterns.md` |
| "deck", "slides", "presentation", "pptx" | PPTX | `references/pptx-styles.md` |
| "chart", "visualization", "graph" | Embedded viz | `references/chart-styles.md` |

### Step 2: Read the design tokens

**Always read `references/design-tokens.md` first.** It contains every color, font, spacing, and radius value. The tokens are the single source of truth.

### Step 3: Read the format-specific reference

Read the reference file(s) matching the output format. Most deliverables need both the format reference and the chart styles reference.

### Step 4: Apply the system

Follow the patterns in the reference files. Key principles:

**Dark background, light text.** Body background is `#1A1B1E` (Mantine dark-7). Cards and panels use `#25262B` (dark-6). Text is `#EAEAEA` for headings, `#C1C2C5` for body. Never use white or light backgrounds.

**Archivo for everything.** One typeface, differentiated by weight. Headings: 600-700. Body: 400. Labels and captions: 500. Load from Google Fonts in every HTML deliverable.

**Green brand accent.** Primary accent is `#56a360` (brand-5). Used for metric values, active states, progress bars, chart title colors, section markers. Lighter green (`#7fc77f`, brand-4) for links. Darker greens for pressed/hover states.

**Mantine-scale spacing and radii.** Cards use `border-radius: 0.5rem` (md). Spacing follows the Mantine scale: xs=0.5rem, sm=0.75rem, md=1rem, lg=1.5rem, xl=2rem.

**Cards have borders and shadows.** Every card/paper gets `border: 1px solid #373A40` and `box-shadow: 0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25)`.

**Attribution footer.** All deliverables include: "Net Zero Industrial Policy Lab | Johns Hopkins University | netzeropolicylab.com"

## File structure

```
nzipl-design/
├── SKILL.md              ← You are here
└── references/
    ├── design-tokens.md   ← Colors, typography, spacing, radii (Mantine dark + green brand)
    ├── html-patterns.md   ← Scrollytelling, dashboard, and map CSS/HTML patterns
    ├── chart-styles.md    ← D3.js and Chart.js styling (axes, tooltips, legends, color scales)
    └── pptx-styles.md     ← Slide layouts, font mapping, color constants for python-pptx
```
