---
name: svg-primitives
description: 'Use when the user asks to build a programmatic SVG schematic in Python: flowcharts, boxes and arrows, auto-fit SVG text, mm-precise diagrams, edge-snapped arrows, tangent-correct curve arrowheads, orthogonal or Manhattan routing, deterministic z-order layers, labeled groups, bracket groupings, leader-line annotations, or strict Canvas.save validation for text overflow. Use figure-qa instead for after-the-fact validation of arbitrary hand-authored or exported SVGs. Built on drawsvg, svgpathtools, and fontTools; output SVGs can be composed by scientific-figure.'
version: 0.3.1
---

# SVG Primitives

Build mm-precise SVG schematics in Python with three mechanical guarantees:

1. **Text never overflows its container** — labeled shapes auto-size to fit measured text bbox + padding.
2. **Arrowheads stay tangent-correct** — arrows emit `<marker orient="auto">` so the renderer rotates the head along the path's terminal tangent; works on straight lines and cubic Beziers.
3. **Paint order is deterministic** — layers paint in registration order; connectors visibly pass under boxes without manual reordering.

The skill ships an end-to-end pytest suite (50+ tests) that renders SVGs and asserts these invariants on the rendered output, so the guarantees are enforced by construction rather than by hand-checking each figure.

## When to use this skill

Reach for `svg-primitives` when:

- The figure is a **schematic** (boxes, arrows, labels) and you're driving it from Python — e.g. nodes come from a YAML config, or the layout depends on data.
- You need the boxes to **auto-fit** their labels (no hand-tuning widths).
- The figure has **curved arrows** that must point cleanly at their targets.
- You want **deterministic z-order** so connectors sit under shapes without manual element reordering.
- The output will be **composed into a multi-panel figure** as a panel SVG that `scientific-figure/compose.py` loads.

Reach for a different tool when:

