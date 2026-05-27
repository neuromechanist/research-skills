"""Validation demo: builds a deliberately broken canvas and demonstrates
the `Canvas.save(validate=...)` modes.

The figure contains:
  - one box whose width was crushed below its text bbox (text-overflow)
  - two overlapping boxes in the same layer (sibling-overlap)
  - one clean box with a clean arrow (passes every check)

Run:
    uv run --with drawsvg --with svgpathtools --with Pillow --with fonttools \\
        --with cairosvg --with lxml \\
        python plugins/figures/skills/svg-primitives/examples/validation_demo.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from svg_primitives import (  # noqa: E402
    Arrow, Canvas, LabeledBox, ValidationError,
)


def build_broken() -> Canvas:
    canvas = Canvas(width_mm=120, height_mm=60)

    # Clean box + arrow (no finding).
    clean_a = LabeledBox(x=5, y=5, text="Clean", font_size=7)
    clean_b = LabeledBox(x=60, y=5, text="Target", font_size=7)
    canvas.layer("boxes").add(clean_a)
    canvas.layer("boxes").add(clean_b)
    canvas.layer("arrows").add(Arrow.connect(clean_a, clean_b))

    # Crushed box — guaranteed text-overflow.
    crushed = LabeledBox(x=5, y=25, text="overflowing text", font_size=7, padding=0)
    crushed.width = 4
    crushed.height = 3
    canvas.layer("boxes").add(crushed)

    # Overlapping boxes — guaranteed sibling-overlap.
    canvas.layer("boxes").add(LabeledBox(x=60, y=35, text="overlap A", font_size=7))
    canvas.layer("boxes").add(LabeledBox(x=63, y=37, text="overlap B", font_size=7))

    return canvas


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    canvas = build_broken()

    print("\n--- validate='warn' (default): findings logged, save proceeds ---")
    findings = canvas.save(out / "validation_demo.svg", validate="warn")
    print(f"\nReturned {len(findings)} finding(s):")
    for f in findings:
        print(f"  {f}")

    print("\n--- validate='strict': raises ValidationError ---")
    try:
        canvas.save(out / "validation_demo_strict.svg", validate="strict")
    except ValidationError as e:
        print(f"\nCaught ValidationError with {len(e.findings)} finding(s).")

    print("\n--- validate='off': skip and just write ---")
    findings_off = canvas.save(out / "validation_demo_off.svg", validate="off")
    print(f"validate='off' returned {len(findings_off)} finding(s) (skipped).")


if __name__ == "__main__":
    main()
