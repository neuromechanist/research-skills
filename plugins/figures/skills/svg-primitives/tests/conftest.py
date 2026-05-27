"""Shared fixtures and geometry helpers for the svg-primitives E2E tests.

Tests parse rendered SVGs with `lxml.etree` (for layer ordering and
attribute extraction) and `svgpathtools` (for path geometry — tangents,
intersections, endpoints). We deliberately do not use a headless browser
or a rasterizer: every assertion is computed from the SVG source.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pytest

# scripts/ and examples/ are not installed; add them to sys.path so the
# package and example build() helpers are importable in pytest.
_SKILL_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _SKILL_ROOT / "scripts"
_EXAMPLES = _SKILL_ROOT / "examples"
for p in (_SCRIPTS, _EXAMPLES):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


SVG_NS = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class Bbox:
    """Axis-aligned bounding box in mm."""
    x: float
    y: float
    w: float
    h: float

    def __post_init__(self) -> None:
        if self.w < 0 or self.h < 0:
            raise ValueError(
                f"Bbox dimensions must be non-negative: w={self.w}, h={self.h}"
            )

    @property
    def left(self) -> float: return self.x
    @property
    def right(self) -> float: return self.x + self.w
    @property
    def top(self) -> float: return self.y
    @property
    def bottom(self) -> float: return self.y + self.h

    def contains(self, other: "Bbox", tol: float = 0.0) -> bool:
        return (
            self.left - tol <= other.left
            and self.right + tol >= other.right
            and self.top - tol <= other.top
            and self.bottom + tol >= other.bottom
        )


def parse_svg(path: Path):
    """Return an lxml root element from an SVG file."""
    from lxml import etree
    return etree.parse(str(path)).getroot()


def get_layer(root, name: str):
    """Return the <g id='layer-{name}'> element or None."""
    return root.find(f"{{{SVG_NS}}}g[@id='layer-{name}']")


def get_layer_ids_in_order(root) -> list[str]:
    """Return the document-order list of layer ids (g[@id^='layer-'])."""
    ids: list[str] = []
    for el in root.iter(f"{{{SVG_NS}}}g"):
        gid = el.get("id", "")
        if gid.startswith("layer-"):
            ids.append(gid)
    return ids


def rect_bboxes(layer) -> list[Bbox]:
    """All <rect> bboxes in `layer` (in mm)."""
    if layer is None:
        return []
    out: list[Bbox] = []
    for r in layer.iter(f"{{{SVG_NS}}}rect"):
        try:
            x = float(r.get("x", "0"))
            y = float(r.get("y", "0"))
            w = float(r.get("width", "0"))
            h = float(r.get("height", "0"))
        except (TypeError, ValueError):
            continue
        out.append(Bbox(x, y, w, h))
    return out


def diamond_bboxes(layer) -> list[Bbox]:
    """Diamond shapes are emitted by drawsvg as `<path d='M ... Z'/>` (closed
    polyline). Match paths whose `d` attribute is a polyline-style sequence
    of M + L + ... + Z and compute the bbox from the endpoints.

    Note: `<path>` with `marker-end` are arrow paths, not diamonds; we
    exclude those here.
    """
    if layer is None:
        return []
    out: list[Bbox] = []
    for el in layer.iter(f"{{{SVG_NS}}}path"):
        if el.get("marker-end"):
            continue
        d = el.get("d", "")
        if not d or "Z" not in d:
            continue
        # Strip M/L/Z and split into x,y pairs.
        cleaned = (d
            .replace("M", " ").replace("L", " ").replace("Z", " ")
            .replace(",", " "))
        nums = [float(n) for n in cleaned.split() if n]
        xs = nums[0::2]
        ys = nums[1::2]
        if xs and ys:
            out.append(Bbox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)))
    return out


def text_bboxes(layer, font_path: str | None = None) -> list[tuple[str, Bbox]]:
    """Approximate bbox for every <text> in `layer`. Uses the same metrics
    module the primitives use, so containment checks are self-consistent.

    This is the "primary" containment check. To guard against the circular
    case where a metrics regression underestimates BOTH the box-fit and the
    test-measurement consistently, see `text_bboxes_pillow_independent`.

    Returns a list of (text_content, bbox) tuples.
    """
    if layer is None:
        return []
    from svg_primitives.metrics import measure_text_mm, MM_PER_PT  # type: ignore
    from svg_primitives.shapes import BASELINE_ASCENT_FRACTION  # type: ignore

    out: list[tuple[str, Bbox]] = []
    for t in layer.iter(f"{{{SVG_NS}}}text"):
        content = (t.text or "").strip()
        if not content:
            continue
        fs_mm_raw = t.get("font-size", "0")
        try:
            fs_mm = float(fs_mm_raw)
        except ValueError:
            fs_mm = 0.0
        if fs_mm <= 0:
            continue
        fs_pt = fs_mm / MM_PER_PT
        text_w_mm, text_h_mm = measure_text_mm(content, fs_pt, font_path)
        cx = float(t.get("x", "0"))
        baseline_y = float(t.get("y", "0"))
        top = baseline_y - BASELINE_ASCENT_FRACTION * text_h_mm
        out.append((content, Bbox(cx - text_w_mm / 2, top, text_w_mm, text_h_mm)))
    return out


def text_bboxes_pillow_independent(layer) -> list[tuple[str, Bbox]]:
    """Independent text-bbox measurement using Pillow's ImageFont.getbbox at
    a high pixel size and rescaling, *without* touching the svg_primitives
    metrics module.

    Used by tests that need to verify the auto-fit boxes contain the text
    even if there is a systematic error in the metrics module — closes the
    circular-logic gap raised in PR #55 review.
    """
    if layer is None:
        return []
    from PIL import ImageFont

    # Resolve a system font once. We hardcode the macOS path for the dev
    # machine; CI can override via env var. If neither works, the test is
    # skipped (we cannot do an independent check without an independent font).
    import os
    font_path = os.environ.get("SVG_PRIMITIVES_TEST_FONT")
    if not font_path:
        for candidate in (
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ):
            if os.path.exists(candidate):
                font_path = candidate
                break
    if not font_path:
        return []  # caller will see an empty list and skip

    MEASURE_PX = 200
    try:
        font = ImageFont.truetype(font_path, size=MEASURE_PX, index=0)
    except (OSError, IOError):
        return []

    out: list[tuple[str, Bbox]] = []
    for t in layer.iter(f"{{{SVG_NS}}}text"):
        content = (t.text or "").strip()
        if not content:
            continue
        fs_mm_raw = t.get("font-size", "0")
        try:
            fs_mm = float(fs_mm_raw)
        except ValueError:
            fs_mm = 0.0
        if fs_mm <= 0:
            continue
        # 1 pt = 25.4/72 mm; SVG attribute is in mm; the rendered height is fs_mm.
        left, top_px, right, bottom = font.getbbox(content)
        width_px = right - left
        height_px = bottom - top_px
        if width_px <= 0 or height_px <= 0:
            continue
        scale = fs_mm / height_px
        text_w_mm = width_px * scale
        text_h_mm = fs_mm
        cx = float(t.get("x", "0"))
        baseline_y = float(t.get("y", "0"))
        # Best independent estimate of the visual top: subtract Pillow's
        # ascent (top_px is negative for above-baseline).
        ascent_mm = (-top_px) * scale if top_px < 0 else fs_mm * 0.78
        top = baseline_y - ascent_mm
        out.append((content, Bbox(cx - text_w_mm / 2, top, text_w_mm, text_h_mm)))
    return out


def path_endpoint(path_d: str) -> tuple[float, float]:
    """Return the (x, y) of the path's terminal point via svgpathtools."""
    from svgpathtools import parse_path
    p = parse_path(path_d)
    end = p.end
    return (end.real, end.imag)


