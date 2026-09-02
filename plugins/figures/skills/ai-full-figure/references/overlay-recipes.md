# Overlay Recipes

How to place labels, arrows, and scale bars on top of an AI-generated substrate, so the final SVG is composable by `figures:scientific-figure` (invoke with the Skill tool) and verifiable by `figures:figure-qa` (invoke with the Skill tool).

This is rung 2 of the text ladder described in `prompt-patterns.md`: use overlay for dense labels, leader-line annotations, scale bars, and anything that must be edited later without a full regeneration.

## The output SVG shape

`overlay_labels.py` emits:

```svg
<svg width="89mm" height="50.06mm" viewBox="0 0 1024 576">
  <defs>
    <marker id="overlay-arrow-1f3a5f" ...>
  </defs>
  <image href="data:image/png;base64,..." x="0" y="0" width="1024" height="576"/>
  <text .../>     <!-- label 1 -->
  <line .../>     <!-- arrow 1 -->
  <text .../>     <!-- label 2 -->
  <g class="scale-bar">...</g>
</svg>
```

Key design choices:

- **viewBox uses substrate pixels.** Every label coordinate is addressed in the substrate's native pixel grid. There is no coordinate transform between "where I see this in the image" and "where I write this in the JSON."
- **width/height use mm.** The composer can place this SVG at the target physical size without rescaling the substrate or the labels.
- **Substrate is base64-embedded.** The SVG is self-contained; there are no external file references, so it composes correctly when the panel is moved between machines.
- **Labels carry a configurable legibility halo under the text** (`stroke` set to `stroke_under` or white by default, `paint-order="stroke"`). This makes text legible against any substrate without requiring background detection.
- **One `<marker>` per distinct color**, named `overlay-arrow-<hex>` where `<hex>` is the lowercased, `#`-stripped stroke color (for example `overlay-arrow-1f3a5f` for the default `#1F3A5F`). Arrowheads and their line always match because the marker id is derived from the color, not a fixed literal.

### Font size and stroke width are physical points, not raw pixels

The document root declares a physical width in millimeters (`width="89mm"`) over a pixel `viewBox`. A bare (unitless) SVG `font-size` or `stroke-width` number is one user unit per viewBox pixel, not one point; writing `font_size_pt: 8` directly as `font-size="8"` under a 1024 px viewBox at 89 mm rendered at roughly 2.5 pt, well under every documented journal minimum. This is what `figures:scientific-figure`'s `validate_fonts.py` computes as `_root_unit_to_pt`: points per user unit equal `(width_mm * 72 / 25.4) / viewbox_width`.

`overlay_labels.py` now inverts that formula once per document:

```
units_per_pt = viewbox_width / (width_mm * 72 / 25.4)
```

and multiplies every pt-denominated value by it before writing the bare SVG number: `font_size_pt`, the arrow stroke width, the scale-bar stroke width, and the text legibility halo stroke width. A label written with `font_size_pt: 8` now measures 8 pt when read back by `validate_fonts.py`, regardless of the substrate's pixel resolution or the chosen `--width-mm`.

## Recipe 1: leader-line label

A label some distance from its target, with a thin arrow pointing at the feature:

```bash
overlay_labels.py substrate.png \
  --label "primary motor cortex@900,200" \
  -o out/labeled.svg
```

Or programmatically via JSON:

```json
{
  "labels": [
    {"text": "primary motor cortex", "x": 900, "y": 200,
     "arrow_to": [760, 380], "color": "#1F3A5F", "font_size_pt": 10}
  ]
}
```

The label sits at `(900, 200)`. The arrow head lands at `(760, 380)`, the actual cortex location. The leader keeps the label out of the visual area.

## Recipe 2: scale bar

```bash
overlay_labels.py substrate.png \
  --scale-bar "1 cm@200,950" \
  -o out/labeled.svg
```

Default length is 80 pixels; customize via JSON:

```json
{
  "scale_bars": [
    {"text": "1 cm", "x": 200, "y": 950, "length_px": 120, "color": "#000000"}
  ]
}
```

The scale-bar line is at `y=950`; the caption sits 8 px above. Position bars near a corner, typically bottom-left or bottom-right, so they do not compete with the subject.

## Recipe 3: multi-label dense overlay (anatomical figure)

When the substrate has many points to label, write a JSON config rather than repeated `--label` flags:

```json
{
  "width_mm": 150,
  "labels": [
    {"text": "occipital", "x": 1200, "y": 600, "arrow_to": [1050, 540]},
    {"text": "parietal", "x": 1000, "y": 200, "arrow_to": [900, 380]},
    {"text": "frontal", "x": 400, "y": 200, "arrow_to": [500, 380]},
    {"text": "temporal", "x": 400, "y": 700, "arrow_to": [550, 600]},
    {"text": "cerebellum", "x": 1200, "y": 850, "arrow_to": [1050, 750]}
  ]
}
```

