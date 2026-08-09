---
name: svg-figure
description: This skill should be used when the user asks to "create an SVG figure", "make a schematic", "draw a diagram", "create a schematic diagram", "draw a flowchart", "draw a process flow", "draw a workflow", "draw a workflow diagram", "make an SVG schematic", "create a process diagram", "create a pipeline diagram", "create a block diagram", "draw a system diagram", "system architecture diagram", or wants a hand-authored or programmatic SVG with shapes, arrows, and labels that the figure-qa agent can verify. **For new Python-driven figures, route to `[[svg-primitives]]` instead** — this skill is the conventions and hand-authoring reference. Outputs are SVG files that can be loaded as panel sources by the scientific-figure composer.
version: 0.2.2
---

# SVG Figure

Conventions for SVG schematics and diagrams (flowcharts, process diagrams, system diagrams, anatomical illustrations) with element-consistency guarantees: text aligned to box bounds, arrows pointing at their targets, lines passing under shapes by z-order. The output SVGs are designed to be composed as panels by the `[[scientific-figure]]` skill and verified by the `[[figure-qa]]` agent's SVG branch.

## When to use this skill

**For new programmatic work, use `[[svg-primitives]]` instead.** It implements every convention below as a mechanical guarantee — text auto-fits boxes, arrowheads stay tangent-correct on curves, paint order is deterministic, and `Canvas.save(validate='strict')` raises if any of those invariants are violated. `examples/schematic_from_primitives.py` in this skill is the canonical programmatic example.

Reach for **this** skill when:

- You are writing SVG **by hand** or with an editor like Inkscape, and need the conventions the figure-qa agent expects.
- You are using a non-Python tool to emit SVG and want to know what shape it should take.
- You are reading hand-authored SVG produced by an external collaborator and want to understand the layout grammar.
- You are debugging a figure-qa finding on an SVG that did not come from `svg-primitives`.
- The figure is a **schematic** (boxes, arrows, labels) rather than data plotted from numbers — for plots use `[[plot-styling]]`.

Reach for a different tool when:

- You are writing Python → use `[[svg-primitives]]`.
- The figure is a **plot** of data → use `[[plot-styling]]`.
- The figure is **pictorial substrate** (a brain, a microscope, a setup photo aesthetic) → use `[[ai-full-figure]]` for the substrate and overlay labels via `[[svg-primitives]]`.
- The figure needs **icon-style elements** repeated across panels → generate the icons via `[[transparent-icons]]` and place them as `<image>` references in the SVG.

## Programmatic authoring (recommended path)

See `[[svg-primitives]]`. The canonical example in this skill is `examples/schematic_from_primitives.py` which reproduces `examples/schematic.svg` using `Canvas`, `LabeledBox`, `Arrow.connect`, and `Annotation`. Run it:

```bash
cd plugins/figures/skills
uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools \
    --with cairosvg --with lxml \
    python svg-figure/examples/schematic_from_primitives.py
```

## Hand-authoring conventions

The recipes below apply when SVG is written by hand or emitted by a non-Python tool. `[[svg-primitives]]` enforces every one of them mechanically; this section is the reference for the underlying SVG conventions and is what the figure-qa agent expects when validating arbitrary SVG inputs.

### 1. Sizing

Set explicit `width`/`height` and a matching `viewBox` so user units equal mm (the same convention `[[scientific-figure]]` uses for composition):

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="89mm" height="60mm" viewBox="0 0 89 60">
  ...
</svg>
```

Now every coordinate inside the SVG is in mm, **including font-size** (it is a length in user units, not points). A `<rect width="20" height="10">` is 20mm × 10mm, and a `<text font-size="9">` is 9 mm tall (~25 pt). To target a physical point size, convert: `N pt = N × 25.4/72 mm`, so 6 pt is `font-size="2.1"` and Nature's 5 pt minimum is `font-size="1.76"`. `figure-qa` reports the physical point size, so keep body labels at `font-size` ≥ ~1.8.

> *Done automatically by `[[svg-primitives]]`*: `Canvas(width_mm, height_mm)` sets the viewBox and units.

### 2. Text aligned to box bounds

When labelling a box, the label belongs **inside** the box's bounding rectangle. Use `text-anchor="middle"` plus `dominant-baseline="middle"` and center the text at the box's centroid:

```svg
<rect x="10" y="10" width="30" height="14" fill="#F4F1DE" stroke="#1F3A5F" stroke-width="0.8" rx="1.5"/>
<text x="25" y="17" text-anchor="middle" dominant-baseline="middle"
      font-family="Helvetica, Arial, sans-serif" font-size="2.1">Cortex</text>
