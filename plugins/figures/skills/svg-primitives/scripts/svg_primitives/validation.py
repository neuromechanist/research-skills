"""In-skill SVG validation.

The same geometric invariants that the E2E test suite checks (text bbox
inside container, arrow tip near target edge, marker orient=auto, no
unexpected sibling-shape overlap) are exposed here as a public module
that `Canvas.save(validate=...)` and `Canvas.validate()` call into.

Each check returns a list of `Finding`s. `validate_all` concatenates
them; `ValidationError` wraps a non-empty list for `strict` mode.

The geometry helpers (Bbox, rect_bboxes, text_bboxes, dist_to_rect_edge,
arrow_paths, marker_fill, all_markers, get_layer, parse_svg,
path_endpoint, marker_id_from_url, get_layer_ids_in_order) live here
so they are shared between the validators and the test conftest.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Literal

from .shapes import BASELINE_ASCENT_FRACTION

log = logging.getLogger(__name__)

SVG_NS = "http://www.w3.org/2000/svg"

ValidationCategory = Literal[
    "text-overflow",
    "arrow-tip-distance",
    "marker-orient",
    "sibling-overlap",
]


@dataclass(frozen=True)
class Finding:
    """One validation finding. Returned by every validator; raised by
    ValidationError in `strict` mode."""

    category: ValidationCategory
    message: str
    element_id: str | None = None
    location: tuple[float, float] | None = None  # mm

    def __str__(self) -> str:
        loc = f" at ({self.location[0]:.2f}, {self.location[1]:.2f}) mm" if self.location else ""
        eid = f" [{self.element_id}]" if self.element_id else ""
        return f"[{self.category}]{eid}{loc} {self.message}"


class ValidationError(Exception):
    """Raised by `Canvas.save(validate='strict')` when validation produces
    one or more findings. The full list is on `self.findings` (a tuple, so
    `str(error)` does not go stale if the caller later mutates a local copy)."""

    def __init__(self, findings: list[Finding] | tuple[Finding, ...]) -> None:
        self.findings: tuple[Finding, ...] = tuple(findings)
        super().__init__(self._format())

    def _format(self) -> str:
        if not self.findings:
            return "ValidationError raised with no findings (programming bug)."
        header = f"{len(self.findings)} validation finding(s):"
        body = "\n".join(f"  - {f}" for f in self.findings)
        return f"{header}\n{body}"


# ---------------------------------------------------------------------------
# Geometry value type
# ---------------------------------------------------------------------------


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

    def overlaps(self, other: "Bbox", tol: float = 0.0) -> bool:
        """True iff bbox interiors overlap by more than `tol` in both axes."""
        return (
            self.left + tol < other.right
            and self.right - tol > other.left
            and self.top + tol < other.bottom
            and self.bottom - tol > other.top
        )


# ---------------------------------------------------------------------------
# SVG parsing helpers (lxml-based, lazy import so the module loads even
# without lxml available — validators that need it raise at call time)
# ---------------------------------------------------------------------------


def parse_svg(path_or_text):
    """Parse an SVG from a path-like (str/Path/file) or an XML string.

    Strips a UTF-8 BOM if present before deciding XML-vs-path; without the
    strip, a BOM-prefixed string falls through to the path branch and
    raises an opaque OSError.
    """
    try:
        from lxml import etree
    except ImportError as e:
        raise RuntimeError(
            "svg-primitives validation requires lxml. Install with: "
            "uv add lxml, or include `--with lxml` on the uv run line."
        ) from e
    if hasattr(path_or_text, "read"):
        return etree.parse(path_or_text).getroot()
    if isinstance(path_or_text, str):
        stripped = path_or_text.lstrip("﻿ \t\n\r")
        if stripped.startswith("<"):
            return etree.fromstring(stripped.encode("utf-8"))
    return etree.parse(str(path_or_text)).getroot()


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
    """All <rect> bboxes in `layer` (in mm). Returns empty list when layer is None."""
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
        if w >= 0 and h >= 0:
            out.append(Bbox(x, y, w, h))
    return out


def diamond_bboxes(layer) -> list[Bbox]:
    """Diamond paths emit as `<path d="M ... Z"/>`. Return the bounding box
    derived from the path's M/L vertices (excluding marker-end paths which
    are arrows, not diamonds)."""
    if layer is None:
        return []
    out: list[Bbox] = []
    for el in layer.iter(f"{{{SVG_NS}}}path"):
        if el.get("marker-end"):
            continue
        d = el.get("d", "")
        if not d or "Z" not in d:
            continue
        cleaned = (d
            .replace("M", " ").replace("L", " ").replace("Z", " ")
            .replace(",", " "))
        nums: list[float] = []
        for token in cleaned.split():
            try:
                nums.append(float(token))
            except ValueError:
                continue
        xs = nums[0::2]
        ys = nums[1::2]
        if xs and ys:
            out.append(Bbox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)))
    return out


def text_bboxes(layer, font_path: str | None = None) -> list[tuple[str, Bbox, str | None]]:
    """Approximate bbox for every <text> in `layer`. Uses the svg_primitives
    metrics module so the bbox computation is consistent with how shapes
    were sized at construction time. Returns (text_content, bbox, id) tuples.
    """
    if layer is None:
        return []
    from .metrics import MM_PER_PT, measure_text_mm

    out: list[tuple[str, Bbox, str | None]] = []
    skipped: list[str] = []
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
        if text_w_mm <= 0 or text_h_mm <= 0:
            skipped.append(content)
            continue
        cx = float(t.get("x", "0"))
        baseline_y = float(t.get("y", "0"))
        top = baseline_y - BASELINE_ASCENT_FRACTION * text_h_mm
        out.append((content, Bbox(cx - text_w_mm / 2, top, text_w_mm, text_h_mm), t.get("id")))
    if skipped:
        log.warning(
            "text_bboxes: metrics returned zero size for %d text element(s) %r — "
            "excluded from containment checks (likely the heuristic font fallback is active; "
            "install a system font or pass strict_metrics=True to surface this earlier)",
            len(skipped), skipped[:3],
        )
    return out


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


def all_markers(root) -> list:
    """Return all <marker> elements in the SVG."""
    return list(root.iter(f"{{{SVG_NS}}}marker"))


def marker_fill(marker_el) -> str:
    """Return the fill of the first child of the marker (the triangle)."""
    for child in marker_el.iter():
        f = child.get("fill")
        if f and f.lower() not in ("none", ""):
            return f.lower()
    return ""


def marker_id_from_url(url_value: str) -> str:
    """Extract `arrow-foo` from `url(#arrow-foo)`."""
    s = url_value.strip()
    if s.startswith("url(#") and s.endswith(")"):
        return s[len("url(#"):-1]
    return s


def path_endpoint(path_d: str) -> tuple[float, float]:
    """Terminal point of the path via svgpathtools."""
    try:
        from svgpathtools import parse_path
    except ImportError as e:
        raise RuntimeError(
            "svg-primitives validation requires svgpathtools. Install with: "
            "uv add svgpathtools, or include `--with svgpathtools` on the uv run line."
        ) from e
    p = parse_path(path_d)
    end = p.end
    return (end.real, end.imag)


def dist_to_rect_edge(pt: tuple[float, float], box: Bbox) -> float:
    """Distance from `pt` to the bounding rect. Points inside the box return
    0 (treated as on the shape); points outside return the Euclidean
    distance to the nearest edge.

    Earlier this returned the *interior* distance to the nearest edge for
    points inside the box, which made `validate_arrow_tip_distance` flag
    arrows whose tips landed inside a target by more than tol — that's
    geometrically on-target, not off it.
    """
    x, y = pt
    dx = max(box.left - x, 0, x - box.right)
    dy = max(box.top - y, 0, y - box.bottom)
    if dx == 0 and dy == 0:
        return 0.0
    return (dx * dx + dy * dy) ** 0.5


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def _layer_groups(root) -> Iterator:
    """Yield direct <g id='layer-*'> children of the root."""
    for el in root:
        if el.tag == f"{{{SVG_NS}}}g":
            gid = el.get("id", "")
            if gid.startswith("layer-"):
                yield el


def validate_text_containment(root, *, tol: float = 0.5) -> list[Finding]:
    """Every <text> element should sit inside at least one shape (rect or
    diamond) in the same layer. Texts whose bbox extends beyond their
    container by more than `tol` mm produce a finding."""
    findings: list[Finding] = []
    for layer in _layer_groups(root):
        containers = rect_bboxes(layer) + diamond_bboxes(layer)
        if not containers:
            continue
        for content, tb, tid in text_bboxes(layer):
            if any(c.contains(tb, tol=tol) for c in containers):
                continue
            findings.append(Finding(
                category="text-overflow",
                message=f"text {content!r} bbox {tb} extends beyond every shape in {layer.get('id')!r}",
                element_id=tid,
                location=(tb.x + tb.w / 2, tb.y + tb.h / 2),
            ))
    return findings


def validate_arrow_tip_distance(root, *, tol: float = 0.6) -> list[Finding]:
    """Every arrow (path/line with marker-end) should terminate within `tol`
    mm of some rect or diamond outline in the SVG. Tips farther away from
    any candidate target produce a finding."""
    findings: list[Finding] = []
    candidates: list[Bbox] = []
    for layer in _layer_groups(root):
        candidates.extend(rect_bboxes(layer))
        candidates.extend(diamond_bboxes(layer))
    if not candidates:
        return findings
    for layer in _layer_groups(root):
        for arrow in arrow_paths(layer):
            d = arrow.get("d", "")
            if not d and arrow.tag == f"{{{SVG_NS}}}line":
                x2 = arrow.get("x2")
                y2 = arrow.get("y2")
                if x2 is None or y2 is None:
                    continue
                tip = (float(x2), float(y2))
            elif d:
                try:
                    tip = path_endpoint(d)
                except (ValueError, AttributeError, IndexError) as exc:
                    # Only swallow expected svgpathtools parse failures. Log
                    # the truncated d so a real path-emission bug doesn't
                    # silently suppress findings for every arrow.
                    log.warning(
                        "validate_arrow_tip_distance: could not parse path d=%r: %s",
                        d[:80], exc,
                    )
                    continue
            else:
                continue
            nearest = min(dist_to_rect_edge(tip, c) for c in candidates)
            if nearest > tol:
                findings.append(Finding(
                    category="arrow-tip-distance",
                    message=f"arrow tip {nearest:.3f} mm from nearest target edge (tol={tol})",
                    element_id=arrow.get("id"),
                    location=tip,
                ))
    return findings


def validate_marker_orient(root) -> list[Finding]:
    """Every <marker> in the SVG should use orient='auto'. Marker elements
    with explicit angles or missing orient indicate a hand-rotated triangle
    that won't track the path tangent."""
    findings: list[Finding] = []
    for m in all_markers(root):
        orient = m.get("orient", "")
        if orient != "auto":
            findings.append(Finding(
                category="marker-orient",
                message=f"marker uses orient={orient!r}, expected 'auto'",
                element_id=m.get("id"),
            ))
    return findings


