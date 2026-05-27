"""Three-stage EEG processing chain — reproduced from `schematic.svg`
using the `svg-primitives` skill.

The hand-authored counterpart `schematic.svg` is the visual reference;
this script produces a visually equivalent SVG via primitives so text
containment, arrow-tip alignment, marker orientation, and layer paint
order are all enforced by `Canvas.save(validate='strict')`.

Run from the figures-plugin root:

    cd plugins/figures/skills
    uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools \\
        --with cairosvg --with lxml \\
        python svg-figure/examples/schematic_from_primitives.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add svg-primitives' scripts/ to sys.path so the package imports when
# this script is run directly (svg-primitives lives as a sibling skill).
_HERE = Path(__file__).resolve().parent
_SVG_PRIMITIVES_SCRIPTS = _HERE.parent.parent / "svg-primitives" / "scripts"
if str(_SVG_PRIMITIVES_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SVG_PRIMITIVES_SCRIPTS))

import drawsvg as dw  # noqa: E402

from svg_primitives import (  # noqa: E402
    Annotation,
    Arrow,
    Canvas,
    LabeledBox,
)


def build() -> Canvas:
    c = Canvas(width_mm=89, height_mm=40)

    # svg-primitives doesn't have a title primitive (titles are usually
    # owned by scientific-figure when composing panels), so punch through
    # to dw.Text and add it to a dedicated "title" layer. font-size in mm:
    # 6 pt × 25.4/72 ≈ 2.117 mm.
    c.layer("title").add(dw.Text(
        "EEG processing chain", x=44.5, y=5,
        text_anchor="middle", font_size=2.117,
        font_family="Helvetica, Arial, sans-serif", font_weight="bold",
    ))

    # Three nodes with okabe-ito palette matching the hand-authored example.
    # min_width/min_height clamp to consistent sizes regardless of label.
    acquire = LabeledBox(
        x=2, y=16, text="Acquire", font_size=5,
        fill="#ffffff", stroke="#0072B2", stroke_width=0.8,
        min_width=20, min_height=12,
    )
    bandpass = LabeledBox.next_to(
        acquire, side="E", gap=11, text="Bandpass", font_size=5,
        fill="#56B4E9", stroke="#0072B2", stroke_width=0.8,
        min_width=22, min_height=12,
    )
    classify = LabeledBox.next_to(
        bandpass, side="E", gap=11, text="Classify", font_size=5,
        fill="#009E73", stroke="#0072B2", stroke_width=0.8,
        min_width=20, min_height=12,
    )
    for b in (acquire, bandpass, classify):
        c.layer("boxes").add(b)

    c.layer("arrows").add(Arrow.connect(acquire, bandpass, stroke="#000000", stroke_width=0.8))
    c.layer("arrows").add(Arrow.connect(bandpass, classify, stroke="#000000", stroke_width=0.8))

    # Artifact-gate annotation. The hand-authored version uses a tiny
    # dashed segment plus a separate <text>; Annotation(leader_to=...)
    # gives us the bbox-edge-to-target leader for free.
    c.layer("annotations").add(Annotation(
        x=44, y=36, text="artifact gate", font_size=5,
        leader_to=(44, 29),
        fill="#D55E00",
        leader_stroke="#888888", leader_stroke_width=0.6,
    ))
    return c


def main() -> Path:
    out_dir = _HERE / "out"
    out_dir.mkdir(exist_ok=True)
    svg_path = out_dir / "schematic_from_primitives.svg"
    findings = build().save(svg_path, output_png=True, png_width=1600, validate="strict")
    assert not findings, f"unexpected findings: {findings}"
    print(f"wrote {svg_path} and {svg_path.with_suffix('.png')}")
    return svg_path


if __name__ == "__main__":
    main()
