---
name: pdf-figures
description: This skill should be used when the user asks to "create a figure", "make a paper figure", "compose a scientific figure", "build a figure panel", "create a graphical abstract", "make a multi-panel figure", "generate a PDF figure", "create a figure for a paper", "layout figure panels", or mentions figure composition, figure panels, paper-ready figures, or react-pdf figures.
version: 0.1.0
---

# Paper-Ready PDF Figures

Creates publication-quality composite figures using React and react-pdf, combining icons, diagrams, text labels, and panels into precisely-sized PDF outputs matching journal requirements.

## When to Use

Activate when the user needs to compose multi-element scientific figures for papers, grants, or presentations. This skill handles layout, sizing, and PDF export; use the **icon-generation** skill first to create individual icons that feed into these compositions.

## Standard Figure Sizes

Academic journals have specific column width requirements. All dimensions in inches:

| Size Name | Width | Height | Use Case |
|-----------|-------|--------|----------|
| `single-column` | 3.5 | auto | Single column width (most journals) |
| `1.5-column` | 5.0 | auto | 1.5 column width |
| `double-column` | 7.0 | auto | Full page width |
| `half-page` | 7.0 | 4.5 | Half page (width x height) |
| `full-page` | 7.0 | 9.0 | Full page |
| `quarter-page` | 3.5 | 4.5 | Quarter page |
| `3-inch` | 3.0 | 3.0 | Small square panel |
| `nature-single` | 3.5 | auto | Nature single column (89mm) |
| `nature-double` | 7.1 | auto | Nature double column (183mm) |
| `science-single` | 3.4 | auto | Science single column |
| `science-double` | 7.0 | auto | Science double column |

Height marked "auto" scales to content. Override any dimension explicitly.

## Workflow

### 1. Plan the figure layout

Determine:
- **Target size**: From the table above or custom dimensions
- **Panel arrangement**: Grid layout (e.g., 2x2, 1x3, 2+1)
- **Elements per panel**: Icons, data plots, text labels, arrows, brackets
- **Panel labels**: A, B, C... (uppercase, bold, top-left)

### 2. Gather assets

- Generate icons using the **icon-generation** skill
- Export data plots from analysis tools (matplotlib, R) as PNG/SVG
- Prepare text labels and annotations

### 3. Create the figure project

Initialize a react-pdf project for the figure:

```bash
mkdir -p figures/<figure-name> && cd figures/<figure-name>
bun init -y
bun add @react-pdf/renderer react
```

### 4. Write the figure component

Create a React component using react-pdf primitives. The figure script uses `@react-pdf/renderer` to compose elements:

```jsx
import { Document, Page, View, Text, Image, StyleSheet } from '@react-pdf/renderer';
import { renderToFile } from '@react-pdf/renderer';

// Standard sizes in points (1 inch = 72 points)
const SIZES = {
  'single-column': { width: 252 },      // 3.5 in
  'double-column': { width: 504 },      // 7.0 in
  'half-page':     { width: 504, height: 324 },  // 7.0 x 4.5 in
  'nature-single': { width: 252 },      // 89mm
  'nature-double': { width: 511 },      // 183mm
};

const styles = StyleSheet.create({
  page: { padding: 0, backgroundColor: 'white' },
  panelLabel: { fontSize: 14, fontWeight: 'bold', fontFamily: 'Helvetica-Bold' },
  caption: { fontSize: 8, fontFamily: 'Helvetica' },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  panel: { alignItems: 'center' },
});
```

### 5. Render to PDF

```bash
bun run render.tsx  # outputs figure.pdf
```

### 6. Review and iterate

Open the PDF and verify:
- Dimensions match journal requirements
- Panel labels are visible and correctly positioned
- Icons/images are sharp (not blurry from scaling)
- Text is readable at print size
- Colors are consistent across panels
- No elements overlap or are cut off

## Figure Composition Patterns

### Multi-panel grid (e.g., Figure 1A-D)
```
+--------+--------+
|   A    |   B    |
+--------+--------+
|   C    |   D    |
+--------+--------+
```
Use `flexDirection: 'row'` with `flexWrap: 'wrap'` for grid layouts.

### Wide panel + sub-panels (e.g., overview + details)
```
+------------------+
|        A         |
+--------+---------+
|   B    |    C    |
+--------+---------+
```
Stack a full-width View on top, then a row of half-width Views.

### Workflow/pipeline diagram
```
[Icon1] --> [Icon2] --> [Icon3]
  |            |           |
 Label1     Label2      Label3
```
Use a row of Views with arrow images or drawn lines between elements.

### Graphical abstract
```
+----------------------------------+
|  Title text                      |
|  +------+  +------+  +------+   |
|  | Icon |->| Icon |->| Icon |   |
|  +------+  +------+  +------+   |
|  Key finding text                |
+----------------------------------+
```

## Typography

### Font Guidelines
- **Panel labels**: Helvetica-Bold, 14pt (A, B, C...)
- **Axis labels**: Helvetica, 8-10pt
- **Annotations**: Helvetica, 7-8pt
- **Scale bars**: Helvetica, 7pt

### Text Placement
- Panel labels: top-left corner, offset 4pt from edges
- Captions: below figure, not inside the PDF (added in manuscript)
- Annotations: adjacent to the element they describe

## Color Consistency

Maintain a shared color palette across all panels:

```js
const PALETTE = {
  primary: '#2D7D9A',
  secondary: '#E8734A',
  accent: '#F5C242',
  neutral: '#4A4A4A',
  background: '#FFFFFF',
  lightGray: '#F5F5F5',
};
```

Define colors once and reference throughout the figure.

## Additional Resources

### Reference Files
- **`references/figure-sizes.md`** - Complete journal dimension specifications
- **`references/react-pdf-guide.md`** - react-pdf API quick reference

### Example Files
- **`examples/multi-panel.tsx`** - Working 2x2 panel figure example
