# NZIPL HTML Patterns

CSS and HTML patterns for scrollytelling, dashboards, and Leaflet maps. Based on the CICE design system: Mantine dark theme, Archivo font, green brand accent (#56a360).

## Table of Contents
1. [Shared HTML Boilerplate](#shared-html-boilerplate)
2. [Scrollytelling Play Cards](#scrollytelling-play-cards)
3. [Interactive Dashboards](#interactive-dashboards)
4. [Leaflet Maps](#leaflet-maps)
5. [Common Components](#common-components)

---

## Shared HTML Boilerplate

Every NZIPL HTML deliverable starts with this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[Title] — NZIPL</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
<!-- Additional CDN links (D3, Leaflet, Chart.js, etc.) go here -->
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Archivo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #1A1B1E;
  color: #C1C2C5;
  line-height: 1.55;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'Archivo', sans-serif;
  font-weight: 600;
  color: #EAEAEA;
}
a { color: #7fc77f; text-decoration: none; }
a:hover { color: #9dd49d; }
</style>
</head>
<body>
<!-- Content -->
</body>
</html>
```

---

## Scrollytelling Play Cards

Vertical, section-by-section narratives. Each section has a heading, narrative text, and one or more data visualizations.

### Page Structure

```
.header            → Title bar with green accent line
.hero              → Play name, key metric cards, one-sentence framing
.section           → Repeating content blocks
  .section-head    → Section number + title
  .narrative       → 2-4 sentences of analysis
  .chart-container → D3 visualization(s)
  .source-note     → Data source attribution
.footer            → Attribution, data notes
```

### Header CSS

```css
.header {
  background: #25262B;
  padding: 1.5rem 2rem 1rem;
  border-bottom: 2px solid #56a360;
}

.header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #EAEAEA;
  margin-bottom: 0.25rem;
}

.header h1::before {
  content: '';
  display: block;
  width: 36px;
  height: 3px;
  background: #56a360;
  margin-bottom: 0.5rem;
  border-radius: 2px;
  /* IMPORTANT: Use display:block with margin-bottom. Do NOT use position:absolute
     or padding-left on h1. The bar sits above the title in normal document flow. */
}

.header .subtitle {
  font-size: 0.875rem;
  color: #909296;
  max-width: 700px;
}
```

### Section CSS

```css
.section {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
  border-bottom: 1px solid #373A40;
}

.section-head {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-num {
  font-size: 0.75rem;
  font-weight: 600;
  color: #56a360;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #EAEAEA;
}

.narrative {
  font-size: 1rem;
  color: #C1C2C5;
  max-width: 720px;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}
```

### Hero Metric Cards

```css
.metric-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 1.5rem 0;
}

.metric-card {
  background: #25262B;
  border: 1px solid #373A40;
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  min-width: 160px;
  flex: 1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25);
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #909296;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #56a360;
}

.metric-value.negative { color: #c94a4a; }
.metric-value.neutral  { color: #5B8DB8; }

.metric-note {
  font-size: 0.75rem;
  color: #5C5F66;
  margin-top: 0.25rem;
}
```

### Chart Container

```css
.chart-container {
  background: #25262B;
  border: 1px solid #373A40;
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25);
}

.chart-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #56a360;
  margin-bottom: 0.75rem;
}

.chart-container svg {
  width: 100%;
  display: block;
}
```

### Source Notes

```css
.source-note {
  font-size: 0.75rem;
  color: #5C5F66;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #2C2E33;
}
```

---

## Interactive Dashboards

Dashboards use a toolbar + main content area pattern.

**Class name rules:** Use `.dash-card` for dashboard cards. Do not rename to `.chart-card` or similar. For charts inside dashboard cards, nest a `.chart-container` inside a `.dash-card`.

### Layout

```css
.dashboard {
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  min-height: 100vh;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: #25262B;
  border-bottom: 1px solid #373A40;
  align-items: center;
}

.main-content {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .main-content { grid-template-columns: 1fr; }
}
```

### Toolbar Buttons

```css
.toolbar-btn {
  font-family: 'Archivo', sans-serif;
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
  border: 1px solid #373A40;
  border-radius: 0.5rem;
  background: #25262B;
  color: #909296;
  cursor: pointer;
  transition: all 0.15s;
}

.toolbar-btn:hover {
  border-color: #56a360;
  color: #EAEAEA;
  background: #2C2E33;
}

.toolbar-btn.active {
  background: #56a360;
  color: #fff;
  border-color: #56a360;
}
```

### Dashboard Cards

```css
.dash-card {
  background: #25262B;
  border: 1px solid #373A40;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25);
}

.dash-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.dash-card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #56a360;
}
```

### Data Tables

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: #909296;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  text-align: left;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #373A40;
}

.data-table td {
  padding: 0.5rem 0.75rem;
  color: #C1C2C5;
  border-bottom: 1px solid #2C2E33;
}

.data-table tr:hover td {
  background: rgba(86, 163, 96, 0.08);
}

.data-table .num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
```

---

## Leaflet Maps

Maps use CartoDB dark tiles and follow the same card/panel patterns.

### Map Setup

```css
#map {
  width: 100%;
  min-height: 450px;
  position: relative;
  border-radius: 0.5rem;
}
```

```javascript
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap &copy; CARTO',
  maxZoom: 18
}).addTo(map);
```

### Info Panel (map hover/click)

```css
.info-panel {
  background: rgba(26, 27, 30, 0.95);
  border: 1px solid #373A40;
  border-radius: 0.5rem;
  padding: 1rem;
  font-size: 0.875rem;
  max-width: 280px;
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.info-panel h3 {
  font-size: 0.875rem;
  font-weight: 700;
  color: #56a360;
  margin-bottom: 0.5rem;
}

.info-panel .ip-row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.125rem 0;
  color: #C1C2C5;
}

.info-panel .ip-label {
  color: #909296;
  font-size: 0.75rem;
}

.info-panel .ip-val {
  font-weight: 600;
  text-align: right;
}

.info-panel .ip-note {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #373A40;
  font-size: 0.75rem;
  color: #5C5F66;
}
```

### Legend Box

```css
.legend-box {
  background: rgba(26, 27, 30, 0.95);
  border: 1px solid #373A40;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  max-height: calc(100vh - 340px);
  overflow-y: auto;
  box-shadow: 0 1px 3px rgba(0,0,0,0.35);
}

.legend-box h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #56a360;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  cursor: pointer;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.125rem 0;
  color: #C1C2C5;
  cursor: pointer;
  transition: opacity 0.2s;
}

.legend-item.off { opacity: 0.25; }

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
```

### Choropleth Styling (GeoJSON)

```javascript
function choroplethStyle(feature, getValue, colorScale) {
  const val = getValue(feature);
  return {
    fillColor: colorScale(val),
    fillOpacity: opacityScale(val),
    weight: 1,
    color: '#373A40',
    opacity: 0.6
  };
}

function highlightFeature(e) {
  e.target.setStyle({ weight: 2, color: '#56a360', fillOpacity: 0.7 });
  e.target.bringToFront();
}

function resetHighlight(e) {
  geojsonLayer.resetStyle(e.target);
}
```

---

## Common Components

### Data Notes Footer

```css
.data-notes {
  background: #25262B;
  padding: 1rem 1.5rem;
  border-top: 1px solid #373A40;
  font-size: 0.875rem;
  color: #5C5F66;
  line-height: 1.6;
}

.data-notes h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #e89b3f;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.data-notes .dn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .data-notes .dn-grid { grid-template-columns: 1fr; }
}
```

### Attribution Footer

```css
.attribution {
  text-align: center;
  padding: 1.25rem 1.5rem;
  font-size: 0.75rem;
  color: #5C5F66;
  border-top: 1px solid #373A40;
}

.attribution a { color: #7fc77f; }
```

Content: `Net Zero Industrial Policy Lab | Johns Hopkins University | netzeropolicylab.com`

### Tooltip (shared)

```css
.tooltip {
  position: absolute;
  background: rgba(26, 27, 30, 0.96);
  border: 1px solid #373A40;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #EAEAEA;
  pointer-events: none;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  max-width: 240px;
}

.tooltip .tt-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #56a360;
  margin-bottom: 0.25rem;
}

.tooltip .tt-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.75rem;
}

.tooltip .tt-label { color: #909296; }
.tooltip .tt-val { color: #EAEAEA; font-weight: 600; }
```

### Loading Indicator

```css
#loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2000;
  font-size: 1rem;
  color: #56a360;
}
```

### Progress Bar

```css
.progress-bar {
  height: 6px;
  background: #373A40;
  border-radius: 0.25rem;
  margin-top: 0.25rem;
}

.progress-fill {
  height: 100%;
  border-radius: 0.25rem;
  background: #56a360;
  transition: width 0.3s;
}
```
