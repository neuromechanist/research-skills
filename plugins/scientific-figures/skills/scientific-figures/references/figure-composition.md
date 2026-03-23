# Figure Composition with react-pdf

Assemble individual figure elements (icons, plots, diagrams) into publication-ready multi-panel PDF figures using react-pdf. All execution via `bunx`; no permanent installs.

## Setup

```bash
mkdir -p figures/<figure-name> && cd figures/<figure-name>
bunx --bun create-bun@latest . --yes 2>/dev/null
bunx --bun add @react-pdf/renderer react
```

## Core Workflow

### 1. Create the render script

Write a `render.tsx` file using react-pdf primitives. See `react-pdf-guide.md` for API reference.

```tsx
import React from 'react';
import { Document, Page, View, Text, Image, StyleSheet, renderToFile } from '@react-pdf/renderer';

// Double-column, half-page: 7.0 x 4.5 inches = 504 x 324 points
const PAGE = { width: 504, height: 324 };

const PALETTE = {
  primary: '#0072B2',
  secondary: '#D55E00',
  accent: '#009E73',
  text: '#333333',
};

const styles = StyleSheet.create({
  page: { width: PAGE.width, height: PAGE.height, backgroundColor: 'white', flexDirection: 'row', flexWrap: 'wrap' },
  panel: { width: PAGE.width / 2, height: PAGE.height / 2, position: 'relative', alignItems: 'center', justifyContent: 'center', padding: 16 },
  panelLabel: { position: 'absolute', top: 4, left: 6, fontSize: 14, fontFamily: 'Helvetica-Bold', color: PALETTE.text },
  element: { width: 80, height: 80, objectFit: 'contain' },
  caption: { fontSize: 8, fontFamily: 'Helvetica', color: PALETTE.text, textAlign: 'center', marginTop: 6 },
});

const Panel = ({ label, src, caption }: { label: string; src: string; caption: string }) => (
  <View style={styles.panel}>
    <Text style={styles.panelLabel}>{label}</Text>
    <Image src={src} style={styles.element} />
    <Text style={styles.caption}>{caption}</Text>
  </View>
);

const Figure = () => (
  <Document>
    <Page size={[PAGE.width, PAGE.height]} style={styles.page}>
      <Panel label="A" src="../../elements/brain.png" caption="EEG recording setup" />
      <Panel label="B" src="../../elements/analysis.svg" caption="Signal processing pipeline" />
      <Panel label="C" src="../../elements/network.svg" caption="Connectivity analysis" />
      <Panel label="D" src="../../elements/results.svg" caption="Group comparison" />
    </Page>
  </Document>
);

const output = process.argv[2] || 'figure.pdf';
renderToFile(<Figure />, output).then(() => console.log(`Rendered: ${output}`));
```

### 2. Render

```bash
bunx --bun run render.tsx
```

### 3. Convert PDF to PNG for visual QA

```bash
# Using poppler (pdftoppm)
pdftoppm -png -r 300 figure.pdf figure_preview

# Or using Python
uvx --from "pdf2image pillow" python -c "
from pdf2image import convert_from_path
pages = convert_from_path('figure.pdf', dpi=300)
pages[0].save('figure_preview.png', 'PNG')
"
```

### 4. Visual inspection

Read `figure_preview.png` and verify against the QA checklist:

- Dimensions match target journal specs
- Panel labels (A, B, C) are visible, bold, correctly positioned
- All text readable at print size (9-10pt labels, 7-8pt annotations)
- Sans-serif font throughout
- Colors consistent across panels
- No overlapping, clipped, or bleeding elements
- Tick marks and axis labels clear
- White background, no artifacts
- Icons/images sharp (not blurry)

### 5. Iterate

Fix issues in `render.tsx`, re-run steps 2-4 until pixel-perfect.

## Layout Patterns

### Multi-panel grid (2x2)
```
+--------+--------+
|   A    |   B    |
+--------+--------+
|   C    |   D    |
+--------+--------+
```
Use `flexDirection: 'row'` with `flexWrap: 'wrap'`, each panel at 50% width.

### Wide top + sub-panels
```
+------------------+
|        A         |
+--------+---------+
|   B    |    C    |
+--------+---------+
```
Stack a full-width View on top, then a row of half-width Views.

### Workflow/pipeline
```
[Icon1] --> [Icon2] --> [Icon3]
  |            |           |
 Label1     Label2      Label3
```
Row of Views with arrow characters or SVG arrows between elements.

### Asymmetric panels (e.g., 1 large + 2 small)
```
+------------+------+
|            |  B   |
|     A      +------+
|            |  C   |
+------------+------+
```
Use nested `flexDirection: 'row'` with `flex: 2` and `flex: 1` ratios.

## Typography in Composition

| Element | Font | Size (pt) |
|---------|------|-----------|
| Panel labels | Helvetica-Bold | 12-14 |
| Subcaptions | Helvetica | 8 |
| Annotations | Helvetica | 7-8 |
| Scale bars | Helvetica | 7 |

## Color Consistency

Define the palette once at the top of the render script. Reference the same object for all text, borders, and highlights. Match the palette used in plot elements.

## Standard Page Sizes

| Preset | Width (pt) | Height (pt) | Inches |
|--------|-----------|-------------|--------|
| nature-single | 252 | auto | 3.5 x auto |
| nature-double | 519 | auto | 7.2 x auto |
| science-single | 245 | auto | 3.4 x auto |
| science-double | 504 | auto | 7.0 x auto |
| half-page | 504 | 324 | 7.0 x 4.5 |
| full-page | 504 | 648 | 7.0 x 9.0 |

## Embedding Elements

### Raster images (PNG, JPG)
```tsx
<Image src="elements/plot.png" style={{ width: 200, height: 150, objectFit: 'contain' }} />
```

### SVG files
react-pdf supports SVG via the `Svg` component for inline SVG, or convert to PNG first:

```bash
# Convert SVG to PNG at 600 DPI for embedding
uvx --from "cairosvg" python -c "
import cairosvg
cairosvg.svg2png(url='elements/plot.svg', write_to='elements/plot.png', dpi=600)
"
```

### Scaling rules
- Set explicit width/height in points; react-pdf scales the image to fit
- Use `objectFit: 'contain'` to maintain aspect ratio
- For icons: 60-100pt width (typical panel icon size)
- For plots: match the panel width minus padding

## Working Example

See `examples/multi-panel.tsx` for a complete 2x2 panel figure with placeholder panels.
