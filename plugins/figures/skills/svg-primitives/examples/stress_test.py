"""Stress-test the svg-primitives layer with edge cases.

Covers:
  - Single-character label (smallest possible auto-fit)
  - 45-character single-line label (no overflow)
  - Three-line stacked label
  - min_width / min_height enforcement with short text
  - 6 pt vs 12 pt rendered side by side
  - Two crossing cubic arrows in different colors
  - A vertical S-curve arrow with bow

Run:

    uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools --with cairosvg \\
      python plugins/figures/skills/svg-primitives/examples/stress_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import drawsvg as dw  # noqa: E402

from svg_primitives import Arrow, Canvas, LabeledBox  # noqa: E402


def build() -> Canvas:
    canvas = Canvas(width_mm=120, height_mm=100)

    short = LabeledBox(x=5, y=5, text="A", padding=2, font_size=7)
    long_one_line = LabeledBox(
        x=20, y=5, text="Extremely long label that should not overflow",
        padding=2, font_size=7,
    )
    multi = LabeledBox(
        x=5, y=22, text="Line one\nLine two\nLine three", padding=2, font_size=7,
    )
    chunky = LabeledBox(
        x=60, y=22, text="X", padding=2, font_size=7,
        min_width=25, min_height=18,
    )
    small = LabeledBox(x=5, y=55, text="6pt label", padding=2, font_size=6)
    big = LabeledBox(x=35, y=55, text="12pt label", padding=2, font_size=12)

    n1 = LabeledBox(x=5, y=78, text="N1", padding=2, font_size=7)
    n2 = LabeledBox(x=35, y=78, text="N2", padding=2, font_size=7)
    n3 = LabeledBox(x=5, y=90, text="N3", padding=2, font_size=7)
    n4 = LabeledBox(x=35, y=90, text="N4", padding=2, font_size=7)
    cross_a = Arrow.connect(n1, n4, curve="cubic", bow=4)
    cross_b = Arrow.connect(n3, n2, curve="cubic", bow=4, stroke="#2A6F3D")
    vert = Arrow.connect(short, multi, curve="cubic", bow=6, stroke="#7E57C2")

    bg = canvas.layer("background")
    bg.add(dw.Rectangle(0, 0, 120, 100, fill="#FAFAFA"))
    arrows_layer = canvas.layer("connectors")
    for a in (cross_a, cross_b, vert):
        arrows_layer.add(a)
    boxes_layer = canvas.layer("boxes")
    for b in (short, long_one_line, multi, chunky, small, big, n1, n2, n3, n4):
        boxes_layer.add(b)
    return canvas


def main() -> Path:
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    svg_path = out_dir / "stress_test.svg"
    build().save(svg_path, output_png=True, png_width=1600)
    print(f"wrote {svg_path}")
    return svg_path


if __name__ == "__main__":
    main()