- The figure is **plotted from numbers** (matplotlib/seaborn/plotnine) → use `[[plot-styling]]`.
- The figure is a **photographic / pictorial substrate** (a brain scene, microscope setup) → use `[[ai-full-figure]]` for the substrate and overlay labels via Arrow/LabeledBox here.
- The figure is **hand-authored SVG** or the patterns are reference material for hand-authoring → use `[[svg-figure]]` (this skill's library-agnostic counterpart).

## Quick start

```python
from svg_primitives import Canvas, LabeledBox, Arrow

c = Canvas(width_mm=183, height_mm=80)
boxes = c.layer("boxes")
arrows = c.layer("connectors")

raw = boxes.add(LabeledBox(x=10, y=20, text="Raw EEG", font_size=7))
band = boxes.add(LabeledBox.next_to(raw, side="E", gap=10, text="Bandpass\nfilter", font_size=7))
ica = boxes.add(LabeledBox.next_to(band, side="E", gap=10, text="Independent component\nanalysis", font_size=7))

arrows.add(Arrow.connect(raw, band))                          # straight, snapped to edges
arrows.add(Arrow.connect(band, ica))                          # straight
arrows.add(Arrow.connect(ica, raw, curve="cubic", bow=14,     # feedback arc
                          stroke="#C45146"))                  # red — gets its own red marker

c.save("eeg.svg", output_png=True)
```

`examples/eeg_pipeline.py` is the canonical reference; run it to see the full output:

```bash
uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools --with cairosvg \
  python plugins/figures/skills/svg-primitives/examples/eeg_pipeline.py
```

## Primitive reference

### `Canvas(width_mm, height_mm, background=None)`

The root drawing surface. User units equal mm; the `viewBox` is set so coordinates inside the SVG are in mm and font-size is emitted in mm regardless of the input pt size.

- `.layer(name) -> Layer` — gets or creates a named layer. Subsequent `.layer("boxes")` calls return the same layer.
- `.add_layer(Layer) -> Canvas` — explicit insertion when registration order matters.
- `.save(path, output_png=False, png_width=1800)` — writes the SVG; with `output_png=True`, also writes a sibling PNG via cairosvg.

Layer paint order is the order layers were first registered. Typical convention: `background` → `connectors` → `boxes` → `labels`.

### `Layer(name)`

An ordered bucket of elements. `.add(element)` appends and returns the element so calls chain.

### `LabeledBox(x, y, text, font_size=7, padding=2, ...)`

Auto-sized rounded rectangle with centered text. The width and height are computed from the measured text bbox (via fontTools) plus `padding` on every side, clamped by `min_width` / `min_height`. Multi-line text (newline-separated) stacks with `line_spacing` em between baselines.

- `anchor="top-left"` (default) — `x, y` is the top-left corner.
- `anchor="center"` — `x, y` is the centroid.
- `.anchor_point("N"|"S"|"E"|"W") -> complex` — exposed for `Arrow.connect`.
- `.outline_path() -> svgpathtools.Path` — used internally for arrow edge snapping.
- `.next_to(other, side, gap, **kwargs)` (classmethod) — build a sibling positioned relative to an existing box.

`font_size` is in **pt** for ergonomics (`font_size=7` matches "7 pt Helvetica" in typographic terms). The emitted SVG `font-size` attribute is in mm (`pt × 25.4 / 72`).

### `Pill(...)` and `Diamond(...)`

Variants of `LabeledBox`:

- `Pill` — corner radius equals `height/2` after auto-sizing → flat-sided capsule. Good for terminal nodes.
- `Diamond` — rhombus. Width and height are doubled after the text + padding measurement so the inscribed text rectangle fits. Outline is a 4-edge polygon.

### `Arrow.connect(src, dst, curve=..., bow=0, src_side="auto", dst_side="auto", via=None, corner_radius=0, stroke, stroke_width)`

Connector between two shapes (any `Shape` — `LabeledBox`, `Pill`, `Diamond`, `Group`). Returns an Arrow object that the Canvas renders as an SVG `<path>` with `marker-end` referencing a per-color marker.

- `curve="straight"` (default) — direct line; endpoints snapped to box outlines.
- `curve="cubic"` — Bezier with control points perpendicular to the chord at `bow` mm of bulge. Positive `bow` = upward (negative SVG y), negative = downward.
- `curve="orthogonal-h"` — three-segment right-angle path: out horizontally from `src`, vertical traverse at the x-midpoint, in horizontally to `dst`. Auto-sides become E/W.
- `curve="orthogonal-v"` — same idea, vertical-first: out vertically, horizontal at the y-midpoint, in vertically. Auto-sides become N/S.
- `via=[(x, y), ...]` — multi-waypoint path (straight curve only). The polyline passes through each waypoint in order between `src` and `dst`.
- `corner_radius` — when > 0, each interior corner of a polyline (`via` mode) is replaced with a quadratic Bezier of that radius, clamped to half the shorter adjoining segment.
- `src_side` / `dst_side` — `"auto"` picks the appropriate side; override to force `"N"`, `"S"`, `"E"`, `"W"`.

Arrowhead orientation is delivered by `<marker orient="auto">`, so the head is always rotated to match the path tangent at the terminal point — including on cubic splines and orthogonal turns.

### `Bracket(start, end, depth, label=None, label_offset=2, ...)`

Square-style bracket ("rake") for grouping elements. The spine sits `depth` mm perpendicular to the start-end line; the optional label sits at the spine apex `label_offset` mm further out on the closed side of the bracket. Renders as one `<path>` plus an optional `<text>`. Useful for electrode-group labels, time-window annotations, or condition spans in EEG/EMG figures.

### `Annotation(x, y, text, leader_to=None, ...)`

Text label at `(x, y)` with an optional leader line drawn from the text bounding box edge to a target coordinate. When `leader_to` is `None`, just text. The leader is computed against the measured text bbox so the line starts at the visual edge of the text (not its centroid), with a configurable `leader_gap`.

### `Group(*shapes)`

Virtual container — not a renderable. Exposes the union-bbox geometry of its member shapes (`cx`, `cy`, `left/right/top/bottom`, `anchor_point`, `outline_path`) so `Arrow.connect(group, other_box)` works the same as connecting two boxes, but the arrow snaps to the rectangle that bounds all members. Useful when an arrow should target a cluster of boxes as one visual unit (e.g. "all frontal channels feed the regressor").

The `Shape` Protocol formalizes the minimal geometry contract — anything with `cx`, `cy`, `anchor_point`, and `outline_path` is accepted by `Arrow.connect`. `LabeledBox`, `Pill`, `Diamond`, and `Group` all satisfy it.

## Anchor system

Every shape exposes four cardinal anchor points: `N` (top center), `S` (bottom center), `E` (right center), `W` (left center). When `Arrow.connect` is given `src_side="auto"`, it picks the side of `src` facing `dst` and likewise for `dst`. Override either side explicitly to draw a feedback loop:

```python
Arrow.connect(rejection, ica, curve="cubic", src_side="N", dst_side="N", bow=14)
```

## Layering rules

SVG has no z-index — paint order is document order. The Canvas flushes layers in the order they were first registered, so `c.layer("background").add(...)` will sit behind `c.layer("boxes").add(...)` even if it's added later, as long as the `background` layer was registered first. Add a layer once at the top of the build function to lock its z-position:

```python
c.layer("background")    # locks z=0
c.layer("connectors")    # locks z=1
c.layer("boxes")         # locks z=2
# ... add elements to any layer in any order from here
```

## Validation

`Canvas.save(path, validate=...)` accepts three modes:

| Mode | Behavior |
| --- | --- |
| `"warn"` (default) | Run all validators on the rendered SVG. Log each finding at WARNING. Return the list. Caller can ignore. |
| `"strict"` | Run all validators. Raise `ValidationError` if any findings; the exception's `.findings` attribute carries the full list. |
| `"off"` | Skip validation entirely. Return `[]`. |

`Canvas.validate()` runs the same checks against an in-memory render without writing to disk and returns the findings — useful for assertion-style gates.

The validators that run:

- **`text-overflow`** — every `<text>` bbox must sit inside at least one rect or diamond **in the same layer** (0.5 mm tolerance). The same-layer scope is intentional: text labels belong to their box's layer.
- **`arrow-tip-distance`** — every arrow tip must be within 0.6 mm of some target shape's edge **anywhere on the canvas** (any layer). The cross-layer scope is intentional: arrows commonly span layers (e.g. a connector layer pointing into a boxes layer).
- **`marker-orient`** — every `<marker>` must use `orient="auto"`.
- **`sibling-overlap`** — no two rects in the same non-background layer should overlap (use `validate_sibling_overlap(ignore_layers=...)` to whitelist additional layers).

Each `Finding` carries `category`, `message`, `element_id`, and `location` (mm). See `examples/validation_demo.py` for a runnable demonstration.

`svg-primitives` validation is complementary to the `[[figure-qa]]` agent: `figure-qa` validates any SVG (including hand-authored ones); this validates SVGs produced by this skill, in-process, before they hit disk.

## Composition into a panel

Once authored, the SVG is a panel source for `[[scientific-figure]]`:

```python
from compose import Figure

Figure(width_mm=183, height_mm=60, journal="nature") \
    .add_panel("schematic.svg", x_mm=0, y_mm=0, scale=1.0, label="A") \
    .add_panel("plot.svg", x_mm=92, y_mm=0, scale=0.5, label="B") \
    .save("figure.svg")
```

Schematics are typically sized at the **final** panel dimensions and composed at `scale=1.0` so labels stay at their authored size.

## Running the examples

```bash
uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools --with cairosvg \
  python plugins/figures/skills/svg-primitives/examples/eeg_pipeline.py
uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools --with cairosvg \
  python plugins/figures/skills/svg-primitives/examples/stress_test.py
```

Each writes `<file>.svg` and `<file>.png` into `examples/out/` (gitignored).

## Running the tests

The skill ships an E2E pytest suite that asserts text containment, arrow tip distance to target edges, marker orientation, layer paint order, per-color marker generation, font-size unit correctness, and Diamond text containment — all on real rendered SVGs parsed from disk. No mocks.

```bash
uv run --with pytest --with lxml --with svgelements --with svgpathtools \
    --with drawsvg --with Pillow --with fonttools --with cairosvg --with shapely \
    pytest plugins/figures/skills/svg-primitives/tests/ -v
```

Expected: all tests pass (50+ tests covering text containment, arrow geometry, layer order, validation errors, and Phase 2 primitives).

## Quality assurance

After authoring, run `[[figure-qa]]` for the standard pre-export font / palette / geometry checks:

```bash
uv run --with lxml --with svgelements --with svgpathtools --with shapely \
    python plugins/figures/agents/figure-qa-scripts/check_svg.py \
    schematic.svg --journal nature --palette okabe-ito
```

The geometry section (bbox-overlap, arrow-tip-to-target, text-overflow) landed via issue #47; the primitive-layer tests in this skill cover the same invariants for SVGs built from `svg_primitives`.

## Handoff to Illustrator or Affinity Designer

Canvas output is already close to the editor-safe dialect
(named `<g id="layer-...">` groups, origin-0 mm viewBox, single positioning, no data URIs).
Two constructs are intentionally kept editor-unfriendly in the master
because validation depends on them:
`<marker orient="auto">` arrowheads
and middle-anchored labels
(`LabeledBox`/`Pill`/`Diamond`/`Bracket` always center;
`Annotation` defaults to middle but is configurable).
When a figure goes to a human editor,
derive the handoff copy with the editor-prep pass
in the `[[svg-figure]]` skill's `scripts/editor_prep.py`,
which bakes markers into rotated geometry and resolves anchors to measured left edges.
The editor-handoff reference in `[[svg-figure]]` explains why.

## Additional resources

- `examples/eeg_pipeline.py` — canonical EEG preprocessing flowchart.
- `examples/stress_test.py` — edge cases (min-size, long labels, multi-line, crossing arrows, 6 pt vs 12 pt).
- `references/api.md` — full API reference.
- `references/design.md` — design rationale, library choices, convention notes.
- `references/font-metrics.md` — how fontTools advance widths feed the auto-fit logic, font search path, fallbacks.

## Cross-references

- `[[svg-figure]]` — hand-authored SVG patterns; reference material for writing SVG by hand or generating it ad-hoc.
- `[[scientific-figure]]` — multi-panel composer that loads SVGs produced here.
- `[[plot-styling]]` — data plots (matplotlib / seaborn / plotnine / plotly / PyVista).
- `[[ai-full-figure]]` — AI-generated pictorial substrate; overlay labels with `LabeledBox` / `Arrow` here.
- `[[transparent-icons]]` — flat scientific icons; place them inside a `LabeledBox` neighborhood with `Arrow.connect`.
- `[[figure-qa]]` — QA agent that validates the rendered SVG.

## Running in CI

`measure_text_mm` reads real font tables (fontTools/Pillow). A vanilla Linux CI container has no system fonts — install one before running the tests:

```bash
apt-get install -y fonts-liberation     # or fonts-dejavu-core
```

Without a system font, `measure_text_mm` falls back to a 0.55-em-per-character heuristic and logs a `WARNING`. Pass `strict_metrics=True` to `LabeledBox` to raise `MetricsFallbackError` instead — recommended for journal-submission workflows.
