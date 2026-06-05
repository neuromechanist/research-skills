"""Self-contained test fixture for check_svg.py's geometry section (issue #47).

Constructs synthetic SVGs covering the three geometry checks and asserts the expected
finding counts: text bleeding out of its box, an arrow tip that misses its target, and
sibling shapes whose bounding boxes collide. Also covers the cases that must NOT fire:
free-floating text, an arrow whose tip lands on the target edge, and intentional
containment (an icon foreground over its background rect).

    uv run --with lxml --with svgelements --with shapely \\
        python check_svg_failure_cases.py

Exit 0 if every assertion passes, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from check_svg import check_svg  # type: ignore[import-not-found]  # noqa: E402  (after sys.path setup)

_HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">'


def _svg(w: int, h: int, body: str) -> str:
    return _HEAD.format(w=w, h=h) + body + "</svg>"


# (label, svg, exp_text_overflow, exp_arrow_issues, exp_bbox_overlaps)
CASES: list[tuple[str, str, int, int, int]] = [
    (
        "text overflows its box",
        _svg(
            100, 50,
            '<rect x="10" y="10" width="10" height="10" fill="#fff" stroke="#000"/>'
            '<text x="15" y="15" text-anchor="middle" dominant-baseline="middle" '
            'font-size="5">this label is far too long for its tiny box</text>',
        ),
        1, 0, 0,
    ),
    (
        "arrow tip misses every target",
        _svg(
            100, 50,
            '<rect x="60" y="20" width="20" height="20" fill="#fff" stroke="#000"/>'
            '<line x1="5" y1="10" x2="20" y2="10" stroke="#000" marker-end="url(#a)"/>',
        ),
        0, 1, 0,
    ),
    (
        "sibling boxes collide",
        _svg(
            100, 50,
            '<rect x="10" y="10" width="20" height="20" fill="#0072B2"/>'
            '<rect x="25" y="15" width="20" height="20" fill="#009E73"/>',
        ),
        0, 0, 1,
    ),
    (
        "clean: text fits, no arrow, no collision",
        _svg(
            50, 30,
            '<rect x="5" y="5" width="40" height="20" fill="#fff" stroke="#000"/>'
            '<text x="25" y="15" text-anchor="middle" dominant-baseline="middle" '
            'font-size="5">ok</text>',
        ),
        0, 0, 0,
    ),
    (
        "free-floating text (overlaps no shape) is not flagged",
        _svg(
            60, 30,
            '<rect x="5" y="5" width="10" height="10" fill="#0072B2"/>'
            '<text x="45" y="25" text-anchor="middle" font-size="5">caption</text>',
        ),
        0, 0, 0,
    ),
    (
        "arrow tip on target edge is not flagged",
        _svg(
            60, 30,
            '<line x1="5" y1="15" x2="20" y2="15" stroke="#000" marker-end="url(#a)"/>'
            '<rect x="20" y="5" width="20" height="20" fill="#fff" stroke="#000"/>',
        ),
        0, 0, 0,
    ),
    (
        "intentional containment (icon fg over bg rect) is not a collision",
        _svg(
            50, 50,
            '<rect x="5" y="5" width="40" height="40" fill="#eeeeee"/>'
            '<rect x="15" y="15" width="20" height="20" fill="#0072B2"/>',
        ),
        0, 0, 0,
    ),
    (
        "transform stack resolved: a scaled panel that collides is flagged",
        _svg(
            100, 60,
            '<g transform="translate(10,10) scale(1.5)">'
            '<rect x="2" y="2" width="30" height="14" fill="#ffffff" stroke="#0072B2"/></g>'
            '<g transform="translate(55,10)">'
            '<rect x="0" y="0" width="35" height="20" fill="#ffffff" stroke="#0072B2"/></g>',
        ),
        0, 0, 1,
    ),
    (
        "right-aligned (text-anchor=end) text overflows left out of its box",
        _svg(
            100, 40,
            '<rect x="60" y="10" width="20" height="12" fill="#fff" stroke="#000"/>'
            '<text x="78" y="16" text-anchor="end" dominant-baseline="middle" '
            'font-size="5">overflowing right aligned label</text>',
        ),
        1, 0, 0,
    ),
    (
        "two circles whose bboxes collide",
        _svg(
            60, 40,
            '<circle cx="20" cy="20" r="12" fill="#0072B2"/>'
            '<circle cx="35" cy="20" r="12" fill="#009E73"/>',
        ),
        0, 0, 1,
    ),
]


def run() -> int:
    failures = 0
    with TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        for i, (label, svg, exp_text, exp_arrow, exp_bbox) in enumerate(CASES):
            path = tmp / f"case_{i}.svg"
            path.write_text(svg)
            geom = check_svg(path, journal=None, palette=None)["checks"]["geometry"]
            assert geom.get("available") and not geom.get("error"), f"{label}: geometry unavailable: {geom}"
            n_text = len(geom["text_overflow"])
            n_arrow = len(geom["arrow_tip_issues"])
            n_bbox = len(geom["bbox_overlaps"])
            ok = n_text == exp_text and n_arrow == exp_arrow and n_bbox == exp_bbox
            print(
                f"[{'PASS' if ok else 'FAIL'}] {label}: "
                f"text={n_text}(exp {exp_text}) arrow={n_arrow}(exp {exp_arrow}) "
                f"bbox={n_bbox}(exp {exp_bbox})"
            )
            if not ok:
                failures += 1

    print()
    print(f"{len(CASES) - failures}/{len(CASES)} cases passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
