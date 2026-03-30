---
name: scientific-figures
description: This skill should be used when the user asks to "create a figure", "make a scientific figure", "create a paper figure", "generate a figure element", "make an icon", "plot data for a figure", "compose figure panels", "create a graphical abstract", "make a multi-panel figure", "generate a PDF figure", "create a Nature-style figure", "make a publication figure", "create a figure for my grant", "make a poster figure", "create a schematic diagram", or mentions scientific figures, figure elements, figure composition, figure panels, icons for papers, matplotlib/seaborn/ggplot plots for figures, or react-pdf figures.
version: 0.1.1
---

# Scientific Figures

Create publication-quality scientific figures for Nature, Science, PNAS, Cell, and other top-tier journals. This skill covers the full pipeline: generating individual figure elements (icons, plots, diagrams), composing them into multi-panel layouts, and exporting as pixel-perfect PDFs.

## Pipeline Overview

```
1. Plan layout    -->  2. Create elements  -->  3. Compose PDF  -->  4. Visual QA
   (panels, size)       (icons, plots)          (react-pdf)         (render, verify)
```

Every step uses on-the-fly execution via `uvx` (Python) or `bunx` (JS/TS); no permanent installs required.

## Quality Standards

All figures must meet these publication standards:

- **Font**: Sans-serif (Helvetica/Arial), 9-10pt for labels, 7-8pt for annotations
- **Panel labels**: Bold uppercase (A, B, C...), 12-14pt, top-left of each panel
- **Tick labels**: Clear, readable at print size, consistent decimal places
- **Line weights**: Consistent across panels (0.5-1pt for axes, 1-2pt for data)
- **Colors**: Colorblind-safe palette, consistent across all panels (see `references/color-palettes.md`)
- **Resolution**: 300 DPI minimum for raster elements, vector preferred
- **Background**: White, no unnecessary gridlines or chart junk
- **Captions**: Define all abbreviations on first use; describe each panel explicitly

Consult `references/figure-standards.md` for journal-specific dimensions and font requirements.

## Step 1: Plan the Figure Layout

Determine before creating anything:

- **Target journal**: Dictates width (single-column ~3.5in, double-column ~7.0in)
- **Panel arrangement**: Grid (2x2, 1x3, 2+1), wide-top + sub-panels, or freeform
- **Element types per panel**: Icon, data plot, schematic, photograph, or combination
- **Color palette**: Select from `references/color-palettes.md` or define custom

## Step 2: Create Figure Elements

Each panel contains one or more elements. Generate them as SVG or transparent PNG.

### Icons (gpt-image-1.5)

Flat, minimalist scientific icons in Nature/Science style. See `references/element-icons.md` for full guide.

```bash
# From template (icon bible)
uvx --from "openai python-dotenv pillow" python scripts/generate_icon.py --template brain-eeg -o elements/brain.png --transparent

# Free-form
uvx --from "openai python-dotenv pillow" python scripts/generate_icon.py "a DNA helix" -o elements/dna.png --transparent
```

Template catalog: `references/icon-templates.json`. Schema: `references/icon-bible.md`.

### Data Plots (matplotlib/seaborn)

Generate publication-quality plots as SVG or transparent PNG. See `references/element-plots.md` for full guide.

```bash
# Quick inline plot
uvx --from "matplotlib seaborn numpy" python -c "
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 9,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
})

# ... plot code ...
plt.savefig('elements/plot.svg', bbox_inches='tight', transparent=True)
"
```

Key rules for plot elements:
- Always set `transparent=True` and `bbox_inches='tight'`
- Use `savefig` with SVG format (vector, scalable) or PNG at 600 DPI
- Remove chart junk: no top/right spines, minimal gridlines
- Match the figure's shared color palette

### Data Plots (ggplot2/R, plotly)

Full ggplot2 and plotly templates with publication rcParams are in `references/element-plots.md`. Use the same font, spine, and tick conventions as the matplotlib example above.

## Step 3: Compose the Figure (react-pdf)

Assemble elements into a precisely-sized PDF using react-pdf. See `references/figure-composition.md` for full guide.

```bash
cd figures/<figure-name>
bunx --bun create-bun@latest . --yes 2>/dev/null; bunx --bun add @react-pdf/renderer react
```

Write a render script (e.g., `render.tsx`) using react-pdf primitives (`Document`, `Page`, `View`, `Text`, `Image`). See `references/react-pdf-guide.md` for API reference and `examples/multi-panel.tsx` for a working example.

Standard sizes in points (1in = 72pt):

