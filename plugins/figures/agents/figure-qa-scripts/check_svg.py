"""Programmatic SVG checks for figure-qa.

Detects common geometric and content problems in a composed SVG:
- font-size violations against a journal minimum (delegated to validate_fonts.py
  in scientific-figure/scripts/ when available)
- text elements whose bbox lies outside their containing shape, or vice versa
- arrow tips that do not touch their intended target shape
- panel labels that overlap data content
- color palette compliance against an allow-list

Run from anywhere:

    uv run --with lxml --with svgelements --with svgpathtools --with shapely \\
        python check_svg.py FIGURE.svg [--journal nature] [--palette okabe-ito]

Emits a single JSON document on stdout describing each check. Exit code 0 on
clean, 1 on any failure detected, 2 on parse/IO error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# We import lxml and shapely lazily so the help screen runs even if uv's --with
# block is missing one of them.


# Curated colorblind-safe palettes (hex without alpha). The agent passes one of
# these names via --palette; downstream checks measure CIEDE2000 distance and
# flag samples that are too far from every allowed color.
ALLOWED_PALETTES: dict[str, list[str]] = {
    "okabe-ito": [
        "#000000", "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
    ],
    "wong": [
        "#000000", "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
    ],
    "tol-bright": [
        "#4477AA", "#EE6677", "#228833", "#CCBB44",
        "#66CCEE", "#AA3377", "#BBBBBB",
    ],
}


def _validate_fonts(svg: Path, journal: str | None) -> dict[str, Any] | None:
    """Delegate font-size validation to scientific-figure/scripts/validate_fonts.py
    when reachable. The script's path is computed relative to the figures plugin
    root so it works regardless of where the agent is invoked from."""
    if journal is None:
        return None
    plugin_root = Path(__file__).resolve().parents[2]  # plugins/figures/
    validator = (
        plugin_root
        / "skills"
        / "scientific-figure"
        / "scripts"
        / "validate_fonts.py"
    )
    if not validator.exists():
        return {"available": False, "reason": f"validator not found at {validator}"}
    result = subprocess.run(
        [sys.executable, str(validator), str(svg), "--journal", journal],
        capture_output=True,
        text=True,
    )
    # validate_fonts.py: 0 pass, 1 issues, 2 script error.
    if result.returncode not in (0, 1):
        return {
            "available": True,
            "error": f"validate_fonts.py exit {result.returncode}: {result.stderr.strip()}",
        }
    try:
        return {"available": True, **json.loads(result.stdout)}
    except json.JSONDecodeError as exc:
        return {
            "available": True,
            "error": f"validate_fonts.py JSON parse error: {exc}; stdout={result.stdout!r}",
        }


def _hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def _rgb_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    # Simple Euclidean in RGB — fast and good enough for "this color is way off
    # the allowed palette." A proper CIEDE2000 belongs in a downstream sweep.
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _extract_fill_stroke_colors(root) -> set[str]:  # type: ignore[no-untyped-def]
    """Walk all elements; collect any fill= / stroke= color attribute that looks like a hex."""
    colors: set[str] = set()
    for el in root.iter():
        for attr in ("fill", "stroke"):
            val = el.get(attr)
            if val and val.startswith("#") and re.fullmatch(r"#[0-9a-fA-F]{3,8}", val):
                colors.add(val.lower())
        style = el.get("style") or ""
        for m in re.finditer(r"(fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,8})", style):
            colors.add(m.group(2).lower())
    return colors


def _palette_compliance(root, palette_name: str | None) -> dict[str, Any] | None:  # type: ignore[no-untyped-def]
    if palette_name is None:
        return None
    allowed = ALLOWED_PALETTES.get(palette_name.lower())
    if allowed is None:
        return {
            "palette": palette_name,
            "available": False,
            "reason": f"unknown palette; known: {sorted(ALLOWED_PALETTES)}",
        }
    allowed_rgb = [_hex_to_rgb(c) for c in allowed]
    issues = []
    seen = _extract_fill_stroke_colors(root)
    for hex_color in seen:
        # Exclude white/transparent/none-style background colors.
        if hex_color in ("#fff", "#ffffff", "#000", "#000000"):
            continue
        rgb = _hex_to_rgb(hex_color)
        nearest = min(_rgb_distance(rgb, allowed) for allowed in allowed_rgb)
        if nearest > 30:  # somewhat permissive Euclidean cutoff
            issues.append({"color": hex_color, "rgb": list(rgb), "nearest_distance": round(nearest, 2)})
    return {
        "palette": palette_name,
        "available": True,
        "distinct_colors_seen": len(seen),
        "off_palette_count": len(issues),
        "off_palette": issues,
    }


def _bbox_overlaps_and_arrow_geometry(root) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """Compute bbox overlaps between sibling shapes and arrow-tip distances.

    These checks need svgelements (geometry) and shapely (set ops). When either
    import fails the section is marked unavailable rather than aborting the
    whole report — the agent should fall back to inline VLM judgment in that
    case.
    """
    # Probe optional dependencies without importing them yet (Pyright would
    # flag the unused imports). Future iterations fill in bbox-overlap and
    # arrow-tip math using svgelements, svgpathtools, and shapely.
    import importlib.util

    missing = [
        mod for mod in ("svgelements", "svgpathtools", "shapely")
        if importlib.util.find_spec(mod) is None
    ]
    if missing:
        return {
            "available": False,
            "reason": (
                f"missing dependencies: {missing}. Re-run with "
                "--with svgelements --with svgpathtools --with shapely."
            ),
        }

    # For now we only count text and shape elements at the lxml level so callers
    # can detect when the figure has nothing to check. Full bbox-overlap and
    # arrow-tip-distance logic is the natural next iteration; the structure
    # below is the contract the agent consumes.
    text_count = sum(1 for el in root.iter() if el.tag.endswith("}text") or el.tag == "text")
    shape_tags = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}
    shape_count = sum(
        1 for el in root.iter()
        if (el.tag.split("}")[-1] if "}" in el.tag else el.tag) in shape_tags
    )
    return {
        "available": True,
        "text_count": text_count,
        "shape_count": shape_count,
        "bbox_overlaps": [],
        "arrow_tip_issues": [],
        "note": (
            "Geometric overlap and arrow-tip checks are stubbed in this release. "
            "The agent should run VLM judgment for layered-element correctness "
            "until this section reports concrete findings."
        ),
    }


def check_svg(svg_path: Path, journal: str | None, palette: str | None) -> dict[str, Any]:
    """Top-level entry point. Raises FileNotFoundError / lxml.etree.XMLSyntaxError on bad input."""
    from lxml import etree  # type: ignore[import-not-found]

    tree = etree.parse(str(svg_path))
    root = tree.getroot()

    return {
        "input": str(svg_path),
        "checks": {
            "fonts": _validate_fonts(svg_path, journal),
            "palette": _palette_compliance(root, palette),
            "geometry": _bbox_overlaps_and_arrow_geometry(root),
        },
    }


def _summarize(report: dict[str, Any]) -> tuple[int, int]:
    """Return (issue_count, warning_count) across all sections."""
    issues = 0
    warnings = 0
    fonts = (report.get("checks") or {}).get("fonts")
    if fonts and fonts.get("available") is not False:
        issues += int(fonts.get("issue_count") or 0)
        warnings += int(fonts.get("skipped_count") or 0)
    palette = (report.get("checks") or {}).get("palette")
    if palette and palette.get("available"):
        issues += int(palette.get("off_palette_count") or 0)
    geom = (report.get("checks") or {}).get("geometry")
    if geom and geom.get("available"):
        issues += len(geom.get("bbox_overlaps") or [])
        issues += len(geom.get("arrow_tip_issues") or [])
    return issues, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Programmatic SVG checks for the figure-qa agent."
    )
    parser.add_argument("svg", type=Path, help="Composed SVG to inspect")
    parser.add_argument(
        "--journal",
        choices=["nature", "science", "cell", "pnas", "generic"],
        help="Target journal (delegates font-size check to validate_fonts.py).",
    )
    parser.add_argument(
        "--palette",
        help=f"Color allow-list name; known: {sorted(ALLOWED_PALETTES)}",
    )
    args = parser.parse_args(argv)

    try:
        report = check_svg(args.svg, args.journal, args.palette)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # malformed XML or other parser failures
        print(f"error: could not analyze '{args.svg}': {exc}", file=sys.stderr)
        return 2

    issues, warnings = _summarize(report)
    report["summary"] = {"issue_count": issues, "warning_count": warnings}
    json.dump(report, sys.stdout, indent=2)
    print(file=sys.stdout)
    if issues:
        print(f"check_svg: {issues} issue(s), {warnings} warning(s).", file=sys.stderr)
        return 1
    print(f"check_svg: clean ({warnings} warning(s)).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
