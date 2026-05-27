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

# Make `svg_primitives` importable in the test process. The package lives in
# scripts/ next to tests/. Examples/ also adds itself to sys.path; we mirror
# that here so we can import the examples' build() helpers.
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

    Returns a list of (text_content, bbox) tuples.
    """
    if layer is None:
        return []
    from svg_primitives.metrics import measure_text_mm, MM_PER_PT  # type: ignore

    out: list[tuple[str, Bbox]] = []
    for t in layer.iter(f"{{{SVG_NS}}}text"):
        content = (t.text or "").strip()
        if not content:
            continue
        # font-size emitted in mm by Canvas.
        fs_mm_raw = t.get("font-size", "0")
        try:
            fs_mm = float(fs_mm_raw)
        except ValueError:
            fs_mm = 0.0
        if fs_mm <= 0:
            continue
        # Re-measure using the same metrics module (in pt, then to mm).
        fs_pt = fs_mm / MM_PER_PT
        text_w_mm, text_h_mm = measure_text_mm(content, fs_pt, font_path)
        # text-anchor=middle, baseline-ish y is at the dw.Text's y attr.
        cx = float(t.get("x", "0"))
        baseline_y = float(t.get("y", "0"))
        # Reverse the 0.78*single_h baseline offset used in shapes._render_text:
        # the drawn baseline sits 0.78*single_h below the visual top of the
        # first line. Approximate visual top as baseline - 0.78 * text_h.
        top = baseline_y - 0.78 * text_h_mm
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


@pytest.fixture
def render_canvas(tmp_path):
    """Save a Canvas to tmp_path/{name}.svg and return its Path."""
    def _save(canvas, name: str = "test") -> Path:
        out = tmp_path / f"{name}.svg"
        canvas.save(out)
        return out
    return _save
