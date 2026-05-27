"""Bracketed electrode grouping — demonstrates Bracket, Annotation, and Group.

A row of six EEG-electrode Pills (Fz, F3, F4, Cz, O1, O2) with:
  - a Bracket above grouping Fz/F3/F4 as 'frontal'
  - a Bracket below grouping O1/O2 as 'occipital'
  - a leader-line Annotation pointing at Cz
  - a Group(Fz, F3, F4) connected to a 'Frontal regressor' box via
    Arrow.connect — the arrow targets the group's union edge, not
    any individual pill.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from svg_primitives import (
    Annotation, Arrow, Bracket, Canvas, Group, LabeledBox, Pill,
)


def build() -> Canvas:
    canvas = Canvas(width_mm=160, height_mm=110)
    fs = 7.0
    pad = 2.0

    # Six electrodes in a row at y=50.
    x0 = 12
    gap = 4
    pills = []
    last_right = x0 - gap
    for label in ("Fz", "F3", "F4", "Cz", "O1", "O2"):
        p = Pill(x=last_right + gap, y=50, text=label, padding=pad, font_size=fs, min_width=10)
        pills.append(p)
        last_right = p.right
    fz, f3, f4, cz, o1, o2 = pills

    # Bracket above Fz/F3/F4 grouping them as "frontal".
    frontal_bracket = Bracket(
        start=(fz.left, fz.top - 1), end=(f4.right, f4.top - 1),
        depth=-6, label="Frontal channels", label_offset=2,
        font_size=fs - 1,
    )

    # Bracket below O1/O2 grouping them as "occipital".
    occipital_bracket = Bracket(
        start=(o1.left, o1.bottom + 1), end=(o2.right, o2.bottom + 1),
        depth=6, label="Occipital channels", label_offset=2,
        font_size=fs - 1,
    )

    # Leader-line annotation pointing at Cz.
    cz_callout = Annotation(
        x=cz.cx, y=85,
        text="Reference",
        leader_to=(cz.cx, cz.bottom + 1),
        font_size=fs - 1,
    )

    # Group the frontal pills and connect them to a regressor box.
    frontal_group = Group(fz, f3, f4)
    regressor = LabeledBox(x=10, y=15, text="Frontal regressor", padding=pad, font_size=fs)
    arrow = Arrow.connect(regressor, frontal_group, curve="cubic", bow=-4, stroke="#C45146")

    annotations_layer = canvas.layer("annotations")
    annotations_layer.add(frontal_bracket)
    annotations_layer.add(occipital_bracket)
    annotations_layer.add(cz_callout)

    arrows_layer = canvas.layer("connectors")
    arrows_layer.add(arrow)

    boxes = canvas.layer("boxes")
    for p in pills:
        boxes.add(p)
    boxes.add(regressor)

    return canvas


def main() -> Path:
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    svg_path = out_dir / "bracketed_grouping.svg"
    build().save(svg_path, output_png=True, png_width=1800)
    print(f"wrote {svg_path}")
    return svg_path


if __name__ == "__main__":
    main()
