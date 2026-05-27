"""Arrow connector primitive.

Arrow.connect(src, dst, curve='straight'|'cubic', bow=N) returns an Arrow
whose path:

* Starts at the source box's anchor (defaults to the side facing the
  destination, override with `src_side`).
* Ends at the destination box's anchor (likewise).
* For straight arrows, snaps endpoints to the box outlines along the
  chord so the head tip kisses the visible edge.
* For cubic arrows, builds a Bezier with control points perpendicular
  to the chord at `bow` mm of bulge (positive = upward in SVG y),
  then crops the Bezier where it intersects each box outline.

The arrowhead is delivered via SVG `<marker orient='auto'>` set up by
Canvas at render time — the renderer computes the path tangent at the
endpoint and rotates the marker accordingly, so curved-path arrowheads
stay tangent-correct.

Per-color marker selection happens in Canvas (one marker per unique
stroke); Arrow only carries its stroke color via the `stroke` field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import drawsvg as dw
from svgpathtools import CubicBezier, Line, Path

from .geometry import first_intersect_point, first_intersect_t
from .shapes import Shape, Side

Curve = Literal["straight", "cubic", "orthogonal-h", "orthogonal-v"]
AutoSide = Literal["auto", "N", "S", "E", "W"]


def _auto_side(a: Shape, b: Shape) -> Side:
    """Pick the side of `a` that faces `b` (free orientation)."""
    dx = b.cx - a.cx
    dy = b.cy - a.cy
    if abs(dx) > abs(dy):
        return "E" if dx > 0 else "W"
    return "S" if dy > 0 else "N"


def _auto_side_orthogonal(a: Shape, b: Shape, axis: Literal["h", "v"]) -> Side:
    """For orthogonal routing, force the auto-side onto the primary-traverse
    axis ('h' → E/W, 'v' → N/S). If `b` is aligned with `a` on that axis (so
    the strict comparison would be ambiguous), fall back to the perpendicular
    axis so the path stays coherent instead of degenerating to W/W or N/N."""
    if axis == "h":
        if b.cx > a.cx:
            return "E"
        if b.cx < a.cx:
            return "W"
        return "S" if b.cy > a.cy else "N"
    if b.cy > a.cy:
        return "S"
    if b.cy < a.cy:
        return "N"
    return "E" if b.cx > a.cx else "W"


def _build_polyline_d(points: list[complex], corner_radius: float = 0.0) -> str:
    """Build an SVG path string from a list of polyline vertices.

    If `corner_radius > 0`, interior vertices are replaced with a quadratic
    Bezier corner of that radius (clamped to half the shorter adjoining
    segment so the rounding never overshoots). The path starts with M and
    chains L/Q segments.
    """
    if not points:
        return ""
    if corner_radius <= 0 or len(points) < 3:
        parts = [f"M {points[0].real:.3f} {points[0].imag:.3f}"]
        for p in points[1:]:
            parts.append(f"L {p.real:.3f} {p.imag:.3f}")
        return " ".join(parts)
    parts = [f"M {points[0].real:.3f} {points[0].imag:.3f}"]
    for i in range(1, len(points) - 1):
        prev, this, nxt = points[i - 1], points[i], points[i + 1]
        d_in = abs(this - prev)
        d_out = abs(nxt - this)
        # Treat near-zero segments as zero so we don't emit a degenerate Q
        # whose start point equals its control point.
        if d_in < 1e-9 or d_out < 1e-9:
            parts.append(f"L {this.real:.3f} {this.imag:.3f}")
            continue
        r = min(corner_radius, d_in / 2, d_out / 2)
        in_dir = (this - prev) / d_in
        out_dir = (nxt - this) / d_out
        c_in = this - in_dir * r
        c_out = this + out_dir * r
        parts.append(f"L {c_in.real:.3f} {c_in.imag:.3f}")
        parts.append(f"Q {this.real:.3f} {this.imag:.3f} {c_out.real:.3f} {c_out.imag:.3f}")
    last = points[-1]
    parts.append(f"L {last.real:.3f} {last.imag:.3f}")
    return " ".join(parts)


@dataclass
class Arrow:
    """A drawable arrow path with a marker-end arrowhead.

    Construct via `Arrow.connect(src, dst, ...)` rather than the bare
    constructor — `connect` handles endpoint snapping and curve geometry.
    """

    d: str  # SVG path "d" attribute
    stroke: str = "#1F3A5F"
    stroke_width: float = 0.6

    # Private fields sealed from constructor: Canvas discovers Arrow
    # elements via the _is_arrow attribute (a sentinel to avoid the
    # arrows-imports-canvas circular dependency) and writes _marker_url
    # at render time so every arrow uses the marker matching its stroke.
    _is_arrow: bool = field(init=False, default=True, repr=False)
    _marker_url: str = field(init=False, default="url(#arrow-default)", repr=False)

    @classmethod
    def connect(
        cls,
        src: Shape,
        dst: Shape,
        *,
        curve: Curve = "straight",
        src_side: AutoSide = "auto",
        dst_side: AutoSide = "auto",
        bow: float = 0.0,
        via: list[tuple[float, float]] | None = None,
        corner_radius: float = 0.0,
        stroke: str = "#1F3A5F",
        stroke_width: float = 0.6,
    ) -> "Arrow":
        if curve in ("orthogonal-h", "orthogonal-v"):
            if via:
                raise ValueError(
                    f"'via' waypoints are not supported with curve={curve!r}; "
                    "use curve='straight' for multi-waypoint paths."
                )
            axis: Literal["h", "v"] = "h" if curve == "orthogonal-h" else "v"
            if src_side == "auto":
                src_side = _auto_side_orthogonal(src, dst, axis)
            if dst_side == "auto":
                dst_side = _auto_side_orthogonal(dst, src, axis)
        else:
            if src_side == "auto":
                src_side = _auto_side(src, dst)
            if dst_side == "auto":
                dst_side = _auto_side(dst, src)
        p0 = src.anchor_point(src_side)
        p1 = dst.anchor_point(dst_side)

        if abs(p1 - p0) == 0:
            raise ValueError(
                f"Arrow.connect: src and dst anchor points are coincident at {p0}; "
                "cannot construct an arrow (consider different src_side/dst_side or non-overlapping boxes)."
            )

        if curve == "straight":
            waypoints = [complex(x, y) for x, y in (via or [])]
            # Snap p0 along the first segment direction; snap p1 along the
            # last segment direction. With no waypoints, both segments are
            # the same chord p0-p1 (original behavior).
            first_target = waypoints[0] if waypoints else p1
            last_source = waypoints[-1] if waypoints else p0
            first_seg = Path(Line(p0, first_target))
            last_seg = Path(Line(last_source, p1))
            p0_snap_opt = first_intersect_point(first_seg, src.outline_path(), prefer="start")
            p1_snap_opt = first_intersect_point(last_seg, dst.outline_path(), prefer="end")
            p0_snap = p0_snap_opt if p0_snap_opt is not None else p0
            p1_snap = p1_snap_opt if p1_snap_opt is not None else p1
            polyline = [p0_snap, *waypoints, p1_snap]
            d = _build_polyline_d(polyline, corner_radius=corner_radius)
        elif curve == "cubic":
            chord = p1 - p0
            length = abs(chord)
            # Convention: positive bow = upward in SVG (negative y), negative
            # bow = downward. Approximately holds for any chord direction; for
            # purely vertical chords positive bow bulges toward +x rather than
            # geometrically "up", which is a known limitation of using imag>0
            # as the orientation test.
            normal = complex(chord.imag, -chord.real) / length
            if normal.imag > 0:
                normal = -normal
            offset = normal * bow
            c1 = p0 + chord * 0.33 + offset
            c2 = p0 + chord * 0.67 + offset
            bez = CubicBezier(p0, c1, c2, p1)
            t0 = first_intersect_t(bez, src.outline_path(), prefer="start")
            t1 = first_intersect_t(bez, dst.outline_path(), prefer="end")
            t0 = t0 if t0 is not None else 0.0
            t1 = t1 if t1 is not None else 1.0
            # Overlapping boxes can produce t0 >= t1 (both intersections fall
            # on the same side of the Bezier); fall back to the untrimmed
            # curve rather than letting svgpathtools raise AssertionError.
            if t0 >= t1:
                t0, t1 = 0.0, 1.0
            trimmed = bez.cropped(t0, t1)
            d = (
                f"M {trimmed.start.real:.3f} {trimmed.start.imag:.3f} "
                f"C {trimmed.control1.real:.3f} {trimmed.control1.imag:.3f}, "
                f"{trimmed.control2.real:.3f} {trimmed.control2.imag:.3f}, "
                f"{trimmed.end.real:.3f} {trimmed.end.imag:.3f}"
            )
        elif curve == "orthogonal-h":
            # out horizontally from p0, vertical to p1.y at chord midpoint, in horizontally
            mid_x = (p0.real + p1.real) / 2
            d = (
                f"M {p0.real:.3f} {p0.imag:.3f} "
                f"L {mid_x:.3f} {p0.imag:.3f} "
                f"L {mid_x:.3f} {p1.imag:.3f} "
                f"L {p1.real:.3f} {p1.imag:.3f}"
            )
        elif curve == "orthogonal-v":
            mid_y = (p0.imag + p1.imag) / 2
            d = (
                f"M {p0.real:.3f} {p0.imag:.3f} "
                f"L {p0.real:.3f} {mid_y:.3f} "
                f"L {p1.real:.3f} {mid_y:.3f} "
                f"L {p1.real:.3f} {p1.imag:.3f}"
            )
        else:
            raise ValueError(f"unsupported curve: {curve!r}")
        return cls(d=d, stroke=stroke, stroke_width=stroke_width)

    def to_drawsvg(self) -> dw.Path:
        p = dw.Path(stroke=self.stroke, stroke_width=self.stroke_width, fill="none")
        p.args["d"] = self.d
        p.args["marker-end"] = self._marker_url
        return p


__all__ = ["Arrow", "Curve"]
