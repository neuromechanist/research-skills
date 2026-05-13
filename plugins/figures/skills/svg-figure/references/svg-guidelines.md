# SVG Guidelines

Element-consistency rules for SVG schematics in the figures plugin. The `figure-qa` agent's SVG branch enforces what it can programmatically; this document records the conventions for the rest.

## Coordinate system

- **Always set `viewBox` so user units equal mm.** `width="89mm" height="60mm" viewBox="0 0 89 60"` makes every coordinate inside the SVG one millimeter. This is the same convention `[[scientific-figure]]/compose.py` uses, so a panel SVG can be composed at scale 1.0 without re-mapping coordinates.
- **Use integer or one-decimal coordinates** wherever possible. Floats with five+ decimal places make diffs noisy and produce no rendering benefit at the target physical size.
- **Document origin is top-left**. Increasing y goes down. Set up a mental grid before authoring.

## Stroke and fill

- **Stroke width in mm**: 0.5 for thin grid/axis lines, 0.8 for default outlines, 1.0–1.2 for emphasis. Avoid 0.2 (sub-printer-resolution).
- **Stroke alignment**: SVG strokes are centered on the path by default. For a 1 mm-thick stroke on a `<rect width="20">`, the visible outer dimension is 21 mm. Compensate when alignment matters.
- **Stroke linejoin** for boxes with rounded corners: `linejoin="round"` plus `rx="1.5"` produces smoother corners than the default miter.
- **Fill** should be either a named palette color, `white`, `none`, or `transparent`. Avoid intermediate grays in fills (use them only for stroke/chrome).

## Color palette

The `figure-qa` SVG branch knows two named allow-lists:

- **`okabe-ito`** (also valid as `wong`): `#000000 #E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7`. Colorblind-safe; Nature-recommended.
- **`tol-bright`**: `#4477AA #EE6677 #228833 #CCBB44 #66CCEE #AA3377 #BBBBBB`. Slightly punchier; Tol's bright qualitative palette.

The agent's palette check **exempts near-gray colors** (where R/G/B channels are all within 15 of each other) and pure black/white. So use `#888`, `#999`, `#cccccc`, etc. freely for axis spines, ticks, gridlines, separators, dropshadows — they don't need to be in the palette.

For multi-panel figures where a schematic ships next to a data plot, reuse the plot's color encoding inside the schematic (e.g., if condition A is `#0072B2` in the plot, the box representing condition A in the schematic should be `#0072B2`). Reusing colors creates an implicit cross-panel legend without spelling it out.

## Element naming and IDs

When an SVG ships as a panel for a multi-panel figure, give each significant element an `id` so the composer or QA agent can address it later:

```svg
<rect id="panel-A-cortex" .../>
<text id="panel-A-cortex-label" .../>
```

IDs should be `kebab-case`, descriptive, and namespaced to the panel (`panel-A-...`, `panel-B-...`) so two SVGs composed into the same figure don't collide.

## Z-order

SVG ignores CSS `z-index` outside of HTML-rendered contexts. Document order is the only z-order. Pattern:

1. Background fills and chrome
2. Connections (lines, arrows)
3. Nodes (boxes, circles, icons)
4. Text labels on top of everything

This makes connections visually pass **under** nodes, which is the schematic convention readers expect.

## Text

- **Font family**: `Helvetica, Arial, sans-serif` is the safest cross-platform stack. Some journals require Myriad (Science) — set `font-family="Myriad Pro, Helvetica, Arial, sans-serif"` and the renderer will fall back when Myriad is absent.
- **Font size in pt** via the unitless number `font-size="9"` (which renders as 9 user units = 9 mm with our viewBox convention — wait, that's actually pt because matplotlib's SVG output uses pt and so does standard SVG when no unit is given inside a viewBox that maps to mm). The QA agent's `validate_fonts.py` walks the transform stack to compute effective pt; trust its output over your in-head math.
- **`text-anchor`** controls horizontal alignment: `start` (default, like CSS left-align), `middle`, `end`. Use `middle` for box labels.
- **`dominant-baseline`** controls vertical: `auto` (default; baseline at the given y), `middle` (centerline at the given y), `central` (similar but Unicode-aware), `hanging` (top edge at y). Use `middle` for box labels.

## File hygiene

- Strip Inkscape `sodipodi:` and `inkscape:` namespaces before shipping (they bloat the file and add no rendering value). The Inkscape CLI command is `inkscape --export-plain-svg`.
- Inline any external style — the SVG should be self-contained for portability.
- Remove unused `<defs>` and zero-size elements before committing.

## What the QA agent's SVG branch checks

Programmatic (deterministic):

- Font sizes vs journal minimum (delegated to `validate_fonts.py`; covers `<text>` and `<tspan>`).
- Palette compliance, near-gray-exempt (see above).
- Element counts (text vs shape) for sanity.

Stubbed (planned for a future iteration):

- Text-bbox-inside-shape using `svgelements` + `shapely`.
- Arrow-tip-to-target distance using `svgpathtools` tangent at `t=1`.
- Bbox overlap between sibling shapes.

Until the geometry checks ship, the agent falls back to VLM judgment for layered-element correctness. Author defensively (z-order, anchored text, tight bboxes) and the figure will pass either way.