def validate_sibling_overlap(
    root, *, tol: float = 0.0, ignore_layers: tuple[str, ...] = ("background",),
) -> list[Finding]:
    """Within each layer, no two rects should overlap by more than `tol`
    mm in both axes. The `background` layer is skipped by default so a
    canvas background rect doesn't trigger findings against every shape."""
    findings: list[Finding] = []
    for layer in _layer_groups(root):
        layer_name = layer.get("id", "").replace("layer-", "", 1)
        if layer_name in ignore_layers:
            continue
        rects = rect_bboxes(layer)
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if rects[i].overlaps(rects[j], tol=tol):
                    findings.append(Finding(
                        category="sibling-overlap",
                        message=f"two rects in layer {layer_name!r} overlap",
                        location=(rects[i].x, rects[i].y),
                    ))
    return findings


def validate_all(
    root,
    *,
    text_tol: float = 0.5,
    arrow_tol: float = 0.6,
    overlap_tol: float = 0.0,
    ignore_overlap_layers: tuple[str, ...] = ("background",),
) -> list[Finding]:
    """Run every validator on `root`. Returns the concatenated finding
    list (empty when the SVG is clean)."""
    return [
        *validate_text_containment(root, tol=text_tol),
        *validate_arrow_tip_distance(root, tol=arrow_tol),
        *validate_marker_orient(root),
        *validate_sibling_overlap(root, tol=overlap_tol, ignore_layers=ignore_overlap_layers),
    ]


__all__ = [
    "Bbox",
    "Finding",
    "ValidationCategory",
    "ValidationError",
    "validate_all",
    "validate_arrow_tip_distance",
    "validate_marker_orient",
    "validate_sibling_overlap",
    "validate_text_containment",
    # Geometry helpers used by tests / external callers:
    "all_markers",
    "arrow_paths",
    "diamond_bboxes",
    "dist_to_rect_edge",
    "get_layer",
    "get_layer_ids_in_order",
    "marker_fill",
    "marker_id_from_url",
    "parse_svg",
    "path_endpoint",
    "rect_bboxes",
    "text_bboxes",
]
