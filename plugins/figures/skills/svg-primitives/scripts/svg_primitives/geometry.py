"""svgpathtools-based geometry helpers.

The arrow trimming logic needs three things:

* Compute the intersection of an arrow path with a target box outline,
  so the arrow endpoint can be snapped to the visual box edge rather
  than the box's geometric center.
* Pick the "first" or "last" intersection — for the source endpoint we
  want the intersection nearest t=0; for the destination endpoint we
  want the one nearest t=1.
* Crop a cubic Bezier between two t parameters so the rendered path
  segment matches the trimmed visible segment.
"""

from __future__ import annotations

from typing import Literal

from svgpathtools import CubicBezier, Path

Prefer = Literal["start", "end"]


def first_intersect_point(p: Path, q: Path, prefer: Prefer = "start") -> complex | None:
    """Return the intersection point on `p` closest to t=0 (`prefer='start'`)
    or t=1 (`prefer='end'`), or None if `p` and `q` do not intersect.

    `Path.intersect` returns a list of tuples of the form
    `((T1, seg1, t1), (T2, seg2, t2))` where T1/T2 are global path-level
    parameters and t1/t2 are segment-local. We collect the points by
    evaluating `seg1.point(t1)` and sort by T1.
    """
    intersections = p.intersect(q)
    if not intersections:
        return None
    pts = [(T1, seg1.point(t1)) for (T1, seg1, t1), _ in intersections]
    pts.sort(key=lambda x: x[0])
    return pts[-1][1] if prefer == "end" else pts[0][1]


def first_intersect_t(bez: CubicBezier, q: Path, prefer: Prefer = "start") -> float | None:
    """For a single cubic Bezier, return the segment-local t in [0,1] at
    which it intersects `q`, picking nearest-to-start or nearest-to-end.

    Used by Arrow.connect to compute t0 and t1 for `bez.cropped(t0, t1)`
    when trimming a cubic against two box outlines.
    """
    path = Path(bez)
    intersections = path.intersect(q)
    if not intersections:
        return None
    ts = [t1 for (_T1, _seg, t1), _ in intersections]
    return max(ts) if prefer == "end" else min(ts)
