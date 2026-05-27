# svg-primitives API reference

Full reference for the public API. Constructors, methods, and conventions.

## `Canvas(width_mm: float, height_mm: float, background: str | None = "#FFFFFF")`

The root drawing surface.

- `width_mm`, `height_mm` — physical dimensions in millimeters; emitted to the SVG `width="<W>mm"` and `height="<H>mm"` attributes and as the `viewBox`.
- `background` — fill color of the canvas background rect. Pass `None` to omit the background rect entirely (useful when composing into a parent figure).

**Methods**

- `layer(name: str) -> Layer` — gets the named layer, creating it on first access. Layer paint order = first-registration order.
- `add_layer(layer: Layer) -> Canvas` — explicit insertion; returns self for chaining.
- `save(path: str | Path, output_png: bool = False, png_width: int = 1800) -> None` — writes the SVG. With `output_png=True`, also writes a sibling PNG via cairosvg (requires cairosvg).
- `to_drawsvg() -> drawsvg.Drawing` — emit the drawsvg tree without saving; useful for tests.

## `Layer(name: str)`

An ordered bucket of elements.

- `add(element) -> element` — append the element; returns it so calls can chain (`b = layer.add(LabeledBox(...))`).

## `LabeledBox(x, y, text, font_size=7, padding=2, ...)`

Auto-sized rounded rectangle with centered text.

**Constructor parameters**

| Name | Default | Description |
| --- | --- | --- |
| `x`, `y` | required | Top-left corner (mm) when `anchor="top-left"`, centroid when `anchor="center"`. |
| `text` | required | Label content. Use `\n` for line breaks. |
| `font_size` | `7.0` | Font size in **pt**. Emitted SVG `font-size` is in mm. |
| `padding` | `2.0` | Inset on each side (mm). |
| `min_width`, `min_height` | `0.0` | Lower bounds for the auto-sized rect. |
| `fill` | `"#F4F1DE"` | Box fill. |
| `stroke` | `"#1F3A5F"` | Box stroke and text color. |
| `stroke_width` | `0.6` | Box stroke width (mm). |
| `rx` | `1.5` | Corner radius (mm). |
| `anchor` | `"top-left"` | Anchor convention: `"top-left"` or `"center"`. |
| `line_spacing` | `1.2` | Inter-line spacing for multi-line text (em). |
| `font_path` | `None` | Optional explicit font file. Overrides the search path. |
| `strict_metrics` | `False` | If `True`, raise `MetricsFallbackError` instead of using the 0.55-em heuristic when no font is found. |

**Computed attributes** (read after construction)

- `width`, `height` — final mm dimensions.
- `left`, `right`, `top`, `bottom`, `cx`, `cy` — bounding box and centroid.

**Methods**

- `anchor_point(side: "N"|"S"|"E"|"W") -> complex` — anchor on the requested side.
- `outline_path() -> svgpathtools.Path` — sharp-corner outline used by `Arrow.connect` for edge snapping.
- `to_drawsvg() -> drawsvg.Group` — emit the SVG group containing rect + text.

**Class method**

- `LabeledBox.next_to(other: LabeledBox, side: "N"|"S"|"E"|"W", gap: float, **kwargs) -> LabeledBox` — build a new box positioned relative to `other`. `gap` is the spacing between touching edges (mm). Rejects `anchor="center"` in kwargs — placement is always by top-left of the new box.

**Validation**

`LabeledBox.__post_init__` raises `ValueError` for: non-positive `font_size`, negative `padding`, or `anchor` not in `("top-left", "center")`.

## `Pill(...)` and `Diamond(...)`

Subclasses of `LabeledBox` with different geometry.

- `Pill` — `rx` is overridden to `height/2` after auto-sizing → flat-sided capsule. Useful for terminal "start"/"end" nodes.
- `Diamond` — rhombus. The auto-sized width and height are doubled after the text-fit pass so the inscribed text rectangle still fits without overlap. The outline is a four-edge polygon emitted as a closed SVG `<path d="M ... Z"/>`.

## `Arrow.connect(src, dst, *, curve="straight", bow=0, src_side="auto", dst_side="auto", via=None, corner_radius=0.0, stroke, stroke_width) -> Arrow`

Connector between two shapes.

| Name | Default | Description |
| --- | --- | --- |
| `src`, `dst` | required | Two `Shape` instances — `LabeledBox`, `Pill`, `Diamond`, `Group`. |
| `curve` | `"straight"` | `"straight"` line, `"cubic"` Bezier, `"orthogonal-h"` right-angle horizontal-first, `"orthogonal-v"` right-angle vertical-first. |
| `bow` | `0.0` | Cubic only: perpendicular bulge in mm. Positive = upward in SVG y, negative = downward. The sign is normalized regardless of chord direction. |
| `src_side`, `dst_side` | `"auto"` | Anchor sides. `"auto"` picks the side facing the other endpoint (or the side on the primary axis for orthogonal modes). |
| `via` | `None` | Straight curve only. List of `(x, y)` waypoints the polyline passes through between `src` and `dst`. |
| `corner_radius` | `0.0` | When > 0, interior polyline corners are replaced with quadratic Beziers of that radius, clamped to half the shorter adjoining segment. |
| `stroke` | `"#1F3A5F"` | Arrow color. The Canvas generates one `<marker>` per unique stroke color. |
| `stroke_width` | `0.6` | Stroke width (mm). |

