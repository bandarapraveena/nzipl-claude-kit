# NZIPL Design Tokens

Single source of truth for all visual values. Based on the CICE (Clean Industrial Capabilities Explorer) design system: Mantine v7, dark color scheme, green brand palette, Archivo typeface.

## Table of Contents
1. [Color System](#color-system)
2. [Typography](#typography)
3. [Spacing and Layout](#spacing-and-layout)
4. [Borders and Radii](#borders-and-radii)
5. [Shadows](#shadows)
6. [Breakpoints](#breakpoints)
7. [Google Fonts Link](#google-fonts-link)

---

## Color System

### Surface Colors (Mantine Dark Palette)

| Token | Hex | Mantine var | Usage |
|-------|-----|-------------|-------|
| `bg-body` | `#1A1B1E` | dark-7 | Page/slide background |
| `bg-card` | `#25262B` | dark-6 | Cards, paper, panels, navbar, toolbar |
| `bg-input` | `#141517` | dark-8 | Input fields, recessed surfaces |
| `bg-deep` | `#101113` | dark-9 | Deepest surface (footer, overlays) |
| `bg-elevated` | `#2C2E33` | dark-5 | Hover states on cards |

### Text Colors

| Token | Hex | Mantine var | Usage |
|-------|-----|-------------|-------|
| `text-primary` | `#EAEAEA` | custom | Headings, primary content |
| `text-body` | `#C1C2C5` | dark-0 | Body text, table values |
| `text-dimmed` | `#909296` | dark-2 | Subtitles, labels, axis text |
| `text-muted` | `#5C5F66` | dark-3 | Source notes, footnotes, disabled |

### Brand Green Scale

| Token | Hex | Usage |
|-------|-----|-------|
| `brand-0` | `#e8f5e8` | Lightest tint (highlight bg) |
| `brand-1` | `#d1ebd1` | Light background |
| `brand-2` | `#b8e0b8` | Disabled state fill |
| `brand-3` | `#9dd49d` | Secondary accent |
| `brand-4` | `#7fc77f` | Links, anchor text in dark mode |
| `brand-5` | `#56a360` | Primary brand accent |
| `brand-6` | `#4a8a52` | Filled buttons, active states |
| `brand-7` | `#3e7244` | Dark accent, pressed buttons |
| `brand-8` | `#325a36` | Filled button dark variant |
| `brand-9` | `#264228` | Darkest green |

### Functional Colors

| Token | Hex | Context |
|-------|-----|---------|
| `positive` | `#56a360` | RCA > 1, growth, advantage |
| `negative` | `#c94a4a` | RCA < 1, decline, deficit |
| `warning` | `#e89b3f` | Attention, data quality notes |
| `info` | `#5B8DB8` | Informational, reference lines |
| `border` | `#373A40` | dark-4, card borders, dividers |
| `border-subtle` | `#2C2E33` | dark-5, inner dividers |

### Chart Color Scales

#### Sequential (single-hue, for choropleths and heatmaps)
Green scale for positive metrics (RCA, relatedness density):
```
['#264228', '#325a36', '#3e7244', '#4a8a52', '#56a360', '#7fc77f', '#9dd49d']
```

#### Diverging (values above/below a threshold)
Red-to-green through neutral gray:
```
['#c94a4a', '#d4756f', '#dfa094', '#909296', '#7fc77f', '#56a360', '#3e7244']
```

#### Categorical (for multi-play or multi-country comparison)
| Index | Color | Hex |
|-------|-------|-----|
| 0 | Green (brand) | `#56a360` |
| 1 | Blue | `#5B8DB8` |
| 2 | Amber | `#e89b3f` |
| 3 | Red | `#c94a4a` |
| 4 | Purple | `#8b6cc1` |
| 5 | Pink | `#c96a8b` |

---

## Typography

### Font Stack

| Role | Family | Weight | Fallbacks |
|------|--------|--------|-----------|
| All text | Archivo | 400, 500, 600, 700 | -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif |
| Code/Data | JetBrains Mono | 400 | Consolas, monospace |

Archivo is used for both headings and body text. Headings are distinguished by weight (600-700) and size, not by a separate typeface.

### Type Scale

| Element | Size | Weight | Line-height | Color |
|---------|------|--------|-------------|-------|
| Page title (h1) | 2.5rem (40px) | 700 | 1.2 | `#EAEAEA` |
| Section heading (h2) | 2rem (32px) | 600 | 1.3 | `#EAEAEA` |
| Subsection (h3) | 1.5rem (24px) | 600 | 1.4 | `#EAEAEA` |
| h4 | 1.25rem (20px) | 600 | 1.4 | `#EAEAEA` |
| h5 | 1.125rem (18px) | 600 | 1.4 | `#EAEAEA` |
| h6 | 1rem (16px) | 600 | 1.4 | `#EAEAEA` |
| Body text (md) | 1rem (16px) | 400 | 1.55 | `#C1C2C5` |
| Small body (sm) | 0.875rem (14px) | 400 | 1.5 | `#C1C2C5` |
| Caption/label (xs) | 0.75rem (12px) | 500 | 1.5 | `#909296` |
| Button text | 0.875rem (14px) | 500 | 1 | varies |
| Chart axis tick | 0.75rem (12px) | 400 | 1 | `#909296` |

---

## Spacing and Layout

### Spacing Scale (Mantine)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 0.5rem (8px) | Icon gaps, tight inline spacing |
| `sm` | 0.75rem (12px) | Button padding, legend gaps |
| `md` | 1rem (16px) | Card padding, control gaps |
| `lg` | 1.5rem (24px) | Section padding, panel padding |
| `xl` | 2rem (32px) | Major section spacing |

### Container Widths

| Size | Max-width |
|------|-----------|
| xs | 540px |
| sm | 720px |
| md | 960px |
| lg | 1140px |
| xl | 1320px |

### Grid Patterns

Dashboard grid: `display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;`
Metric cards: `display: flex; gap: 1rem; flex-wrap: wrap;`
Toolbar: `display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;`

---

## Borders and Radii

### Border Radius (Mantine)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 0.25rem (4px) | Buttons, badges |
| `sm` | 0.375rem (6px) | Small cards, tooltips |
| `md` | 0.5rem (8px) | Cards, paper, panels (default) |
| `lg` | 0.75rem (12px) | Large containers |
| `xl` | 1rem (16px) | Hero sections |

Default for cards and paper: `md` (0.5rem).

### Border Styles

| Element | Border |
|---------|--------|
| Card/paper | 1px solid `#373A40` |
| Active element | 1px solid `#56a360` |
| Subtle divider | 1px solid `#2C2E33` |
| Section divider | 1px solid `#373A40` |

---

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `sm` | `0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25)` | Cards, paper (default) |
| `md` | `0 4px 6px rgba(0,0,0,0.3)` | Elevated elements |
| `tooltip` | `0 2px 8px rgba(0,0,0,0.5)` | Tooltips, popovers |

---

## Breakpoints

| Name | Width | Changes |
|------|-------|---------|
| xs | < 576px | Single column, stacked controls |
| sm | >= 576px | 540px container |
| md | >= 768px | Two-column grid, side-by-side charts |
| lg | >= 992px | Full toolbar, sidebar panels |
| xl | >= 1200px | 1140px container |
| xxl | >= 1400px | 1320px container |

---

## Google Fonts Link

Include this in every HTML deliverable's `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
```

For deliverables that also use code/data display:
```html
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```
