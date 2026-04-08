# NZIPL Chart Styles

Styling reference for D3.js and Chart.js visualizations. All colors reference design-tokens.md. Primary accent: #56a360 (brand-5). Body background: #1A1B1E. Card background: #25262B.

## Table of Contents
1. [D3.js Patterns](#d3js-patterns)
2. [Chart.js Configuration](#chartjs-configuration)
3. [Chart Type Selection](#chart-type-selection)

---

## D3.js Patterns

D3 is the primary charting library for scrollytelling and play cards. All charts render as SVG within `.chart-container` elements.

### SVG Container Setup

```javascript
const margin = { top: 20, right: 20, bottom: 40, left: 50 };
const width = containerWidth - margin.left - margin.right;
const height = 300 - margin.top - margin.bottom;

const svg = d3.select(container)
  .append('svg')
  .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
  .append('g')
  .attr('transform', `translate(${margin.left},${margin.top})`);
```

Use `viewBox` for responsive sizing. Do not set fixed width/height on SVG elements.

### Axis Styling

```javascript
// X-axis
svg.append('g')
  .attr('transform', `translate(0,${height})`)
  .call(d3.axisBottom(xScale).tickSize(0).tickPadding(8))
  .call(g => g.select('.domain').attr('stroke', '#373A40'))
  .call(g => g.selectAll('.tick text')
    .attr('fill', '#909296')
    .attr('font-family', 'Archivo, sans-serif')
    .attr('font-size', '12px'));

// Y-axis
svg.append('g')
  .call(d3.axisLeft(yScale).tickSize(-width).tickPadding(8).ticks(5))
  .call(g => g.select('.domain').remove())
  .call(g => g.selectAll('.tick line')
    .attr('stroke', '#2C2E33')
    .attr('stroke-dasharray', '2,2'))
  .call(g => g.selectAll('.tick text')
    .attr('fill', '#909296')
    .attr('font-family', 'Archivo, sans-serif')
    .attr('font-size', '12px'));
```

Key patterns:
- X-axis: no tick marks (`tickSize(0)`), domain line in `#373A40`
- Y-axis: no domain line, grid lines as dashed `#2C2E33` lines extending to full width
- Tick labels: Archivo, 12px, `#909296`
- Tick padding: 8px

### Bar Charts

```javascript
// Horizontal bars (most common in play cards)
svg.selectAll('.bar')
  .data(data)
  .join('rect')
  .attr('class', 'bar')
  .attr('x', 0)
  .attr('y', d => yScale(d.name))
  .attr('width', d => xScale(d.value))
  .attr('height', yScale.bandwidth())
  .attr('fill', '#56a360')
  .attr('rx', 3);

// Value labels at end of bars
svg.selectAll('.bar-label')
  .data(data)
  .join('text')
  .attr('x', d => xScale(d.value) + 6)
  .attr('y', d => yScale(d.name) + yScale.bandwidth() / 2)
  .attr('dy', '0.35em')
  .attr('fill', '#C1C2C5')
  .attr('font-family', 'Archivo, sans-serif')
  .attr('font-size', '12px')
  .text(d => formatValue(d.value));
```

Bar fill colors by context:
- Default/positive: `#56a360`
- Comparative (play A vs B): use categorical palette
- Negative/deficit: `#c94a4a`
- Highlight (selected): `#5B8DB8`

Bar radius: `rx: 3` (consistent with Mantine md radius).

### Line Charts

```javascript
const line = d3.line()
  .x(d => xScale(d.year))
  .y(d => yScale(d.value))
  .curve(d3.curveMonotoneX);

svg.append('path')
  .datum(data)
  .attr('fill', 'none')
  .attr('stroke', '#56a360')
  .attr('stroke-width', 2)
  .attr('d', line);

// Data points
svg.selectAll('.dot')
  .data(data)
  .join('circle')
  .attr('cx', d => xScale(d.year))
  .attr('cy', d => yScale(d.value))
  .attr('r', 3)
  .attr('fill', '#56a360')
  .attr('stroke', '#1A1B1E')
  .attr('stroke-width', 1.5);
```

Line weights: primary series 2px, secondary series 1.5px.
Dot stroke matches body background (`#1A1B1E`) to create visual separation.

### Treemaps

```javascript
const colorScale = d3.scaleSequential()
  .domain([0, d3.max(data, d => d.value)])
  .interpolator(d3.interpolateRgb('#325a36', '#56a360'));

cell.append('text')
  .attr('fill', '#EAEAEA')
  .attr('font-family', 'Archivo, sans-serif')
  .attr('font-size', d => d.dx > 80 ? '12px' : '10px')
  .text(d => d.data.name);
```

Treemap stroke between cells: `#1A1B1E` at 1px (uses body background to create gaps).

### Annotations

```javascript
// Reference line (e.g., RCA = 1 threshold)
svg.append('line')
  .attr('x1', xScale(1)).attr('x2', xScale(1))
  .attr('y1', 0).attr('y2', height)
  .attr('stroke', '#e89b3f')
  .attr('stroke-width', 1)
  .attr('stroke-dasharray', '4,3');

// Annotation label
svg.append('text')
  .attr('x', xScale(1) + 6)
  .attr('y', 12)
  .attr('fill', '#e89b3f')
  .attr('font-family', 'Archivo, sans-serif')
  .attr('font-size', '12px')
  .attr('font-weight', 600)
  .text('RCA = 1');
```

Annotation colors: `#e89b3f` (amber). Dashed line: `4,3`.

### D3 Tooltip

```javascript
const tooltip = d3.select('body').append('div')
  .attr('class', 'tooltip')
  .style('opacity', 0);

function showTooltip(event, d) {
  tooltip.transition().duration(150).style('opacity', 1);
  tooltip.html(`
    <div class="tt-title">${d.name}</div>
    <div class="tt-row">
      <span class="tt-label">Exports</span>
      <span class="tt-val">${formatUSD(d.exports)}</span>
    </div>
    <div class="tt-row">
      <span class="tt-label">RCA</span>
      <span class="tt-val">${d.rca.toFixed(2)}</span>
    </div>
  `)
  .style('left', (event.pageX + 12) + 'px')
  .style('top', (event.pageY - 20) + 'px');
}

function hideTooltip() {
  tooltip.transition().duration(200).style('opacity', 0);
}
```

Tooltip CSS is defined in `html-patterns.md` under Common Components.

### Number Formatting

```javascript
const formatUSD = d => {
  if (d >= 1e9) return `$${(d / 1e9).toFixed(1)}B`;
  if (d >= 1e6) return `$${(d / 1e6).toFixed(1)}M`;
  if (d >= 1e3) return `$${(d / 1e3).toFixed(0)}K`;
  return `$${d.toFixed(0)}`;
};

const formatPct = d => `${(d * 100).toFixed(1)}%`;
const formatRCA = d => d.toFixed(2);
```

---

## Chart.js Configuration

Chart.js is used for dashboards and simpler visualizations. Apply the NZIPL theme via global defaults.

### Global Defaults

```javascript
// IMPORTANT: Apply these defaults before creating any Chart instance.
Chart.defaults.color = '#909296';
Chart.defaults.borderColor = '#373A40';
Chart.defaults.font.family = "'Archivo', sans-serif";
Chart.defaults.font.size = 12;

// Legend
Chart.defaults.plugins.legend.labels.color = '#909296';
Chart.defaults.plugins.legend.labels.font = { family: "'Archivo', sans-serif", size: 12, weight: 500 };
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.legend.labels.padding = 12;

// Tooltip
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(26, 27, 30, 0.96)';
Chart.defaults.plugins.tooltip.borderColor = '#373A40';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.titleFont = { family: "'Archivo', sans-serif", size: 13, weight: 600 };
Chart.defaults.plugins.tooltip.titleColor = '#56a360';
Chart.defaults.plugins.tooltip.bodyFont = { family: "'Archivo', sans-serif", size: 12 };
Chart.defaults.plugins.tooltip.bodyColor = '#EAEAEA';
Chart.defaults.plugins.tooltip.padding = { top: 8, bottom: 8, left: 12, right: 12 };
Chart.defaults.plugins.tooltip.cornerRadius = 6;
```

### Scale Configuration

```javascript
const nziplScaleOptions = {
  x: {
    grid: { display: false },
    border: { color: '#373A40' },
    ticks: {
      color: '#909296',
      font: { family: "'Archivo', sans-serif", size: 12 },
      padding: 8
    }
  },
  y: {
    grid: {
      color: '#2C2E33',
      borderDash: [2, 2],
      drawBorder: false
    },
    ticks: {
      color: '#909296',
      font: { family: "'Archivo', sans-serif", size: 12 },
      padding: 8
    }
  }
};
```

### Bar Chart Example

```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      data: values,
      backgroundColor: '#56a360',
      borderRadius: 4,
      borderSkipped: false,
      barPercentage: 0.7,
      categoryPercentage: 0.85
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: nziplScaleOptions
  }
});
```

### Doughnut Chart

```javascript
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: labels,
    datasets: [{
      data: values,
      backgroundColor: ['#56a360', '#5B8DB8', '#e89b3f', '#c94a4a', '#8b6cc1'],
      borderColor: '#1A1B1E',
      borderWidth: 2
    }]
  },
  options: {
    responsive: true,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'right',
        labels: { color: '#909296', padding: 8 }
      }
    }
  }
});
```

Doughnut border between segments: `#1A1B1E` at 2px (matches body background). Cutout: 65%.

---

## Chart Type Selection

| Question | Chart Type | Library |
|----------|-----------|---------|
| How does X rank against peers? | Horizontal bar | D3 or Chart.js |
| How has X changed over time? | Line chart | D3 |
| What is the composition of X? | Treemap or stacked bar | D3 |
| What share does X hold? | Doughnut | Chart.js |
| Where is X concentrated geographically? | Choropleth map | Leaflet + D3 scale |
| How do two variables relate? | Scatter plot | D3 |
| What is the distribution of X? | Histogram or box plot | D3 |
| How do 3+ plays compare across metrics? | Grouped bar or radar | D3 or Chart.js |

Default chart height: 300px for standard, 400px for hero charts, 200px for small multiples.
