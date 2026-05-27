# svg-primitives design rationale

## Why a new skill rather than extending `svg-figure`?

`svg-figure` is intentionally **library-agnostic**: it documents how to write an SVG schematic by hand (or with any library), with conventions for sizing, palette, text alignment, arrow patterns, and z-order. That's the right reference material for ad-hoc work and for understanding the constraints the figure-qa agent enforces.

`svg-primitives` is the **opinionated programmatic path**. It picks one library stack and provides primitives that make the conventions in `svg-figure` true by construction — text alignment is no longer "make sure your text-anchor and x are right," it's `LabeledBox(text="…")` and the math is done for you.

Both ship; both are useful. `svg-figure`'s SKILL.md links to this skill as the recommended programmatic path.

## Why drawsvg + svgpathtools + fontTools?

Surveyed in Phase 0 (`.context/figures-svg-primitives.md` on the epic branch). Summary of the choice:

- **drawsvg** (MIT, active 2026) — clean Python API for emitting SVG, supports `<marker orient="auto">`, mm-precise user units. Foundation.
- **svgpathtools** (MIT, active 2025) — exposes `Path.intersect`, `Path.unit_tangent`, `bez.cropped(t0, t1)`. Solves the geometry problems we need: edge snapping (where does this line cross this rect?) and cubic trimming (cut a Bezier between two t parameters).
- **fontTools** (MIT, vendored everywhere) — reads font tables directly. We compute width as `sum(hmtx[cmap[ord(c)]].advance) / unitsPerEm * em_mm`, which is exact for any TTF/OTF, platform-neutral, and doesn't require Pillow.

Disqualified candidates:

- **Graphviz, diagrams, Mermaid** — auto-layout; lose mm-precision. Hard "no" for journal panels.
- **schemdraw.flow** — has anchor-snap connectors and auto-expanding boxes, but boxes are NOT auto-fit (each `w=…` is hand-tuned), feedback wires render Manhattan-style, and the default style is circuit-schematic.
- **PyX** — TeX-based, exact metrics, but archaic API and TeX dependency.
- **svgwrite** — archived 2024.

## Why `font_size` in pt?

Journal style guides specify font sizes in pt ("Figure labels should be ≥7 pt in the final printed size"). Accepting `font_size=7` and emitting `font-size="2.469"` in mm internally is the smallest interface that matches how authors think while preserving mm-precise rendering.

## Why `bow > 0 = up`?

For a horizontal arrow going right-to-left or left-to-right, "above the chord" is the intuitive interpretation of a positive bow value. The implementation normalizes the perpendicular vector so this convention holds regardless of chord direction (vertical chords, diagonal chords, etc.). This avoids the "why is my feedback arrow bowing into the boxes" problem from the Phase 0 prototype.

## Why per-color markers?

A single hardcoded blue marker means red arrows get blue arrowheads — a frequent visual bug in hand-authored figures. The Canvas collects all unique arrow stroke colors at render time and generates one `<marker>` per color with the triangle fill matching the stroke. The Arrow elements get rewritten to reference their color's marker.

## Why named layers instead of explicit z-index?

SVG has no z-index in the conformance sense; paint order = document order. A `Layer` abstraction makes the intended order explicit (`background → connectors → boxes → labels`) and lets you add elements to any layer in any order during the build — the Canvas flushes them in registration order at save time. This eliminates the "I added the arrow after the box so it's on top" class of bugs.

## What's intentionally NOT in Phase 1

- **Orthogonal/Manhattan routing** — comes in Phase 2 along with brackets, group anchors, and multi-waypoint paths.
- **Auto-layout** — never, for journal-precision reasons. Use `elkjs` or Graphviz externally if you need it, then place results manually.
- **Animation** — out of scope; this is for static figures.
- **Validation gates in Canvas.save()** — Phase 3 will wire `figure-qa`'s SVG checks in via a `validate="warn"|"strict"|"off"` parameter once #47 lands.

## Testing philosophy

E2E tests render real SVGs into pytest's `tmp_path` and parse them back from disk. No mocks. No headless browser. The reasoning:

- The primitive layer's job is to emit correct SVG; the test should verify what we actually emitted.
- Geometric invariants (text contained in box, arrow tip on edge, marker orientation) are checkable from SVG attributes + svgpathtools — no rasterizer needed.
- A real SVG parse exercises the actual code path users will hit when their SVG is loaded by `scientific-figure/compose.py` or `figure-qa/check_svg.py`.

The tolerance choices (0.5 mm for text containment, 0.6 mm for arrow tip) account for the difference between the box's rounded corners (rx=1.5 mm rendered shape) and the sharp-corner outline path used internally for snapping. They are tight enough that visible misalignment fails.
