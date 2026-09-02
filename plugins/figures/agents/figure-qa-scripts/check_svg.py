"""Programmatic SVG checks for figure-qa.

Detects common geometric and content problems in a composed SVG:
- font-size violations against a journal minimum (delegated to validate_fonts.py
  in scientific-figure/scripts/ when available)
- text whose estimated bbox bleeds outside its containing shape
- arrow tips (marker-end) that do not reach their nearest target shape
- sibling shapes whose bounding boxes collide (excluding intentional containment)
- color palette compliance against an allow-list

Run from anywhere:

    uv run --with lxml --with svgelements --with shapely \\
        python check_svg.py FIGURE.svg [--journal nature] \\
        [--palette okabe-ito|path/to/theme.json] [--json]

Default output is a single JSON document (the per-check report) on stdout.
With --json, stdout carries only the unified finding envelope shared with
check_raster.py; human-readable summaries always go to stderr.

Exit code 0 on clean, 1 on any failure detected, 2 on parse/IO error.
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


def _load_theme_lib():  # type: ignore[no-untyped-def]
    """Import plugins/figures/lib/theme.py by file path under a unique module
    name (a bare ``import theme`` could collide with an unrelated module).
    Returns the module, or None when the lib is missing or fails to import."""
    import importlib.util

    lib_path = Path(__file__).resolve().parents[2] / "lib" / "theme.py"
    if not lib_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("figures_theme_lib", lib_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, SyntaxError, OSError):
        return None
    return module


ALLOWED_PALETTES: dict[str, list[str]] = {
    "okabe-ito": [
        "#000000",
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
    ],
    "tol-bright": [
        "#4477AA",
        "#EE6677",
        "#228833",
        "#CCBB44",
        "#66CCEE",
        "#AA3377",
        "#BBBBBB",
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
        plugin_root / "skills" / "scientific-figure" / "scripts" / "validate_fonts.py"
    )
    if not validator.exists():
        return {"available": False, "reason": f"validator not found at {validator}"}
    try:
        result = subprocess.run(
            [sys.executable, str(validator), str(svg), "--journal", journal],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,  # non-zero (1) means "issues found", handled below, not a crash
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


def _resolve_palette(spec: str, theme_lib) -> tuple[str, list[str]]:  # type: ignore[no-untyped-def]
    """Resolve --palette to (name, hex list): a known preset name, or a path
    to a theme.json (flattened via lib/theme.py's palette_hexes ordering).
    Falls back to the local ALLOWED_PALETTES + a naive theme.json reader when
    lib/theme.py cannot be imported."""
    if theme_lib is not None:
        return theme_lib.resolve_palette(spec)
    preset = ALLOWED_PALETTES.get(spec.lower())
    if preset is not None:
        return spec.lower(), list(preset)
    path = Path(spec)
    if path.exists():
        theme = json.loads(path.read_text())
        palette = theme.get("palette") or {}
        hexes = [
            v for v in palette.values() if isinstance(v, str) and v.startswith("#")
        ]
        for arr_key in ("categorical", "sequential", "diverging"):
            hexes += [
                c
                for c in palette.get(arr_key, [])
                if isinstance(c, str) and c.startswith("#")
            ]
        if not hexes:
            raise ValueError(f"{path}: theme has no usable hex colors in its palette")
        return str(theme.get("theme_id") or path.stem), hexes
    raise ValueError(
        f"'{spec}' is neither a known palette preset ({sorted(ALLOWED_PALETTES)}) nor an existing theme.json path"
    )


def _palette_compliance(
    root, palette_name: str | None, theme_lib
) -> dict[str, Any] | None:  # type: ignore[no-untyped-def]
    if palette_name is None:
        return None
    try:
        name, allowed = _resolve_palette(palette_name, theme_lib)
    except ValueError as exc:
        return {"palette": palette_name, "available": False, "reason": str(exc)}
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
            issues.append(
                {
                    "color": hex_color,
                    "rgb": list(rgb),
                    "nearest_distance": round(nearest, 2),
                }
            )
    return {
        "palette": name,
        "available": True,
        "distinct_colors_seen": len(seen),
        "off_palette_count": len(issues),
        "off_palette": issues,
    }


# Clearance tolerance for every geometry check, in millimetres. Anything within this
# band counts as "touching"/"contained" so sub-mm rounding does not produce findings.
_GEOM_TOL_MM = 1.0
# svgelements does not measure glyph extents (it returns a zero-size bbox at the text
# anchor) and SVGs rarely embed the font, so text width is estimated from font size and
# character count. The ratio is a deliberately conservative average sans-serif advance:
# it keeps tightly-fitted labels in clean figures from being flagged and catches clear
# overflow, not sub-mm fit. For exact text-fit validation use svg-primitives (fontTools).
_TEXT_ADVANCE_EM = 0.45


def _viewbox_mm_per_unit(root) -> float:  # type: ignore[no-untyped-def]
    """Millimetres per SVG user unit, derived from the width attribute and the viewBox.
    Defaults to 1.0 (user units already in mm, the convention for figures this plugin
    produces) when the width carries no physical unit."""
    vb = root.get("viewBox")
    width = root.get("width")
    if not vb or not width:
        return 1.0
    try:
        vb_w = float(
            re.split(r"[\s,]+", vb.strip())[2]
        )  # viewBox may be comma- or space-delimited
    except (IndexError, ValueError):
        return 1.0
    match = re.match(r"\s*(-?[0-9.]+)\s*([a-z%]*)\s*$", width, re.IGNORECASE)
    if not match or vb_w == 0:
        return 1.0
    val, unit = float(match.group(1)), match.group(2).lower()
    to_mm = {
        "mm": 1.0,
        "cm": 10.0,
        "in": 25.4,
        "pt": 25.4 / 72.0,
        "pc": 25.4 / 6.0,
        "px": 25.4 / 96.0,
    }
    if unit not in to_mm:  # unitless or "%": assume user units are already millimetres
        return 1.0
    return (val * to_mm[unit]) / vb_w


def _text_bbox(
    elem, ax: float, ay: float, fs: float, text: str
) -> tuple[float, float, float, float]:  # type: ignore[no-untyped-def]
    """Estimate a text element's bounding box in user units from its anchor point
    (ax, ay), font size, and content. Honours text-anchor (x) and dominant-baseline (y)."""
    w = len(text) * fs * _TEXT_ADVANCE_EM
    anchor = (
        elem.values.get("text-anchor") or getattr(elem, "anchor", "") or "start"
    ).lower()
    if anchor in ("middle", "center"):
        xmin, xmax = ax - w / 2.0, ax + w / 2.0
    elif anchor == "end":
        xmin, xmax = ax - w, ax
    else:
        xmin, xmax = ax, ax + w
    baseline = (elem.values.get("dominant-baseline") or "").lower()
    if baseline in ("middle", "central"):
        ymin, ymax = ay - fs / 2.0, ay + fs / 2.0
    elif baseline in ("hanging", "text-before-edge"):
        ymin, ymax = ay, ay + fs
    else:  # alphabetic baseline: glyphs sit above the anchor
        ymin, ymax = ay - 0.8 * fs, ay + 0.2 * fs
    return xmin, ymin, xmax, ymax


def _contains(outer, inner, tol: float) -> bool:
    """True when `inner` bbox sits within `outer` bbox, allowing `tol` slack on each side."""
    return (
        inner[0] >= outer[0] - tol
        and inner[1] >= outer[1] - tol
        and inner[2] <= outer[2] + tol
        and inner[3] <= outer[3] + tol
    )


def _overlaps(a, b) -> bool:
    """True when two bboxes intersect at all."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _bbox_gap(a, b) -> float:
    """Axis-aligned gap between two bboxes (0 when they overlap)."""
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return (dx * dx + dy * dy) ** 0.5


def _bbox_overlaps_and_arrow_geometry(root, svg_path: Path) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """Geometry checks for a composed SVG, in user (viewBox) units:

    - text_overflow: a <text> that overlaps a shape but bleeds beyond every shape it
      overlaps (heuristic text width; see _TEXT_ADVANCE_EM).
    - arrow_tip_issues: a line/path with a marker-end whose tip is more than the
      tolerance from the nearest closed target shape.
    - bbox_overlaps: a pair of closed shapes whose bounding boxes collide (partial
      overlap, neither containing the other; containment is treated as intentional,
      e.g. an icon foreground over its background rect).

    Rect, Circle, Ellipse, and Polygon are recognized as closed shapes/targets, as
    are `<image>` elements (the substrate of an ai-full-figure overlay composition)
    and closed `<path>` elements (path data ending in 'z'/'Z'); an open `<path>`
    (e.g. a hand-drawn box with no closing segment) is not treated as a shape, so
    arrows aimed at one are reported via `arrows_without_targets` instead.

    Needs svgelements (resolved geometry) and shapely (distance). When a dependency is
    missing the section is marked unavailable so the agent falls back to VLM judgment.
    """
    import importlib.util

    missing = [
        m for m in ("svgelements", "shapely") if importlib.util.find_spec(m) is None
    ]
    if missing:
        return {
            "available": False,
            "reason": (
                f"missing dependencies: {missing}. Re-run with --with svgelements --with shapely."
            ),
        }

    from shapely.geometry import Point  # type: ignore[import-not-found]
    from shapely.geometry import box as shapely_box
    from svgelements import (  # type: ignore[import-not-found]
        SVG,
        Circle,
        Ellipse,
        Image,
        Path,
        Polygon,
        Rect,
        Text,
    )

    try:
        doc = SVG.parse(str(svg_path), reify=True)
        vb_w = float(doc.viewbox.width) if doc.viewbox else float(doc.width)
        factor = float(doc.width) / vb_w if vb_w else 1.0
    except Exception as exc:  # noqa: BLE001 - a geometry parse failure must not abort the report
        return {
            "available": True,
            "error": f"svgelements parse failed: {type(exc).__name__}: {exc}",
        }
    if (
        not factor
    ):  # width="0" or similar; fall back to 1:1 rather than dividing by zero
        factor = 1.0

    mm_per_unit = _viewbox_mm_per_unit(root)
    tol = (
        _GEOM_TOL_MM / mm_per_unit if mm_per_unit else _GEOM_TOL_MM
    )  # tolerance in user units

    def to_user(v: float) -> float:
        return v / factor

    closed: list[dict[str, Any]] = []  # filled shapes: bbox + id
    texts: list[dict[str, Any]] = []  # estimated text bbox + label
    arrows: list[dict[str, Any]] = []  # marker-end tip point + label
    skipped_texts = 0
    skipped_images = 0  # <text> whose bbox could not be resolved
    skipped_arrows = 0  # marker-end element whose tip could not be resolved
    simple_closed_types = (Rect, Circle, Ellipse, Polygon)

    def _is_closed_path(el) -> bool:  # type: ignore[no-untyped-def]
        """A <path> counts as a closed shape (bbox target for text/arrow checks)
        when its data ends in a close-path command. svgelements normalizes the
        command casing on reify, so 'z'/'Z' both surface as an uppercase 'Z'."""
        try:
            d = el.d()
        except Exception:  # noqa: BLE001 - malformed path data must not abort the report
            return False
        return d.strip().upper().endswith("Z")

    for e in doc.elements():
        if isinstance(e, Text):
            raw = (e.text or "").strip()
            fs = float(getattr(e, "font_size", 0) or 0)
            if not raw or fs <= 0:
                continue
            try:
                bx = e.bbox()
            except Exception:  # noqa: BLE001
                bx = None
            if not bx:
                skipped_texts += 1
                continue
            ax, ay = to_user(bx[0]), to_user(bx[1])
            texts.append({"bbox": _text_bbox(e, ax, ay, fs, raw), "text": raw})
            continue
        if isinstance(e, Image):
            # Image.bbox() reports (0, 0, 0, 0) until the pixel data has been
            # decoded (needed to resolve preserveAspectRatio); load it first so
            # an ai-full-figure substrate is treated as a real shape, not skipped.
            try:
                e.load()
                bx = e.bbox()
            except Exception:  # noqa: BLE001 - missing Pillow or undecodable data
                bx = None
            if not (bx and any(bx)):
                skipped_images += 1
                continue
            if bx and any(bx):
                closed.append(
                    {
                        "bbox": tuple(to_user(v) for v in bx),
                        "id": e.values.get("id") or "image",
                    }
                )
            continue
        try:
            bx = e.bbox()
        except Exception:  # noqa: BLE001
            bx = None
        marker_end = e.values.get("marker-end") if hasattr(e, "values") else None
        if marker_end:
            try:  # the tip is the path end; svgelements exposes it as point(1)
                tip = e.point(1)
                arrows.append(
                    {
                        "tip": (to_user(tip.x), to_user(tip.y)),
                        "label": e.values.get("id") or "arrow",
                    }
                )
            except Exception:  # noqa: BLE001
                skipped_arrows += 1
        if isinstance(e, simple_closed_types) and bx:
            closed.append(
                {
                    "bbox": tuple(to_user(v) for v in bx),
                    "id": e.values.get("id") or type(e).__name__.lower(),
                }
            )
        elif isinstance(e, Path) and bx and _is_closed_path(e):
            closed.append(
                {
                    "bbox": tuple(to_user(v) for v in bx),
                    "id": e.values.get("id") or "path",
                }
            )

    # 1. Text bleeding out of every shape it overlaps.
    text_overflow = []
    for t in texts:
        tb = t["bbox"]
        overlapped = [c for c in closed if _overlaps(tb, c["bbox"])]
        if overlapped and not any(_contains(c["bbox"], tb, tol) for c in overlapped):
            nearest = min(overlapped, key=lambda c: _bbox_gap(tb, c["bbox"]))
            text_overflow.append(
                {
                    "text": t["text"][:60],
                    "text_bbox": [round(v, 2) for v in tb],
                    "container_id": nearest["id"],
                    "container_bbox": [round(v, 2) for v in nearest["bbox"]],
                }
            )

    # 2. Arrow tips that miss every closed target shape. When arrows exist but no closed
    # target shapes were found (e.g. targets drawn as open <path> boxes), the check cannot
    # run; report that instead of returning a falsely-clean result.
    arrow_tip_issues = []
    arrows_without_targets = len(arrows) if arrows and not closed else 0
    if closed and arrows:
        targets = [shapely_box(*c["bbox"]) for c in closed]
        for a in arrows:
            pt = Point(a["tip"])
            dist = min(pt.distance(poly) for poly in targets)
            if dist > tol:
                arrow_tip_issues.append(
                    {
                        "label": a["label"],
                        "tip": [round(a["tip"][0], 2), round(a["tip"][1], 2)],
                        "distance_to_nearest_target": round(dist, 2),
                        "distance_mm": round(dist * mm_per_unit, 2),
                    }
                )

    # 3. Sibling closed shapes whose bboxes collide (partial overlap, no containment).
    bbox_overlaps = []
    for i in range(len(closed)):
        for j in range(i + 1, len(closed)):
            a, b = closed[i]["bbox"], closed[j]["bbox"]
            if not _overlaps(a, b):
                continue
            if _contains(a, b, tol) or _contains(b, a, tol):
                continue  # intentional containment (icon over background, label in panel)
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > tol and oy > tol:  # meaningful 2-D collision, not an edge graze
                bbox_overlaps.append(
                    {
                        "a_id": closed[i]["id"],
                        "b_id": closed[j]["id"],
                        "overlap_user": [round(ox, 2), round(oy, 2)],
                    }
                )

    return {
        "available": True,
        "text_count": len(texts),
        "shape_count": len(closed),
        "skipped_texts": skipped_texts,
        "skipped_images": skipped_images,
        "skipped_arrows": skipped_arrows,
        "arrows_without_targets": arrows_without_targets,
        "units": {
            "mm_per_user_unit": round(mm_per_unit, 4),
            "tolerance_mm": _GEOM_TOL_MM,
        },
        "text_overflow": text_overflow,
        "arrow_tip_issues": arrow_tip_issues,
        "bbox_overlaps": bbox_overlaps,
        "text_overflow_method": "font-size estimate (heuristic); use svg-primitives for exact text-fit",
    }


def check_svg(
    svg_path: Path, journal: str | None, palette: str | None
) -> dict[str, Any]:
    """Top-level entry point. Raises FileNotFoundError / lxml.etree.XMLSyntaxError on bad input."""
    from lxml import etree  # type: ignore[import-not-found]

    tree = etree.parse(str(svg_path))
    root = tree.getroot()
    theme_lib = _load_theme_lib()

    return {
        "input": str(svg_path),
        "checks": {
            "fonts": _validate_fonts(svg_path, journal),
            "palette": _palette_compliance(root, palette, theme_lib),
            "geometry": _bbox_overlaps_and_arrow_geometry(root, svg_path),
        },
    }


def _summarize(report: dict[str, Any]) -> tuple[int, int, int]:
    """Return (issue_count, warning_count, script_error_count) across all sections.
    A section with `error` set (e.g., a subprocess crashed) is counted as a
    script error so main() can exit 2 rather than 0 when a check itself fails."""
    issues = 0
    warnings = 0
    script_errors = 0
    fonts = (report.get("checks") or {}).get("fonts")
    if fonts and fonts.get("available") is not False:
        if fonts.get("error"):
            script_errors += 1
        else:
            issues += int(fonts.get("issue_count") or 0)
            warnings += int(fonts.get("skipped_count") or 0)
    palette = (report.get("checks") or {}).get("palette")
    if palette and palette.get("available"):
        if palette.get("error"):
            script_errors += 1
        else:
            issues += int(palette.get("off_palette_count") or 0)
    geom = (report.get("checks") or {}).get("geometry")
    if geom and geom.get("available"):
        if geom.get("error"):
            script_errors += 1
        else:
            issues += len(geom.get("bbox_overlaps") or [])
            issues += len(geom.get("arrow_tip_issues") or [])
            issues += len(geom.get("text_overflow") or [])
            # Elements that could not be measured (or arrows with no target shape) are
            # warnings, not clean: the agent should cover them with VLM judgment.
            warnings += int(geom.get("skipped_texts") or 0)
            warnings += int(geom.get("skipped_images") or 0)
            warnings += int(geom.get("skipped_arrows") or 0)
            warnings += int(geom.get("arrows_without_targets") or 0)
    return issues, warnings, script_errors


def _findings_from_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize every check section into the shared finding shape used by
    both check_svg.py and check_raster.py's --json output."""
    findings: list[dict[str, Any]] = []
    checks = report.get("checks", {})

    fonts = checks.get("fonts")
    if fonts and fonts.get("available") is not False:
        if fonts.get("error"):
            findings.append(
                {
                    "check": "fonts",
                    "severity": "block",
                    "message": fonts["error"],
                    "action": "none",
                    "hint": None,
                }
            )
        else:
            for issue in fonts.get("issues") or []:
                findings.append(
                    {
                        "check": "font_too_small",
                        "severity": "block",
                        "message": (
                            f"'{issue.get('text', '')}' measures {issue.get('effective_pt')} pt, "
                            f"below the {issue.get('minimum_pt')} pt minimum"
                        ),
                        "action": "rescale",
                        "hint": "increase font-size or route the label through svg-primitives auto-fit text",
                    }
                )

    palette = checks.get("palette")
    if palette is not None:
        if palette.get("error"):
            findings.append(
                {
                    "check": "palette",
                    "severity": "block",
                    "message": palette["error"],
                    "action": "none",
                    "hint": None,
                }
            )
        elif palette.get("available") is False:
            findings.append(
                {
                    "check": "palette",
                    "severity": "warn",
                    "message": palette["reason"],
                    "action": "none",
                    "hint": "pass a known preset or a valid theme.json path",
                }
            )
        else:
            for off in palette.get("off_palette", []):
                findings.append(
                    {
                        "check": "palette_off",
                        "severity": "warn",
                        "message": f"color {off['color']} is {off['nearest_distance']} from the nearest palette color",
                        "action": "recolor",
                        "hint": None,
                    }
                )

    geom = checks.get("geometry")
    if geom and geom.get("available"):
        if geom.get("error"):
            findings.append(
                {
                    "check": "geometry",
                    "severity": "block",
                    "message": geom["error"],
                    "action": "none",
                    "hint": None,
                }
            )
        else:
            for item in geom.get("text_overflow", []):
                findings.append(
                    {
                        "check": "text_overflow",
                        "severity": "warn",
                        "message": f"text '{item['text']}' overflows container {item['container_id']}",
                        "action": "edit",
                        "hint": "shrink the label or widen its container",
                    }
                )
            for item in geom.get("arrow_tip_issues", []):
                findings.append(
                    {
                        "check": "arrow_tip_miss",
                        "severity": "warn",
                        "message": f"arrow '{item['label']}' tip is {item['distance_mm']} mm from its nearest target",
                        "action": "edit",
                        "hint": "snap the arrow endpoint to the target shape's edge",
                    }
                )
            for item in geom.get("bbox_overlaps", []):
                findings.append(
                    {
                        "check": "bbox_overlap",
                        "severity": "warn",
                        "message": f"shapes '{item['a_id']}' and '{item['b_id']}' overlap",
                        "action": "overlay",
                        "hint": "reposition or resize one of the overlapping shapes",
                    }
                )
            if geom.get("arrows_without_targets"):
                findings.append(
                    {
                        "check": "arrow_without_target",
                        "severity": "info",
                        "message": f"{geom['arrows_without_targets']} arrow(s) point at a shape the checker could not resolve",
                        "action": "none",
                        "hint": "close the target <path> or verify manually",
                    }
                )
        if int(geom.get("skipped_images") or 0):
            findings.append(
                {
                    "check": "image_unmeasured",
                    "severity": "warn",
                    "message": (
                        f"{geom['skipped_images']} <image> element(s) could not be decoded; "
                        "run with --with pillow so substrates count as shapes"
                    ),
                    "action": "none",
                    "hint": "Re-run check_svg.py with --with pillow.",
                }
            )

    return findings


def _status_and_exit(findings: list[dict[str, Any]]) -> tuple[str, int]:
    severities = {f["severity"] for f in findings}
    if "block" in severities:
        return "block", 2
    if "warn" in severities:
        return "revise", 1
    return "ship", 0


def _build_envelope(report: dict[str, Any], journal: str | None) -> dict[str, Any]:
    findings = _findings_from_report(report)
    status, _ = _status_and_exit(findings)
    return {
        "file": report["input"],
        "type": "svg",
        "journal": journal,
        "status": status,
        "findings": findings,
        "measurements": report["checks"],
    }


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
        help=f"Color preset name ({sorted(ALLOWED_PALETTES)}) or a path to a theme.json.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the unified finding envelope (shared with check_raster.py) instead of the per-check report.",
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
            f"--with lxml --with svgelements --with shapely: {exc}",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:  # noqa: BLE001 - malformed XML or other parser failures; name it, don't crash
        print(
            f"error ({type(exc).__name__}): could not analyze '{args.svg}': {exc}",
            file=sys.stderr,
        )
        return 2

    issues, warnings, script_errors = _summarize(report)
    report["summary"] = {
        "issue_count": issues,
        "warning_count": warnings,
        "script_error_count": script_errors,
    }

    envelope = _build_envelope(report, args.journal)
    status, exit_code = _status_and_exit(envelope["findings"])
    if args.json:
        json.dump(envelope, sys.stdout, indent=2)
        print(file=sys.stdout)
    else:
        json.dump(report, sys.stdout, indent=2)
        print(file=sys.stdout)

    # The exit code follows the same severity model as the JSON status, so a
    # caller gating on either sees one answer: 0 ship, 1 revise, 2 block.
    if script_errors:
        print(
            f"check_svg: {script_errors} section(s) failed to run; see report.",
            file=sys.stderr,
        )
        return 2
    print(
        f"check_svg: {status} ({issues} issue(s), {warnings} warning(s)).",
        file=sys.stderr,
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