| Journal | Single column | Double column |
|---------|--------------|--------------|
| Nature | 252pt (89mm) | 519pt (183mm) |
| Science | 245pt | 504pt |
| PNAS | 246pt | 504pt |
| Cell | 241pt (85mm) | 493pt (174mm) |

```bash
bunx --bun run render.tsx    # outputs figure.pdf
```

For researchers using LaTeX for figure composition, standard LaTeX figure tools (includegraphics, subfigure) remain a valid alternative. This skill focuses on the react-pdf workflow for its precise layout control and programmatic composition.

## Step 4: Visual QA Feedback Loop

After rendering the PDF, verify it is paper-ready before delivery. This step is critical; figure creation without visual verification is incomplete.

### Render PDF to PNG for inspection

```bash
uvx --from "pdf2image pillow" python -c "
from pdf2image import convert_from_path
pages = convert_from_path('figure.pdf', dpi=300)
pages[0].save('figure_preview.png', 'PNG')
"
```

See `references/figure-composition.md` for alternative conversion approaches (e.g., pdftoppm).

### Read and inspect the rendered image

**You must read `figure_preview.png` using the Read tool.** Do not skip this step. Visually analyze the image and verify every item below. Report each finding explicitly.

#### Layout and alignment
- [ ] Dimensions match target journal specs
- [ ] Panel labels (A, B, C...) are visible, bold, top-left positioned, and vertically aligned with each other across the figure
- [ ] All panels are evenly spaced with consistent gutters
- [ ] No elements are clipped, bleeding outside panel boundaries, or extending into adjacent panels

#### Text and labels
- [ ] All text is readable at print size (9-10pt body, 7-8pt annotations)
- [ ] Font is sans-serif throughout (no serif or monospace leaks)
- [ ] Axis labels, tick labels, and annotations do not overlap each other or overlap data
- [ ] Panel titles or subtitles (if present) are consistently positioned and formatted
- [ ] No text is cut off, truncated, or running into panel edges

#### Arrows, connectors, and annotations
- [ ] Arrows point to their intended targets and do not cross over unrelated elements
- [ ] Annotation lines or brackets do not overlap other annotations or data
- [ ] Arrow styles are consistent (same head type, line weight, color)
- [ ] Connector paths are clean with no unnecessary crossings

#### Visual quality
- [ ] Colors are consistent across panels and match the chosen palette
- [ ] Tick marks and axis labels are clear with consistent decimal places
- [ ] Scale bars (if present) have correct labels and consistent sizing
- [ ] White background, no artifacts, unwanted borders, or rendering glitches
- [ ] Icons/images are sharp (not blurry from over-scaling or under-resolution)
- [ ] Line weights are consistent across all panels and elements

#### Paper-readiness
- [ ] Figure looks professional and polished at actual print size
- [ ] Visual hierarchy is clear: the most important data draws the eye first
- [ ] No placeholder text, debug borders, or development artifacts remain
- [ ] Figure would not require revisions from a journal production team

### Iterate until paper-ready

If **any** issue is found:
1. Describe the specific problem (e.g., "Panel B y-axis label overlaps the tick labels at the bottom")
2. Fix the render script (`render.tsx`) to address the issue
3. Re-run steps 3-4 (re-render PDF, re-convert to PNG, re-inspect)
4. Repeat until every checklist item passes

Do not deliver a figure that has not passed visual QA. A figure with overlapping labels or misaligned panels undermines the quality of the entire paper.

## Caption Guidelines

Generate a figure caption that:
- Starts with a concise title (bold, one sentence)
- Describes each panel: "(A) Description of panel A. (B) Description of panel B."
- Defines all abbreviations on first use (e.g., "electroencephalography (EEG)")
- Notes sample sizes, statistical tests, and error bar meanings where applicable
- States scale bar values if present

## Additional Resources

### Reference Files
- **`references/figure-standards.md`** - Journal dimension specs, font rules, resolution requirements
- **`references/color-palettes.md`** - Curated publication-quality color palettes (colorblind-safe)
- **`references/element-icons.md`** - Icon generation guide (gpt-image-1.5, templates, style)
- **`references/element-plots.md`** - Plot element guide (matplotlib, seaborn, plotly, ggplot2)
- **`references/figure-composition.md`** - react-pdf composition workflow and QA loop
- **`references/react-pdf-guide.md`** - react-pdf API quick reference
- **`references/icon-bible.md`** - Icon template schema and categories
- **`references/icon-templates.json`** - Structured icon template catalog

### Examples
- **`examples/multi-panel.tsx`** - Working 2x2 panel react-pdf figure
- **`examples/matplotlib-element.py`** - Publication-quality matplotlib element

### Scripts
- **`scripts/generate_icon.py`** - Icon generation via gpt-image-1.5 (template and free-form)