```

The text x is the rect's `x + width/2 = 25`. The text y is `y + height/2 = 17`. For tighter visual alignment with the rounded `rx` corner, nudge the y by ~0.5–1 mm; verify with `[[figure-qa]]`.

See `references/text-alignment.md` for the bbox arithmetic and common failure modes (text width exceeding box width, descenders dropping below the box).

> *Done automatically by `[[svg-primitives]]`*: `LabeledBox(text=...)` auto-sizes the rect from measured text bbox and centers the label.

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

> *Done automatically by `[[svg-primitives]]`*: `Arrow.connect(src, dst, curve='straight'|'cubic'|'orthogonal-h'|'orthogonal-v')` snaps straight and cubic endpoints to box outlines via path intersection (orthogonal routes use midpoint waypoints between cardinal anchors), and emits `<marker orient='auto'>` for tangent-correct rendering on every curve type.

### 4. Lines and arrows pass under shapes via z-order

SVG renders elements in document order. To draw a connection that visually passes **under** a node:

```svg
<!-- 1. Draw the connection first -->
<line x1="10" y1="30" x2="80" y2="30" stroke="#888" stroke-width="0.5"/>
<!-- 2. Draw the shape that should sit on top second -->
<circle cx="45" cy="30" r="3" fill="white" stroke="#1F3A5F" stroke-width="0.8"/>
```

Avoid `z-index` (it doesn't apply outside CSS-rendered SVG); rely on document order only.

> *Done automatically by `[[svg-primitives]]`*: register layers in paint order with `Canvas.layer(name)` and `Canvas.add_layer(Layer)`; elements added to earlier-registered layers always sit behind elements in later-registered layers, regardless of when they were added.

### 5. Color palette: pick one and stick to it

Reuse the palette from the `[[transparent-icons]]` theme bible when the schematic ships alongside icons. For schematics alone, `references/svg-guidelines.md` lists the colorblind-safe palettes the QA agent's `--palette` flag knows about (`okabe-ito`, `tol-bright`). Near-grays (`#888`, `#999`, `#ccc`) for axes/ticks/gridlines are exempt from palette compliance — use them freely for chrome.

> *Same convention in `[[svg-primitives]]`*: pass hex colors directly to `LabeledBox(fill=..., stroke=...)` and `Arrow.connect(stroke=...)`.

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
uv run --with lxml --with svgelements --with shapely \
    python "$FIGURE_QA_SCRIPTS/check_svg.py" schematics/circuit.svg \
    --journal nature --palette okabe-ito
```

The SVG branch checks font sizes, palette compliance (with near-gray exemption for chrome), and reports geometry counts.

For SVGs built with `[[svg-primitives]]`, validation also runs in-process during `Canvas.save(validate='warn'|'strict'|'off')` — that catches the same invariants (and more) before the file is even written. The two validators are complementary: `figure-qa` works on any SVG; `svg-primitives` validation works on SVGs it produced.

## Handoff to Illustrator or Affinity Designer

When a collaborator will edit the figure in Adobe Illustrator or Affinity Designer,
the SVG is the editable master and any PDF is a derived print artifact;
converted PDFs always open as fragmented point text.
Author for the editors' import quirks:
top-level `<g id="...">` per region (arrives as a named group; nothing in SVG maps to an Illustrator layer),
one `<text>` per line with `text-anchor="start"` and a computed left edge (Illustrator ignores `text-anchor` on import),
a single concrete `font-family` plus numeric `font-weight` (no stacks, no `@font-face`),
sub-figures inlined as `<g transform>` (never nested `<svg>` or SVG data-URI `<image>`),
and arrowheads baked as filled paths (never `<marker>`, which has a known Illustrator bug).
See `references/editor-handoff.md` for the full checklist,
the per-editor behavior table, print-PDF derivation recipes
(Inkscape text-to-path, Ghostscript `-dNoOutputFonts`), and sources.

## Additional resources

- `examples/schematic_from_primitives.py` — programmatic example using svg-primitives (recommended starting point).
- `examples/schematic.svg` — hand-authored reference schematic.
- `references/svg-guidelines.md` — element consistency rules and palette recommendations.
- `references/arrow-patterns.md` — straight, curved, and segmented arrow recipes; svgpathtools-compatible geometry the QA agent recognizes.
- `references/text-alignment.md` — text bbox arithmetic, baseline behavior, and common failure modes (overflow, descender drop, anchor inversion).
- `references/editor-handoff.md` — authoring rules for editable handoff to Illustrator / Affinity Designer, per-editor SVG import behavior, and print-PDF derivation (outlined text, font embedding, PDF layers).
