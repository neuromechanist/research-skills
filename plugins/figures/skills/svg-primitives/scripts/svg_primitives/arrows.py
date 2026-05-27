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

from dataclasses import dataclass
from typing import Literal

import drawsvg as dw
from svgpathtools import CubicBezier, Line, Path

from .geometry import first_intersect_point, first_intersect_t
from .shapes import LabeledBox, Side

Curve = Literal["straight", "cubic"]
AutoSide = Literal["auto", "N", "S", "E", "W"]


def _auto_side(a: LabeledBox, b: LabeledBox) -> Side:
    """Pick the side of `a` that faces `b`."""
    dx = b.cx - a.cx
    dy = b.cy - a.cy
    if abs(dx) > abs(dy):
        return "E" if dx > 0 else "W"
    return "S" if dy > 0 else "N"


@dataclass
class Arrow:
    """A drawable arrow path with a marker-end arrowhead.

    Construct via `Arrow.connect(src, dst, ...)` rather than the bare
    constructor — `connect` handles endpoint snapping and curve geometry.
    """

    d: str  # SVG path "d" attribute
    stroke: str = "#1F3A5F"
    stroke_width: float = 0.6

    # Set by Canvas before rendering. Sentinel attribute lets Canvas
    # discover Arrow elements without importing this module.
    _is_arrow: bool = True
    _marker_url: str = "url(#arrow-default)"

    @classmethod
    def connect(
        cls,
        src: LabeledBox,
        dst: LabeledBox,
        *,
        curve: Curve = "straight",
        src_side: AutoSide = "auto",
        dst_side: AutoSide = "auto",
        bow: float = 0.0,
        stroke: str = "#1F3A5F",
        stroke_width: float = 0.6,
    ) -> "Arrow":
        if src_side == "auto":
            src_side = _auto_side(src, dst)
        if dst_side == "auto":
            dst_side = _auto_side(dst, src)
        p0 = src.anchor_point(src_side)
        p1 = dst.anchor_point(dst_side)

        if curve == "straight":
            line = Path(Line(p0, p1))
            p0_snap = first_intersect_point(line, src.outline_path(), prefer="start") or p0
            p1_snap = first_intersect_point(line, dst.outline_path(), prefer="end") or p1
            d = f"M {p0_snap.real:.3f} {p0_snap.imag:.3f} L {p1_snap.real:.3f} {p1_snap.imag:.3f}"
        elif curve == "cubic":
            chord = p1 - p0
            length = abs(chord)
            if length == 0:
                d = f"M {p0.real:.3f} {p0.imag:.3f}"
            else:
                # Convention: positive bow = upward in SVG (negative y),
                # negative bow = downward. We flip the perpendicular if
                # needed so this holds regardless of chord direction.
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
                trimmed = bez.cropped(t0, t1)
                d = (
                    f"M {trimmed.start.real:.3f} {trimmed.start.imag:.3f} "
                    f"C {trimmed.control1.real:.3f} {trimmed.control1.imag:.3f}, "
                    f"{trimmed.control2.real:.3f} {trimmed.control2.imag:.3f}, "
                    f"{trimmed.end.real:.3f} {trimmed.end.imag:.3f}"
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