**Validation**

`Arrow.connect` raises `ValueError` if `src` and `dst` resolve to coincident anchor points (e.g. `Arrow.connect(box, box, src_side="N", dst_side="N")`). Use different sides or non-overlapping boxes. Also raises on unsupported `curve` values.

**Returned object**

- `Arrow.d` — SVG path "d" attribute (string).
- `Arrow.stroke`, `.stroke_width` — as constructed.
- `Arrow.to_drawsvg() -> drawsvg.Path` — rendered path with `marker-end` set.

## `Bracket(start, end, depth, label=None, label_offset=2, ...)`

Square-style bracket ("rake") whose spine sits `depth` mm perpendicular to the line from `start` to `end`. The optional `label` is centered at the spine apex `label_offset` mm further out on the closed side of the bracket (same direction as the spine offset, regardless of sign).

| Name | Default | Description |
| --- | --- | --- |
| `start`, `end` | required | `(x, y)` tuples in mm. |
| `depth` | required | Mm offset of the spine perpendicular to start-end. Sign chooses side. |
| `label` | `None` | Optional text at the spine apex. |
| `label_offset` | `2.0` | Mm further out from the spine to the label. |
| `font_size`, `font_path`, `strict_metrics` | as `LabeledBox` | Text metrics conventions. |
| `stroke`, `stroke_width` | `"#1F3A5F"`, `0.6` | Outline. |

Raises `ValueError` on non-positive `font_size`.

## `Annotation(x, y, text, leader_to=None, ...)`

Text label at `(x, y)` with an optional thin leader line to a target coordinate.

| Name | Default | Description |
| --- | --- | --- |
| `x`, `y` | required | Text anchor (mm). |
| `text` | required | Label content. |
| `leader_to` | `None` | Target `(x, y)` for an optional leader line. Omitted means text-only. |
| `text_anchor` | `"middle"` | SVG text-anchor: `"start"`, `"middle"`, `"end"`. |
| `leader_gap` | `1.0` | Mm gap between text bbox and leader start so the line does not overlap the text. |
| `leader_stroke`, `leader_stroke_width` | `"#1F3A5F"`, `0.3` | Leader-line styling. |
| `fill`, `font_size`, `font_path`, `strict_metrics` | conventional | Text styling and metrics. |

## `Group(*shapes) -> Group`

Virtual container exposing the union-bbox geometry of its member shapes through the `Shape` protocol. Not added to a layer; not rendered.

| Member | Description |
| --- | --- |
| `members` | Tuple of the grouped shapes. |
| `left`, `right`, `top`, `bottom`, `cx`, `cy`, `width`, `height` | Union-bbox metrics (read-only properties). |
| `anchor_point(side)` | Cardinal anchor on the union bbox edge. |
| `outline_path()` | `svgpathtools.Path` rectangle around the union bbox. |

`Group()` with no members raises `ValueError`.

## `Shape` Protocol

Minimal geometry contract that `Arrow.connect` and other connectors rely on. Anything with `cx`, `cy`, `anchor_point(side) -> complex`, and `outline_path() -> Path` satisfies the protocol. `LabeledBox`, `Pill`, `Diamond`, and `Group` all do.

The arrowhead is delivered by the Canvas-generated `<marker orient="auto">`; the SVG renderer computes the tangent at the terminal point and rotates the marker, so curved-path arrowheads stay tangent-correct.

## Validation summary

| Type | Constructor raises `ValueError` for |
| --- | --- |
| `Canvas` | non-positive `width_mm` or `height_mm` |
| `Canvas.add_layer` | duplicate `layer.name` (use `Canvas.layer(name)` to get-or-create) |
| `LabeledBox` (and subclasses) | non-positive `font_size`, negative `padding`, anchor not in `("top-left", "center")` |
| `LabeledBox.next_to` | `anchor="center"` in kwargs (placement is by top-left) |
| `Arrow.connect` | coincident `src`/`dst` anchor points |
| `Arrow.connect` | unsupported `curve` value (only `"straight"` and `"cubic"` are accepted) |

`MetricsFallbackError` (subclass of `RuntimeError`) is raised when `strict_metrics=True` and no exact font-metric backend succeeds.

## Conventions

- **Units**: user units = mm everywhere except `font_size` (pt). Font size emitted as `<text font-size>` in mm.
- **Bow sign**: positive = upward in SVG (negative y), negative = downward, regardless of chord direction.
- **Layer order**: first-registration order = paint order.
- **Color model**: hex strings (`"#1F3A5F"`); near-grays (`#888`, `#999`, `#ccc`) are exempt from QA palette compliance.
