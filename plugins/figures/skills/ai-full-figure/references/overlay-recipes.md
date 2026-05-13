# Overlay Recipes

How to place labels, arrows, and scale bars on top of an AI-generated substrate so the final SVG is composable by `[[scientific-figure]]` and verifiable by the `[[figure-qa]]` agent.

## The output SVG shape

`overlay_labels.py` emits:

```svg
<svg width="89mm" height="50.06mm" viewBox="0 0 1920 1080">
  <defs>
    <marker id="overlay-arrow" ...>
  </defs>
  <image href="data:image/png;base64,..." x="0" y="0" width="1920" height="1080"/>
  <text .../>     <!-- label 1 -->
  <line .../>     <!-- arrow 1 -->
  <text .../>     <!-- label 2 -->
  <g class="scale-bar">...</g>
</svg>
```

Key design choices:

- **viewBox uses substrate pixels.** Every label coordinate is addressed in the substrate's native pixel grid. No coordinate transform between "where I see this in the image viewer" and "where I write this in the JSON."
- **width/height use mm.** The composer can place this SVG at the target physical size without rescaling the substrate or the labels.
- **Substrate is base64-embedded.** The SVG is self-contained — no external file references — so it composes correctly when the panel is moved between machines.
- **Labels carry a white stroke under the text** (`stroke="white" stroke-width="2" paint-order="stroke"`). This makes text legible against any substrate without requiring background detection.

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

The label sits at `(900, 200)`. The arrow head lands at `(760, 380)` — the actual cortex location. The leader keeps the label out of the visual area.

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

The scale-bar line is at `y=950`; the caption sits 8 px above. Position bars near a corner — typically bottom-left or bottom-right — so they don't compete with the subject.

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

Keep label `font_size_pt` consistent across the set (8 pt is a good default for poster-scale; 10 pt for slide-scale). The `figure-qa` SVG branch's font check uses the journal minimum, so 5 pt is the absolute floor.

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

When labels are eyeballed rather than data-driven:

1. Open the substrate PNG in any image viewer (Preview on macOS, `xdg-open` on Linux).
2. Hover the cursor over each anatomical feature; note the (x, y) pixel coordinates from the viewer's status bar.
3. Add a 40–80 px offset for the label position to keep the text out of the feature.
4. Write the label with `arrow_to` pointing at the original feature coordinate.

For features that are obvious from context (no leader needed), skip `arrow_to` — the text sits at its `(x, y)` without a connector.

## Working around substrate hot spots

White text on a near-white substrate, or dark text on a dark substrate, becomes invisible. The default overlay paints a white stroke under the text via `paint-order="stroke"`. To customize for a substrate where white doesn't read well:

```json
{"text": "...", "x": ..., "y": ..., "color": "#FFFFFF",
 "stroke_under": "#000000"}
```

(The shipped `_label_svg` always uses a 2-px white stroke; if you need black-on-dark with a colored halo, edit `overlay_labels.py` or write the SVG `<text>` directly.)

## Composing into a multi-panel figure

The overlay SVG is a valid panel source for `[[scientific-figure]]`:

```python
from compose import Figure

Figure(width_mm=183, height_mm=100, journal="nature") \
    .add_panel("panels/methods.svg", x_mm=0, y_mm=0, scale=1.0, label="A") \
    .add_panel("out/brain_labeled.svg", x_mm=92, y_mm=0, scale=1.0, label="B") \
    .save("figure.svg")
```

The labeled SVG carries its own `width="89mm"` from the overlay step; the composer respects that.

## Quality check

After overlay, the figure-qa agent's SVG branch will report:

- Font sizes vs journal minimum (delegated to `validate_fonts.py`).
- Palette compliance for label colors (set `--palette okabe-ito` or your project's allow-list).
- Geometry counts; the raster substrate counts as one `<image>` element.

The agent's raster branch should also be run on the substrate itself (before overlay) to verify DPI and dominant colors:

```bash
uv run --with pillow --with colorthief python "$FIGURE_QA_SCRIPTS/check_raster.py" out/substrate.png --journal nature
```

This catches substrates that were generated at too-low resolution for the target physical size before they ship in a figure.
