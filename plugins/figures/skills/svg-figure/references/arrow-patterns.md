# Arrow Patterns

> Hand-authoring recipes for SVG arrows. `[[svg-primitives]]`'s `Arrow.connect(curve='straight'|'cubic'|'orthogonal-h'|'orthogonal-v')` produces these patterns mechanically — read this document when authoring SVG by hand or when debugging arrow geometry in SVG produced by another tool.

Recipes for arrows in SVG schematics that the `figure-qa` agent validates (arrow-tip-to-target distance, issue #47) and that render correctly across all common SVG renderers (Inkscape, Chrome, Firefox, Safari, librsvg, cairosvg).

## The marker definition

Every arrow shares a single marker definition placed inside `<defs>` at the top of the SVG:

```svg
<defs>
  <marker id="arrow" viewBox="0 0 10 10"
          refX="9" refY="5"
          markerWidth="3" markerHeight="3"
          orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#1F3A5F"/>
  </marker>
</defs>
```

Key parameters:

- **`refX="9"`** places the marker's reference point one unit before the triangle's tip (the tip is at `x=10`). The line's endpoint `x2,y2` aligns with this reference, so the visual tip lands exactly at the target coordinate.
- **`markerWidth="3" markerHeight="3"`** sets the rendered size of the marker. In our mm-viewBox SVG, this means a 3 mm × 3 mm arrowhead at scale 1, which sits well alongside ~1 mm strokes. Scale with stroke weight (~3-4× stroke width is a good rule); `markerWidth="6"` is usually too large.
- **`orient="auto-start-reverse"`** rotates the marker along the path tangent at the endpoint. The `-reverse` variant lets the same marker serve `marker-start` and `marker-end` correctly. (Older renderers may not support `-reverse`; if you support Inkscape pre-1.0, also define `arrow-start` separately.)
- **`fill="#1F3A5F"`** matches the line color. SVG markers do not inherit `stroke` from the parent path, so set the fill explicitly.

For multi-color arrow heads (e.g., a process-flow arrow color-coded by step), define one marker per color:

```svg
<marker id="arrow-blue" ...><path d="M 0 0 L 10 5 L 0 10 z" fill="#0072B2"/></marker>
<marker id="arrow-orange" ...><path d="M 0 0 L 10 5 L 0 10 z" fill="#D55E00"/></marker>
```

## Recipe 1: straight arrow between two boxes

The simplest pattern — a `<line>` with the endpoint exactly on the target's edge.

```svg
<rect id="src" x="10" y="10" width="30" height="14" fill="#F4F1DE" stroke="#1F3A5F" stroke-width="0.8" rx="1.5"/>
<rect id="dst" x="60" y="10" width="30" height="14" fill="#F4F1DE" stroke="#1F3A5F" stroke-width="0.8" rx="1.5"/>

<!-- arrow: src.right (x=40) to dst.left (x=60), centered vertically (y=17) -->
<line x1="40" y1="17" x2="60" y2="17"
      stroke="#1F3A5F" stroke-width="0.8" marker-end="url(#arrow)"/>
```

QA check the geometry section runs: the tip of the arrow (`x2, y2`) must be within tolerance of the target shape's edge. For the source side, `marker-start="url(#arrow)"` mirrors the same logic.

## Recipe 2: curved arrow (cubic Bezier)

Use when boxes aren't horizontally aligned and a straight line would clip through other nodes.

```svg
<path d="M 40 17 C 47 17, 47 30, 60 30"
      fill="none" stroke="#1F3A5F" stroke-width="0.8"
      marker-end="url(#arrow)"/>
```

Cubic Bezier with start `(40,17)`, first control `(47,17)`, second control `(47,30)`, end `(60,30)`. The two control points share x=47 so the curve enters and leaves with horizontal tangents — visually smooth.

For the QA agent's tangent calculation, `svgpathtools.Path(...).unit_tangent(1)` gives the unit vector at the endpoint, which the agent uses to verify the arrow head orients correctly toward the target.

## Recipe 3: orthogonal (right-angle) arrow

Common in flow charts and engineering diagrams. Avoid a single `<path>` with sharp corners and the `marker-end` placed wrong; use a multi-segment polyline with the arrow on the final segment:

```svg
<polyline points="40,17 50,17 50,40 60,40"
          fill="none" stroke="#1F3A5F" stroke-width="0.8"
          marker-end="url(#arrow)"/>
```

The marker is placed on the final segment by `marker-end` (the SVG spec applies markers per-segment when `marker-mid` is also set; without `marker-mid`, only the first and last vertices receive markers). The final segment runs left-to-right toward `(60,40)`, and `orient="auto"` rotates the marker to match.

## Recipe 4: bidirectional arrow

Two markers, one on each end:

```svg
<line x1="40" y1="17" x2="60" y2="17"
      stroke="#1F3A5F" stroke-width="0.8"
      marker-start="url(#arrow)" marker-end="url(#arrow)"/>
```

With `orient="auto-start-reverse"` on the marker definition, the start marker is rotated 180° so the head points outward from the line's start.

## Recipe 5: dashed connection (e.g., regulatory or weak association)

Use `stroke-dasharray` on the path; the marker renders the same regardless:

```svg
<line x1="40" y1="17" x2="60" y2="17"
      stroke="#1F3A5F" stroke-width="0.8"
      stroke-dasharray="2 1"
      marker-end="url(#arrow)"/>
```

`stroke-dasharray="2 1"` is 2 mm dash, 1 mm gap. Adjust to taste; keep the dash pattern consistent across all dashed lines in the same figure.

## Common failure modes

| Failure | Cause | Fix |
|---|---|---|
| Arrow head overshoots the target shape | `refX` set to 5 (center of the 0-10 viewBox triangle) | Set `refX="9"` so the tip is the reference point |
| Arrow head misaligned with the line direction | `orient` omitted (defaults to 0°) | Set `orient="auto"` or `orient="auto-start-reverse"` |
| Arrow appears in the wrong color | `<marker>` inherits stroke but not fill from the line | Set `fill="<color>"` explicitly on the marker's `<path>` |
| Arrow head fills entire screen | `markerUnits="userSpaceOnUse"` accidentally set | Default `markerUnits="strokeWidth"` is what you want, or omit entirely |
| Arrow head is invisible after Inkscape export | Older Inkscape stripped `auto-start-reverse` | Define a separate `arrow-start` marker without `-reverse` and use both |
| Curve tangent at endpoint doesn't match arrow orientation | Bezier control points produce a different exit angle | Adjust the second control point to share x or y with the endpoint (forces horizontal/vertical tangent) |

## Tip-to-target tolerance for QA

The QA agent's geometry section computes the distance from the arrow's endpoint to the nearest target shape's bounding box and flags any arrow with distance > 1 mm. To stay within tolerance:

- Set arrow endpoints to exactly the target's edge coordinate.
- For rounded rectangles, use the straight-edge coordinate (not the curve). A `<rect>` with `rx="1.5"` has straight horizontal edges between `x` and `x + width` from `y + rx` to `y + height - rx`; aim the arrow at any y in that range.
- For circles, use `cx ± r` for horizontal arrows or `cy ± r` for vertical. For arbitrary angles, parametrize the edge: `(cx + r * cos(θ), cy + r * sin(θ))`.
