"""EEG preprocessing flowchart — canonical example for the svg-primitives skill.

Exercises:
  - short, long, and multi-line labels (auto-fit widths)
  - straight forward arrows
  - a cubic feedback arrow in a second color
  - a horizontal grid line that visibly passes UNDER the boxes (z-order)

Run from the skill's `scripts/` directory:

    cd plugins/figures/skills/svg-primitives/scripts
    uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools --with cairosvg \\
      python ../examples/eeg_pipeline.py

Output is written to `<this-file's-dir>/out/eeg_pipeline.svg` and `.png`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the scripts/ dir (sibling of examples/) to sys.path so the svg_primitives
# package is importable when this file is run directly.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import drawsvg as dw  # noqa: E402

from svg_primitives import Arrow, Canvas, LabeledBox  # noqa: E402


def build() -> Canvas:
    """Build the EEG preprocessing flowchart Canvas. Return the unsaved Canvas
    so tests can also assert on the in-memory model."""
    canvas = Canvas(width_mm=180, height_mm=80)

    pad = 2.0
    fs = 7.0  # pt
    raw = LabeledBox(x=8, y=20, text="Raw EEG", padding=pad, font_size=fs)
    band = LabeledBox.next_to(raw, side="E", gap=10, text="Bandpass\nfilter", padding=pad, font_size=fs)
    ica = LabeledBox.next_to(band, side="E", gap=10, text="Independent component\nanalysis", padding=pad, font_size=fs)
    rej = LabeledBox.next_to(ica, side="E", gap=10, text="Artifact\nrejection", padding=pad, font_size=fs)
    epoch = LabeledBox.next_to(rej, side="E", gap=10, text="Epoching", padding=pad, font_size=fs)

    # Forward path.
    forward = [
        Arrow.connect(raw, band, curve="straight"),
        Arrow.connect(band, ica, curve="straight"),
        Arrow.connect(ica, rej, curve="straight"),
        Arrow.connect(rej, epoch, curve="straight"),
    ]
    # Feedback: rejection -> ICA decomposition, looping over the row.
    feedback = Arrow.connect(
        rej, ica, curve="cubic", src_side="N", dst_side="N", bow=14,
        stroke="#C45146",
    )

    # Decorative grid line at y=27 (will sit under boxes thanks to layer order).
    grid = dw.Line(4, 27, 176, 27, stroke="#CCCCCC", stroke_width=0.3, stroke_dasharray="1,1")

    bg = canvas.layer("background"); bg.add(grid)
    arrows_layer = canvas.layer("connectors")
    for a in forward + [feedback]:
        arrows_layer.add(a)
    boxes_layer = canvas.layer("boxes")
    for b in (raw, band, ica, rej, epoch):
        boxes_layer.add(b)
    return canvas


def main() -> Path:
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    svg_path = out_dir / "eeg_pipeline.svg"
    build().save(svg_path, output_png=True, png_width=1800)
    print(f"wrote {svg_path} and {svg_path.with_suffix('.png')}")
    return svg_path


if __name__ == "__main__":
    main()
