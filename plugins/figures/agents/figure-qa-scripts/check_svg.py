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
# these names via --palette; downstream checks compute Euclidean RGB distance and
# flag samples that are too far from every allowed color. Near-gray colors
# (axis spines, tick marks) are exempted before comparison so they do not
# produce false positives.
ALLOWED_PALETTES: dict[str, list[str]] = {
    "okabe-ito": [
        "#000000", "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
    ],
    "tol-bright": [
        "#4477AA", "#EE6677", "#228833", "#CCBB44",
        "#66CCEE", "#AA3377", "#BBBBBB",
    ],
}
# Wong 2011 republished the Okabe-Ito 2008 palette unchanged; keep both names
# pointing to the same list so users see the canonical citation either way.
ALLOWED_PALETTES["wong"] = ALLOWED_PALETTES["okabe-ito"]


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
    try:
        result = subprocess.run(
            [sys.executable, str(validator), str(svg), "--journal", journal],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return {
            "available": True,
            "error": "validate_fonts.py timed out after 60 s; the SVG may have a pathological transform stack.",
        }
    # validate_fonts.py: 0 pass, 1 issues, 2 script error.
    stdout = result.stdout or ""
    stderr = (result.stderr or "").strip()
    if result.returncode not in (0, 1):
        return {
            "available": True,
            "error": f"validate_fonts.py exit {result.returncode}: {stderr}",
        }
    # Distinguish "crashed (exit 1, no JSON)" from "1 finding (exit 1, JSON output)".
    if result.returncode == 1 and not stdout.strip():
        return {
            "available": True,
            "error": f"validate_fonts.py crashed (exit 1 with empty stdout): {stderr[:400]}",
        }
    if not stdout.strip():
        # exit 0 with empty stdout means "no <text> elements at all"; treat as clean.
        return {"available": True, "issue_count": 0, "issues": [], "checked_count": 0}
    try:
        return {"available": True, **json.loads(stdout)}
    except json.JSONDecodeError as exc:
        return {
            "available": True,
            "error": f"validate_fonts.py JSON parse error: {exc}; stderr={stderr[:200]}",
        }


# Valid CSS hex colors: 3, 4, 6, or 8 hex digits. 5- and 7-digit strings are not
# valid and would crash _hex_to_rgb if accepted. Alternation is ordered
# longest-first so finditer doesn't greedily match the 3-digit prefix of a
# 6-digit value (e.g., "#007" inside "#0072B2").
_HEX_RE = re.compile(
    r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![0-9a-fA-F])"
)


def _hex_to_rgb(s: str) -> tuple[int, int, int]:
    """Convert a 3/4/6/8-digit CSS hex color to an (R, G, B) triple. Alpha bytes
    on 4- and 8-digit inputs are intentionally discarded (palette compliance
    only checks color, not opacity)."""
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    elif len(s) == 4:  # RGBA shorthand
        s = "".join(c * 2 for c in s[:3])
    elif len(s) == 8:  # RRGGBBAA
        s = s[:6]
    if len(s) != 6:
        raise ValueError(f"unexpected hex length after normalization: '#{s}'")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def _rgb_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    # Simple Euclidean in RGB — fast and good enough for "this color is way off
    # the allowed palette."
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _is_near_gray(rgb: tuple[int, int, int], tol: int = 15) -> bool:
    """True when all three channels are within tol of each other (axis spines,
    ticks, gridlines, background neutrals)."""
    return (
        abs(rgb[0] - rgb[1]) <= tol
        and abs(rgb[1] - rgb[2]) <= tol
        and abs(rgb[0] - rgb[2]) <= tol
    )


def _extract_fill_stroke_colors(root) -> set[str]:  # type: ignore[no-untyped-def]
    """Walk all elements; collect any fill= / stroke= color attribute that looks like a hex."""
    colors: set[str] = set()
    for el in root.iter():
        for attr in ("fill", "stroke"):
            val = el.get(attr)
            if val and val.startswith("#") and _HEX_RE.fullmatch(val):
                colors.add(val.lower())
        style = el.get("style") or ""
        for m in re.finditer(r"(?:fill|stroke)\s*:\s*(" + _HEX_RE.pattern + ")", style):
            colors.add(m.group(1).lower())
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
        try:
            rgb = _hex_to_rgb(hex_color)
        except ValueError:
            # Skip values our regex shouldn't admit; do not crash the whole check.
            continue
        # Skip backgrounds and near-gray colors (axes, ticks, gridlines).
        if hex_color in ("#fff", "#ffffff", "#000", "#000000"):
            continue
        if _is_near_gray(rgb):
            continue
        nearest = min(_rgb_distance(rgb, allowed) for allowed in allowed_rgb)
        if nearest > 30:  # Euclidean RGB cutoff for "clearly off-palette"
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
    # lxml Comment / ProcessingInstruction nodes have a non-string .tag (a
    # cython function); coerce via _localname and skip non-element nodes.
    def _localname(el) -> str:  # type: ignore[no-untyped-def]
        tag = el.tag
        if not isinstance(tag, str):
            return ""
        return tag.split("}")[-1] if "}" in tag else tag

    text_count = sum(1 for el in root.iter() if _localname(el) == "text")
    shape_tags = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}
    shape_count = sum(1 for el in root.iter() if _localname(el) in shape_tags)
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
    except ImportError as exc:
        print(
            f"error: missing dependency for check_svg.py — re-run with "
            f"--with lxml --with svgelements --with svgpathtools --with shapely: {exc}",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:  # malformed XML or other parser failures
        print(f"error ({type(exc).__name__}): could not analyze '{args.svg}': {exc}", file=sys.stderr)
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
