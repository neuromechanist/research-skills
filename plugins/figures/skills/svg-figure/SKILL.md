---
name: svg-figure
description: This skill should be used when the user asks to "create an SVG figure", "make a schematic", "draw a diagram", "create a schematic diagram", "draw a flowchart", "draw a process flow", "draw a workflow", "draw a workflow diagram", "make an SVG schematic", "create a process diagram", "create a pipeline diagram", "create a block diagram", "draw a system diagram", "system architecture diagram", or wants a hand-authored or programmatic SVG with shapes, arrows, and labels that the figure-qa agent can verify. Outputs are SVG files that can be loaded as panel sources by the scientific-figure composer.
version: 0.1.0
---

# SVG Figure

Create SVG schematics and diagrams (flowcharts, process diagrams, system diagrams, anatomical illustrations) with element-consistency guarantees: text aligned to box bounds, arrows pointing at their targets, lines passing under shapes by z-order. The output SVGs are designed to be composed as panels by the `[[scientific-figure]]` skill and verified by the `[[figure-qa]]` agent's SVG branch.

## When to use this skill

Reach for `svg-figure` when:

- The figure is a **schematic** (boxes, arrows, labels) rather than data plotted from numbers — for plots use `[[plot-styling]]`.
- You need precise control over every element's position and the result must reproduce identically across machines — AI image generation produces convincing pictures but cannot place a label at a specific mm coordinate.
- The figure will be **composited into a multi-panel figure** as a panel SVG that `scientific-figure/compose.py` loads.

Reach for a different tool when:

- The figure is a **plot** of data → use `[[plot-styling]]`.
- The figure is **pictorial substrate** (a brain, a microscope, a setup photo aesthetic) → use `[[ai-full-figure]]` for the substrate and overlay labels here.
- The figure needs **icon-style elements** repeated across panels → generate the icons via `[[transparent-icons]]` and place them as `<image>` references in the SVG.

## Authoring patterns

The recipes here are deliberately library-agnostic — the SVG can be written by hand, generated from a Python script via `svgutils.transform`, or produced by Inkscape and then post-processed. The constraints below apply regardless.

### 1. Sizing

Set explicit `width`/`height` and a matching `viewBox` so user units equal mm (the same convention `[[scientific-figure]]` uses for composition):

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="89mm" height="60mm" viewBox="0 0 89 60">
  ...
</svg>
```

Now every coordinate inside the SVG is in mm. A `<text font-size="9">` is 9 pt. A `<rect width="20" height="10">` is 20mm × 10mm.

### 2. Text aligned to box bounds

When labelling a box, the label belongs **inside** the box's bounding rectangle. Use `text-anchor="middle"` plus `dominant-baseline="middle"` and center the text at the box's centroid:

```svg
<rect x="10" y="10" width="30" height="14" fill="#F4F1DE" stroke="#1F3A5F" stroke-width="0.8" rx="1.5"/>
<text x="25" y="17" text-anchor="middle" dominant-baseline="middle"
      font-family="Helvetica, Arial, sans-serif" font-size="6">Cortex</text>
```

The text x is the rect's `x + width/2 = 25`. The text y is `y + height/2 = 17`. For tighter visual alignment with the rounded `rx` corner, nudge the y by ~0.5–1 mm; verify with `[[figure-qa]]` SVG branch (its bbox-inside-shape check will catch text that bleeds past the rect).

See `references/text-alignment.md` for the bbox arithmetic and common failure modes (text width exceeding box width, descenders dropping below the box).

### 3. Arrows that point at their target

A correct arrow ends exactly at the edge of its target shape, with its head oriented along the final tangent of the path. Two patterns work well:

**Straight arrow (line + marker):**

```svg
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="3" markerHeight="3" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#1F3A5F"/>
  </marker>
</defs>
<line x1="40" y1="17" x2="55" y2="17"
      stroke="#1F3A5F" stroke-width="0.8" marker-end="url(#arrow)"/>