Choose `font_size_pt` from the journal minimum plus headroom, not from a flat rule of thumb; `validate_fonts.py`'s per-journal floor is 5 pt for Nature and generic, 6 pt for Science, Cell, and PNAS. Because `font_size_pt` is now a true physical point size, a submission-bound overlay should sit at least 1 to 2 pt above that floor (6 to 8 pt for Nature, 7 to 9 pt for Science/Cell/PNAS) so a later crop or rescale does not push it back under the minimum. Poster- and slide-scale overlays are not journal-constrained; pick a size for the intended viewing distance instead (roughly 12 to 18 pt for an A0 poster viewed from 1 to 2 m, 18 to 28 pt for a projected slide). Keep `font_size_pt` consistent across one label set regardless of the scale you choose.

## Recipe 4: programmatic label placement (data-driven)

Most useful when the substrate is a fixed canvas (e.g., a brain atlas) and labels correspond to ROI coordinates from a CSV. Build the labels list in Python:

```python
import csv, json
labels = []
with open("rois.csv") as f:
    for row in csv.DictReader(f):
        labels.append({
            "text": row["name"],
            "x": float(row["px_x"]) + 60,  # offset right
            "y": float(row["px_y"]) - 40,  # offset up
            "arrow_to": [float(row["px_x"]), float(row["px_y"])],
            "font_size_pt": 8,
            "color": "#1F3A5F",
        })
json.dump({"width_mm": 100, "labels": labels}, open("labels.json", "w"))
```

Then run the overlay once with `--labels-file labels.json`.

## Coordinate-finding workflow

When labels are eyeballed rather than data-driven, do not hover a cursor over the substrate in an image viewer to read pixel coordinates; that workflow does not work for an agent without a display, and it is slow even at a keyboard. Instead, generate a grid overlay and read coordinates from it directly:

```bash
overlay_labels.py substrate.png -o out/labeled.svg --grid
```

This writes a sibling `out/labeled.grid.png` with a red 100 px grid and `x,y` coordinate labels burned into the image at every grid intersection. Read that PNG (the Read tool renders it as pixels) to pick each feature's approximate `(x, y)`, refine within the nearest 100 px cell by proportion, then:

1. Add a 40 to 80 px offset for the label position, to keep the text out of the feature.
2. Write the label with `arrow_to` pointing at the original feature coordinate.
3. Re-run `overlay_labels.py` and re-read the grid PNG (or the composed SVG) to confirm placement; iterate rather than guessing twice.

For features that are obvious from context (no leader needed), skip `arrow_to`; the text sits at its `(x, y)` without a connector.

## Working around substrate hot spots

White text on a near-white substrate, or dark text on a dark substrate, becomes invisible. The default overlay paints a white legibility halo under the text via `paint-order="stroke"`. `overlay_labels.py` reads a `stroke_under` key directly, so a substrate where white does not read well needs no code changes:

```json
{"text": "...", "x": 400, "y": 300, "color": "#FFFFFF",
 "stroke_under": "#000000"}
```

`stroke_under` is honored on both `labels` and `scale_bars` entries.

## Composing into a multi-panel figure

The overlay SVG is a valid panel source for `figures:scientific-figure` (invoke with the Skill tool):

```python
from compose import Figure

Figure(width_mm=183, height_mm=100, journal="nature") \
    .add_panel("panels/methods.svg", x_mm=0, y_mm=0, scale=1.0, label="A") \
    .add_panel("out/brain_labeled.svg", x_mm=92, y_mm=0, scale=1.0, label="B") \
    .save("figure.svg")
```

The labeled SVG carries its own `width="89mm"` from the overlay step; the composer respects that.

## Quality check

Invoke `figures:figure-qa` (with the Skill tool) after overlay. Its SVG branch reports:

- Font sizes vs. the journal minimum, now measured correctly because the overlay emits true physical points (see "Font size and stroke width are physical points, not raw pixels" above).
- Palette compliance for label colors (pass `--palette theme.json` or `--palette okabe-ito`).
- Geometry counts; the raster substrate counts as one `<image>` element.

The raster branch should also run on the substrate itself (before overlay) to verify DPI and dominant colors. Locate the helper scripts the same way `figure-qa-procedure.md` does, do not hardcode a path:

```bash
SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/agents/figure-qa-scripts"
if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] || ! test -d "$SCRIPTS_DIR"; then
    SCRIPTS_DIR="$(find . -type d -name figure-qa-scripts -path '*/figures/agents/*' 2>/dev/null | head -1)"
fi
uv run --with pillow --with pytesseract python "$SCRIPTS_DIR/check_raster.py" out/substrate.png --journal nature
```

This catches substrates that were generated at too-low resolution for the target physical size before they ship in a figure.
