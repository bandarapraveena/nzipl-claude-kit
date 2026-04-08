# NZIPL PPTX Styles

Slide deck formatting using python-pptx. Maps the CICE design tokens (Mantine dark theme, green brand, Archivo font) to PowerPoint's object model.

## Table of Contents
1. [Slide Dimensions and Setup](#slide-dimensions-and-setup)
2. [Color Constants](#color-constants)
3. [Font Mapping](#font-mapping)
4. [Slide Layouts](#slide-layouts)
5. [Chart Styling in PPTX](#chart-styling-in-pptx)
6. [Common Patterns](#common-patterns)

---

## Slide Dimensions and Setup

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

prs = Presentation()
prs.slide_width = Inches(13.333)   # Widescreen 16:9
prs.slide_height = Inches(7.5)
```

Always use widescreen 16:9 (13.333 x 7.5 inches).

---

## Color Constants

```python
# Mantine dark palette
BG_BODY       = RGBColor(0x1A, 0x1B, 0x1E)   # #1A1B1E dark-7, slide background
BG_CARD       = RGBColor(0x25, 0x26, 0x2B)   # #25262B dark-6, cards/panels
BG_INPUT      = RGBColor(0x14, 0x15, 0x17)   # #141517 dark-8, recessed
BG_DEEP       = RGBColor(0x10, 0x11, 0x13)   # #101113 dark-9, deepest

# Text
TEXT_PRIMARY   = RGBColor(0xEA, 0xEA, 0xEA)   # #EAEAEA
TEXT_BODY      = RGBColor(0xC1, 0xC2, 0xC5)   # #C1C2C5 dark-0
TEXT_DIMMED    = RGBColor(0x90, 0x92, 0x96)   # #909296 dark-2
TEXT_MUTED     = RGBColor(0x5C, 0x5F, 0x66)   # #5C5F66 dark-3

# Brand green
BRAND_5       = RGBColor(0x56, 0xA3, 0x60)   # #56a360 primary accent
BRAND_6       = RGBColor(0x4A, 0x8A, 0x52)   # #4a8a52 darker accent
BRAND_4       = RGBColor(0x7F, 0xC7, 0x7F)   # #7fc77f lighter accent

# Functional
INFO_BLUE     = RGBColor(0x5B, 0x8D, 0xB8)   # #5B8DB8
WARNING_AMBER = RGBColor(0xE8, 0x9B, 0x3F)   # #e89b3f
NEGATIVE_RED  = RGBColor(0xC9, 0x4A, 0x4A)   # #c94a4a

# Border
BORDER_COLOR  = RGBColor(0x37, 0x3A, 0x40)   # #373A40 dark-4
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
```

---

## Font Mapping

Archivo must be installed on the rendering machine. Fallback: Calibri.

| Role | Primary | Fallback |
|------|---------|----------|
| Heading | Archivo | Calibri |
| Body | Archivo | Calibri Light |
| Data/code | JetBrains Mono | Consolas |

```python
FONT_MAIN = 'Archivo'
FONT_DATA = 'JetBrains Mono'

def set_font(run, name, size, bold=False, color=TEXT_PRIMARY):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
```

---

## Slide Layouts

### Title Slide

```python
def make_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG_BODY

    # Green accent bar (vertical left marker)
    # IMPORTANT: Thin VERTICAL stripe. Width = Pt(4), Height = Inches(0.35).
    bar = slide.shapes.add_shape(
        1, Inches(0.6), Inches(2.2), Pt(4), Inches(0.35)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = BRAND_5
    bar.line.fill.background()

    # Title
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(10), Inches(1.2))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    set_font(run, FONT_MAIN, 32, bold=True, color=TEXT_PRIMARY)

    # Subtitle
    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    run2.text = subtitle
    set_font(run2, FONT_MAIN, 16, color=TEXT_DIMMED)

    # Green bottom border
    border = slide.shapes.add_shape(
        1, Inches(0), Inches(7.35), Inches(13.333), Pt(3)
    )
    border.fill.solid()
    border.fill.fore_color.rgb = BRAND_5
    border.line.fill.background()

    # Attribution
    att = slide.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(8), Inches(0.4))
    p3 = att.text_frame.paragraphs[0]
    run3 = p3.add_run()
    run3.text = 'Net Zero Industrial Policy Lab | Johns Hopkins University'
    set_font(run3, FONT_MAIN, 10, color=TEXT_MUTED)

    return slide
```

### Section Divider Slide

```python
def make_section_slide(prs, section_num, section_title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG_BODY

    # Section number
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(2), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = f'SECTION {section_num}'
    set_font(run, FONT_MAIN, 11, bold=True, color=BRAND_5)

    # Section title
    txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(3.3), Inches(10), Inches(1))
    p2 = txBox2.text_frame.paragraphs[0]
    run2 = p2.add_run()
    run2.text = section_title
    set_font(run2, FONT_MAIN, 28, bold=True, color=TEXT_PRIMARY)

    # Attribution (every slide gets this, including dividers)
    att = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(8), Inches(0.3))
    p3 = att.text_frame.paragraphs[0]
    run3 = p3.add_run()
    run3.text = 'NZIPL | Johns Hopkins University'
    set_font(run3, FONT_MAIN, 9, color=TEXT_MUTED)

    return slide
```

### Content Slide (text + chart area)

```python
def make_content_slide(prs, title, body_text=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG_BODY

    # Slide title with green marker
    bar = slide.shapes.add_shape(1, Inches(0.6), Inches(0.45), Pt(4), Inches(0.35))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BRAND_5
    bar.line.fill.background()

    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = title
    set_font(run, FONT_MAIN, 18, bold=True, color=TEXT_PRIMARY)

    # Body text (left column)
    if body_text:
        txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(4.5), Inches(5.5))
        tf = txBox2.text_frame
        tf.word_wrap = True
        p2 = tf.paragraphs[0]
        run2 = p2.add_run()
        run2.text = body_text
        set_font(run2, FONT_MAIN, 13, color=TEXT_BODY)
        p2.space_after = Pt(8)

    # Chart/image area: right side
    # Placeholder: Inches(5.8) to Inches(12.5), y from 1.0 to 6.8
    # slide.shapes.add_picture(img_path, Inches(5.8), Inches(1.0), Inches(6.7), Inches(5.8))

    # Attribution
    att = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(8), Inches(0.3))
    p3 = att.text_frame.paragraphs[0]
    run3 = p3.add_run()
    run3.text = 'NZIPL | Johns Hopkins University'
    set_font(run3, FONT_MAIN, 9, color=TEXT_MUTED)

    return slide
```

### Data Slide (full-width chart or table)

```python
def make_data_slide(prs, title, source_note=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG_BODY

    # Title bar
    title_bg = slide.shapes.add_shape(
        1, Inches(0), Inches(0), Inches(13.333), Inches(0.9)
    )
    title_bg.fill.solid()
    title_bg.fill.fore_color.rgb = BG_CARD
    title_bg.line.fill.background()

    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(10), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = title
    set_font(run, FONT_MAIN, 16, bold=True, color=BRAND_5)

    # Chart area: Inches(0.5) to Inches(12.8), y from 1.1 to 6.5

    # Source note
    if source_note:
        att = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(10), Inches(0.3))
        p2 = att.text_frame.paragraphs[0]
        run2 = p2.add_run()
        run2.text = f'Source: {source_note}'
        set_font(run2, FONT_MAIN, 9, color=TEXT_MUTED)

    return slide
```

### Metric Cards Slide

```python
def make_metrics_slide(prs, title, metrics):
    """
    metrics: list of dicts with keys 'label', 'value', 'note' (optional), 'color' (optional)
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG_BODY

    # Title
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(10), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = title
    set_font(run, FONT_MAIN, 18, bold=True, color=TEXT_PRIMARY)

    # Metric cards in a row
    card_width = min(2.5, (12 - 0.5 * (len(metrics) - 1)) / len(metrics))
    start_x = (13.333 - (card_width * len(metrics) + 0.5 * (len(metrics) - 1))) / 2

    for i, m in enumerate(metrics):
        x = start_x + i * (card_width + 0.5)
        # Card background
        card = slide.shapes.add_shape(1, Inches(x), Inches(2.0), Inches(card_width), Inches(2.0))
        card.fill.solid()
        card.fill.fore_color.rgb = BG_CARD
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1)

        # Label
        lbl = slide.shapes.add_textbox(Inches(x + 0.2), Inches(2.2), Inches(card_width - 0.4), Inches(0.3))
        p_lbl = lbl.text_frame.paragraphs[0]
        r_lbl = p_lbl.add_run()
        r_lbl.text = m['label'].upper()
        set_font(r_lbl, FONT_MAIN, 9, bold=True, color=TEXT_DIMMED)

        # Value
        val = slide.shapes.add_textbox(Inches(x + 0.2), Inches(2.6), Inches(card_width - 0.4), Inches(0.8))
        p_val = val.text_frame.paragraphs[0]
        r_val = p_val.add_run()
        r_val.text = m['value']
        val_color = m.get('color', BRAND_5)
        set_font(r_val, FONT_MAIN, 28, bold=True, color=val_color)

        # Note
        if m.get('note'):
            nt = slide.shapes.add_textbox(Inches(x + 0.2), Inches(3.4), Inches(card_width - 0.4), Inches(0.4))
            p_nt = nt.text_frame.paragraphs[0]
            r_nt = p_nt.add_run()
            r_nt.text = m['note']
            set_font(r_nt, FONT_MAIN, 10, color=TEXT_MUTED)

    return slide
```

---

## Chart Styling in PPTX

Generate charts as PNG using matplotlib, then insert as pictures.

### Matplotlib NZIPL Theme

```python
import matplotlib.pyplot as plt

nzipl_theme = {
    'figure.facecolor': '#1A1B1E',
    'axes.facecolor': '#25262B',
    'axes.edgecolor': '#373A40',
    'axes.labelcolor': '#909296',
    'axes.titlesize': 13,
    'axes.titleweight': 600,
    'axes.labelsize': 12,
    'xtick.color': '#909296',
    'ytick.color': '#909296',
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'text.color': '#EAEAEA',
    'grid.color': '#2C2E33',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'legend.facecolor': '#25262B',
    'legend.edgecolor': '#373A40',
    'legend.fontsize': 11,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Archivo', 'Calibri', 'sans-serif'],
}

plt.rcParams.update(nzipl_theme)

NZIPL_COLORS = ['#56a360', '#5B8DB8', '#e89b3f', '#c94a4a', '#8b6cc1', '#c96a8b']
```

### Saving Charts for PPTX

```python
fig.savefig('chart.png', dpi=200, bbox_inches='tight',
            facecolor='#1A1B1E', edgecolor='none', transparent=False)
```

Use dpi=200 for crisp rendering. Always set facecolor to match slide background (`#1A1B1E`).

---

## Common Patterns

### Table on Slide

```python
def style_table(table):
    """Apply NZIPL styling to a pptx table."""
    for row_idx, row in enumerate(table.rows):
        for cell in row.cells:
            cell.fill.solid()
            if row_idx == 0:
                cell.fill.fore_color.rgb = BG_CARD
            else:
                cell.fill.fore_color.rgb = BG_BODY

            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    if row_idx == 0:
                        set_font(run, FONT_MAIN, 10, bold=True, color=TEXT_DIMMED)
                    else:
                        set_font(run, FONT_MAIN, 11, color=TEXT_BODY)
```

### Slide Numbers

```python
def add_slide_number(slide, num, total):
    txBox = slide.shapes.add_textbox(Inches(12.2), Inches(7.1), Inches(1), Inches(0.3))
    p = txBox.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = f'{num}/{total}'
    set_font(run, FONT_MAIN, 9, color=TEXT_MUTED)
```