```

`markerWidth="3" markerHeight="3"` gives a ~3 mm arrowhead in the mm-viewBox convention. Scale with stroke weight (~3–4× stroke width is a good rule); `markerWidth="6"` produces an oversized head on 0.8 mm strokes.

`refX="9"` places the marker's reference point near the tip of the triangle, so `x2,y2` is the visual tip. The arrow visually ends exactly at the target's x = 55.

**Curved arrow (cubic path + marker):**

```svg
<path d="M 40 17 C 47 17, 47 30, 55 30" fill="none"
      stroke="#1F3A5F" stroke-width="0.8" marker-end="url(#arrow)"/>
```

The control points (`47 17, 47 30`) make a smooth S; the tangent at `t=1` runs toward `(55,30)`. Verify the arrow tip touches its target with the SVG QA check (`check_svg.py` will flag tip-to-target distance > tolerance).

See `references/arrow-patterns.md` for the full svgpathtools-compatible patterns the QA agent recognizes.

### 4. Lines and arrows pass under shapes via z-order

SVG renders elements in document order. To draw a connection that visually passes **under** a node:

```svg
<!-- 1. Draw the connection first -->
<line x1="10" y1="30" x2="80" y2="30" stroke="#888" stroke-width="0.5"/>
<!-- 2. Draw the shape that should sit on top second -->
<circle cx="45" cy="30" r="3" fill="white" stroke="#1F3A5F" stroke-width="0.8"/>
```

Avoid `z-index` (it doesn't apply outside CSS-rendered SVG); rely on document order only. The QA agent's geometry section checks whether a connection drawn after a shape erroneously sits on top.

### 5. Color palette: pick one and stick to it

Reuse the palette from the `[[transparent-icons]]` theme bible when the schematic ships alongside icons. For schematics alone, `references/svg-guidelines.md` lists the colorblind-safe palettes the QA agent's `--palette` flag knows about (`okabe-ito`, `tol-bright`). Near-grays (`#888`, `#999`, `#ccc`) for axes/ticks/gridlines are exempt from palette compliance — use them freely for chrome.

## Programmatic authoring (Python)

For schematics that need to be reproducible from data (e.g., a flowchart whose nodes correspond to entries in a YAML config), drive the SVG from Python using `svgwrite` or directly via `svgutils.transform`:

```bash
uv run --with svgwrite python build_schematic.py --config nodes.yaml -o schematic.svg
```

`build_schematic.py` is a thin wrapper that loads the config, places rects, draws connections, and emits the SVG. See `examples/schematic.svg` for the expected output shape and use it as a template.

## Composition into a panel

Once authored, the SVG is a panel source for `[[scientific-figure]]`:

```python
from compose import Figure

Figure(width_mm=183, height_mm=60, journal="nature") \
    .add_panel("panels/data.svg", x_mm=0, y_mm=0, scale=0.5, label="A") \
    .add_panel("schematics/circuit.svg", x_mm=92, y_mm=0, scale=1.0, label="B") \
    .save("figure.svg")
```

The schematic is typically sized at the **final** panel dimensions and composed at `scale=1.0` — schematics don't have plot tick labels that would shrink below readable when scaled.

## Quality assurance

After authoring, invoke `[[figure-qa]]`:

```bash
uv run --with lxml --with svgelements --with svgpathtools --with shapely \
    python "$FIGURE_QA_SCRIPTS/check_svg.py" schematics/circuit.svg \
    --journal nature --palette okabe-ito
```

The SVG branch checks font sizes (delegating to `validate_fonts.py`), palette compliance (with near-gray exemption for chrome), and reports geometry counts. Bbox-overlap and arrow-tip distance are stubbed in the current release; until they ship, run the agent for a VLM-based layered-element judgment.

## Additional resources

- `references/svg-guidelines.md` — element consistency rules and palette recommendations
- `references/arrow-patterns.md` — straight, curved, and segmented arrow recipes; svgpathtools-compatible geometry the QA agent recognizes
- `references/text-alignment.md` — text bbox arithmetic, baseline behavior, and common failure modes (overflow, descender drop, anchor inversion)
- `examples/schematic.svg` — annotated reference schematic