def dist_to_rect_edge(pt: tuple[float, float], box: Bbox) -> float:
    """Distance from point `pt` to the nearest edge of `box`."""
    x, y = pt
    # Distance to each edge segment.
    dx = max(box.left - x, 0, x - box.right)
    dy = max(box.top - y, 0, y - box.bottom)
    if dx == 0 and dy == 0:
        # Inside the box: distance to nearest edge.
        return min(x - box.left, box.right - x, y - box.top, box.bottom - y)
    return (dx * dx + dy * dy) ** 0.5


def all_markers(root) -> list:
    """Return all <marker> elements in <defs>."""
    return list(root.iter(f"{{{SVG_NS}}}marker"))


def marker_fill(marker_el) -> str:
    """Return the fill of the first child polygon/lines under the marker."""
    for child in marker_el.iter():
        f = child.get("fill")
        if f and f.lower() not in ("none", ""):
            return f.lower()
    return ""


def arrow_paths(layer) -> Iterable:
    """Yield path elements in `layer` that carry a marker-end attribute."""
    if layer is None:
        return
    for el in layer.iter(f"{{{SVG_NS}}}path"):
        if el.get("marker-end"):
            yield el
    for el in layer.iter(f"{{{SVG_NS}}}line"):
        if el.get("marker-end"):
            yield el


def marker_id_from_url(url_value: str) -> str:
    """Extract `arrow-foo` from `url(#arrow-foo)`."""
    s = url_value.strip()
    if s.startswith("url(#") and s.endswith(")"):
        return s[len("url(#"):-1]
    return s


@pytest.fixture
def render_canvas(tmp_path):
    """Save a Canvas to tmp_path/{name}.svg and return its Path."""
    def _save(canvas, name: str = "test") -> Path:
        out = tmp_path / f"{name}.svg"
        canvas.save(out)
        return out
    return _save
