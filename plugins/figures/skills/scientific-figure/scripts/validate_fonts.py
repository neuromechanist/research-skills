"""Validate that every <text> element in a composed SVG meets the target journal's font minimum.

Walks the SVG transform stack so that text inside a panel scaled by 0.5 is reported at half its
specified font size, and folds in the document's user-unit -> point scale from the root width and
viewBox so the reported size is the physical point size. That scale is ~1.0 for a point-based
viewBox (matplotlib's default export) and ~72/25.4 for an mm-based viewBox (the convention used by
scientific-figure, svg-figure, and svg-primitives), so a bare font-size of 5 in an `89mm` /
`viewBox 89` schematic is correctly reported as ~14 pt rather than 5 pt. An explicit unit on the
font-size (pt/px/mm/cm/in) is treated as an absolute size; a bare number is treated as user units.

Usage:

    uv run --with lxml python validate_fonts.py figure.svg --journal nature

Output: JSON to stdout, human summary to stderr. Exit code 0 if all pass, 1 if any below minimum.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterator

from lxml import etree


JOURNAL_MIN_PT: dict[str, float] = {
    "nature": 5.0,
    "science": 6.0,
    "cell": 6.0,
    "pnas": 6.0,
    "generic": 5.0,
}

SVG_NS = "http://www.w3.org/2000/svg"
NSMAP = {"svg": SVG_NS}

_FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([0-9.]+)\s*(px|pt|em|%|mm|cm|in|pc)?", re.IGNORECASE)
_TRANSFORM_SCALE_RE = re.compile(
    r"scale\s*\(\s*(-?[0-9.]+)\s*(?:,\s*(-?[0-9.]+)\s*)?\)"
)
_TRANSFORM_MATRIX_RE = re.compile(
    r"matrix\s*\(\s*(-?[0-9.]+)[ ,]+(-?[0-9.]+)[ ,]+(-?[0-9.]+)[ ,]+(-?[0-9.]+)[ ,]+(-?[0-9.]+)[ ,]+(-?[0-9.]+)\s*\)"
)


def _parse_transform(value: str) -> tuple[float, float]:
    """Return (scale_x, scale_y) implied by a transform string."""
    sx, sy = 1.0, 1.0
    if not value:
        return sx, sy
    for m in _TRANSFORM_SCALE_RE.finditer(value):
        x = float(m.group(1))
        y = float(m.group(2)) if m.group(2) is not None else x
        sx *= x
        sy *= y
    for m in _TRANSFORM_MATRIX_RE.finditer(value):
        a, b, c, d, _e, _f = (float(g) for g in m.groups())
        # The matrix scale magnitude in x and y axes.
        sx *= (a * a + b * b) ** 0.5
        sy *= (c * c + d * d) ** 0.5
    return sx, sy


# Absolute length units -> points (1 in = 72 pt, 96 px = 1 in, 1 pc = 12 pt).
_UNIT_TO_PT: dict[str, float] = {
    "pt": 1.0,
    "px": 72.0 / 96.0,
    "mm": 72.0 / 25.4,
    "cm": 72.0 / 2.54,
    "in": 72.0,
    "pc": 12.0,
}


def _root_unit_to_pt(root: etree._Element) -> float:
    """Physical points per SVG user unit at the document root, from its width and viewBox.

    width="89mm" with viewBox width 89 -> 1 user unit is 1 mm -> 72/25.4 pt per unit.
    width="460.8pt" with viewBox width 460.8 -> 1 user unit is 1 pt -> 1.0 pt per unit.
    Returns 1.0 (the prior behavior) when the width has no physical unit or there is no
    viewBox, so unit-less SVGs are unaffected.
    """
    width = root.get("width")
    vb = root.get("viewBox")
    if not width or not vb:
        return 1.0
    try:
        vb_w = float(re.split(r"[\s,]+", vb.strip())[2])  # viewBox: min-x min-y width height
    except (IndexError, ValueError):
        return 1.0
    m = re.match(r"\s*(-?[0-9.]+)\s*([a-z%]*)\s*$", width, re.IGNORECASE)
    if not m or vb_w == 0:
        return 1.0
    val, unit = float(m.group(1)), m.group(2).lower()
    if unit not in _UNIT_TO_PT:  # unit-less or "%": keep the legacy 1:1 (number == pt) reading
        return 1.0
    return (val * _UNIT_TO_PT[unit]) / vb_w


def _font_size_pt(text_el: etree._Element) -> tuple[float, bool] | None:
    """Return (size, in_user_units) for a <text>/<tspan>, or None when no font-size is present.

    When `in_user_units` is True the size is in SVG user units and the caller multiplies it by the
    root user-unit -> pt scale (see `_root_unit_to_pt`); when False the size is already an absolute
    point value (the font-size carried an explicit pt/px/mm/cm/in/pc/em/% unit). A transform scale
    applies in both cases.
    """
    raw = text_el.get("font-size")
    unit: str | None = None
    value: str | None = None
    if raw:
        m = re.match(r"\s*([0-9.]+)\s*(px|pt|em|%|mm|cm|in|pc)?", raw, re.IGNORECASE)
        if m:
            value, unit = m.group(1), m.group(2)
    if value is None:
        style = text_el.get("style") or ""
        m = _FONT_SIZE_RE.search(style)
        if m:
            value, unit = m.group(1), m.group(2)
    if value is None:
        return None
    n = float(value)
    unit = (unit or "").lower()
    if unit == "":  # bare number: user units (mm in an mm-viewBox, pt in a pt-viewBox)
        return n, True
    if unit in _UNIT_TO_PT:
        return n * _UNIT_TO_PT[unit], False
    if unit == "em":
        # Heuristic: assume 12 pt parent em. Avoid em in source plots (matplotlib does
        # not emit em); this branch exists so hand-authored SVGs do not crash the walker.
        return n * 12.0, False
    if unit == "%":
        return n / 100.0 * 12.0, False
    # The regex above only captures the units handled here; reaching this point means the
    # regex and the handler list drifted out of sync, which must be fixed loudly rather
    # than by silently treating an absolute unit as user-relative.
    raise AssertionError(f"unhandled font-size unit {unit!r}; add it to _UNIT_TO_PT or a branch")


def _walk(root: etree._Element) -> Iterator[tuple[etree._Element, float, float]]:
    """Yield (element, cumulative_scale_x, cumulative_scale_y) for every <text> and <tspan>
    element that declares its own font-size. tspan is yielded as well as text so that
    hand-authored SVGs (Inkscape, Illustrator) that put font-size on tspan children are checked.
    Sibling order within a parent is reversed because the walker uses a LIFO stack; this does
    not affect correctness since every relevant element is visited.
    """
    stack: list[tuple[etree._Element, float, float]] = [(root, 1.0, 1.0)]
    while stack:
        el, sx, sy = stack.pop()
        # lxml Comment and ProcessingInstruction nodes have a non-string .tag (a
        # cython function); QName chokes on those. Skip them and recurse into
        # their (non-existent) children harmlessly.
        if not isinstance(el.tag, str):
            for child in el:
                stack.append((child, sx, sy))
            continue
        local_sx, local_sy = _parse_transform(el.get("transform") or "")
        cur_sx, cur_sy = sx * local_sx, sy * local_sy
        tag = etree.QName(el).localname
        if tag in ("text", "tspan"):
            yield el, cur_sx, cur_sy
        for child in el:
            stack.append((child, cur_sx, cur_sy))


def validate(svg_path: Path, journal: str) -> dict:
    """Validate font sizes in svg_path against the journal minimum. Raises ValueError on
    unknown journal, etree.XMLSyntaxError on malformed SVG, and OSError on file errors."""
    minimum_pt = JOURNAL_MIN_PT.get(journal.lower())
    if minimum_pt is None:
        raise ValueError(
            f"unknown journal '{journal}'. Known: {sorted(JOURNAL_MIN_PT)}"
        )

    tree = etree.parse(str(svg_path))
    root = tree.getroot()

    issues: list[dict] = []
    checked = 0
    skipped = 0
    root_unit_to_pt = _root_unit_to_pt(root)
    # When the root width carries no length unit but a viewBox is present, the scale fell
    # back to 1.0 (bare font-sizes read as points). Flag it so a caller does not mistake the
    # guess for the genuine pt-viewBox case (where the unit is explicit).
    root_scale_uncertain = bool(root.get("viewBox")) and re.fullmatch(
        r"\s*-?[0-9.]+\s*", root.get("width") or ""
    ) is not None
    for text_el, sx, sy in _walk(root):
        parsed = _font_size_pt(text_el)
        if parsed is None:
            # tspan with no own font-size inherits from its parent <text>; the parent's
            # check (or another descendant tspan) governs. Don't count it as skipped.
            tag = etree.QName(text_el).localname
            if tag == "tspan":
                continue
            # <text> with no own font-size is only skipped if no descendant tspan
            # supplies one; otherwise the descendant will be checked separately.
            if any(
                etree.QName(d).localname == "tspan" and _font_size_pt(d) is not None
                for d in text_el.iter()
            ):
                continue
            skipped += 1
            continue
        checked += 1
        base, in_user_units = parsed
        # A bare font-size number is in user units; convert it to physical points via the
        # root user-unit -> pt scale. An explicit-unit size is already absolute points.
        specified = base * (root_unit_to_pt if in_user_units else 1.0)
        # abs() so that mirrored panels (scale(-1, 1)) do not produce false negatives.
        effective = specified * min(abs(sx), abs(sy))
        if effective < minimum_pt:
            issues.append(
                {
                    "text": "".join(text_el.itertext()).strip()[:80],
                    "specified_pt": round(specified, 3),
                    "effective_pt": round(effective, 3),
                    "scale_x": round(sx, 4),
                    "scale_y": round(sy, 4),
                    "minimum_pt": minimum_pt,
                    "tag_id": text_el.get("id") or "",
                }
            )

    return {
        "svg": str(svg_path),
        "journal": journal,
        "minimum_pt": minimum_pt,
        "root_unit_to_pt": round(root_unit_to_pt, 4),
        "root_scale_uncertain": root_scale_uncertain,
        "checked_count": checked,
        "skipped_count": skipped,
        "issue_count": len(issues),
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate that every <text> element in a composed SVG meets the journal font minimum."
    )
    parser.add_argument("svg", type=Path, help="Composed SVG to validate")
    parser.add_argument(
        "--journal",
        required=True,
        choices=sorted(JOURNAL_MIN_PT),
        help="Target journal (controls font minimum)",
    )
    args = parser.parse_args(argv)

    try:
        report = validate(args.svg, args.journal)
    except etree.XMLSyntaxError as exc:
        print(f"error: could not parse SVG '{args.svg}': {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: could not open SVG '{args.svg}': {exc}", file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2)
    print(file=sys.stdout)

    if report.get("root_scale_uncertain"):
        print(
            "WARNING: the root width has no length unit (e.g. mm/pt) but a viewBox is "
            "present; bare font-sizes are assumed to be points and physical sizes may be "
            "wrong. Add an explicit unit to the root width.",
            file=sys.stderr,
        )
    if report["skipped_count"]:
        print(
            f"WARNING: {report['skipped_count']} <text> element(s) had no parseable "
            "font-size and were not checked (CSS class selectors or inherited styles).",
            file=sys.stderr,
        )
    if report["issue_count"]:
        print(
            f"font validation: {report['issue_count']} of {report['checked_count']} <text>/<tspan> "
            f"elements below {report['minimum_pt']} pt for journal '{args.journal}'.",
            file=sys.stderr,
        )
        return 1
    print(
        f"font validation: all {report['checked_count']} <text>/<tspan> elements meet "
        f"{report['minimum_pt']} pt minimum for journal '{args.journal}'.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
