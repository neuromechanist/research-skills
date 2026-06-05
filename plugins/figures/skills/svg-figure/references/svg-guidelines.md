# SVG Guidelines

> Element-consistency conventions for hand-authored SVG schematics. These patterns are now mechanically enforced by `[[svg-primitives]]` — read this document when authoring SVG by hand, when understanding what `figure-qa` validates, or when reading SVG produced by another tool.

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
- **Font size**: `validate_fonts.py` treats a unitless `font-size` value as pt. Write `font-size="6"` and the validator records it as 6 pt; this is the value compared against the journal minimum (Nature 5 pt, Science/Cell/PNAS 6 pt). In the mm-viewBox convention, that same unitless value renders as 6 mm visually on screen or in print (well above the legibility floor), but you should size by the validator's pt interpretation, not by visual mm. Trust `validate_fonts.py` output over in-head math.
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

Implemented in figure-qa's geometry section (issue #47), using `svgelements` (resolved geometry) and `shapely` (distance/overlap):

- Text-bbox-inside-shape (heuristic text width from font size; exact fit is validated by `svg-primitives` at save time).
- Arrow-tip-to-target distance for any line/path with a `marker-end`.
- Bbox overlap between sibling closed shapes (containment, e.g. an icon over its background rect, is treated as intentional).

figure-qa computes these programmatically; authoring defensively (z-order, anchored text, tight bboxes) keeps figures clean either way. When a geometry dependency is missing, the agent falls back to VLM judgment for layered-element correctness.
