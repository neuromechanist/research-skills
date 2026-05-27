"""Orthogonal-routed flowchart — demonstrates curve='orthogonal-h'.

Four boxes in a row connected with right-angle paths. The vertical
detour at the chord midpoint demonstrates that the arrowhead lands
on the target's W edge with marker orient='auto' producing a tangent-
correct head along the final horizontal segment.

A second arrow uses via=[(x, y)] + corner_radius to route around the
'Cleaning' box.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from svg_primitives import Arrow, Canvas, LabeledBox  # noqa: E402


def build() -> Canvas:
    canvas = Canvas(width_mm=180, height_mm=70)
    pad = 2.0
    fs = 7.0

    acquire = LabeledBox(x=8, y=15, text="Acquisition\n(64 ch EEG)", padding=pad, font_size=fs)
    clean = LabeledBox(x=acquire.right + 14, y=15, text="Cleaning\n(ICA + ASR)", padding=pad, font_size=fs)
    decode = LabeledBox(x=clean.right + 14, y=15, text="Decoding\n(BCI)", padding=pad, font_size=fs)
    archive = LabeledBox(x=decode.right + 14, y=15, text="Archive\n(BIDS)", padding=pad, font_size=fs)

    arrows = canvas.layer("connectors")
    arrows.add(Arrow.connect(acquire, clean, curve="orthogonal-h"))
    arrows.add(Arrow.connect(clean, decode, curve="orthogonal-h"))
    arrows.add(Arrow.connect(decode, archive, curve="orthogonal-h"))

    # Bypass arrow: acquisition -> archive directly, routed around the row
    # via a waypoint above the boxes, with rounded interior corners.
    bypass_waypoint = [(acquire.right + 6, 5), (archive.left - 6, 5)]
    arrows.add(Arrow.connect(
        acquire, archive, curve="straight", via=bypass_waypoint,
        corner_radius=3.0, stroke="#7E57C2",
        src_side="N", dst_side="N",
    ))

    boxes = canvas.layer("boxes")
    for b in (acquire, clean, decode, archive):
        boxes.add(b)
    return canvas


def main() -> Path:
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    svg_path = out_dir / "orthogonal_flowchart.svg"
    build().save(svg_path, output_png=True, png_width=1800)
    print(f"wrote {svg_path}")
    return svg_path


if __name__ == "__main__":
    main()
