"""Annotation primitives: Bracket and Annotation.

These are non-geometry overlays (they do not contribute box outlines or
anchor points to the Shape protocol) — they render text and/or a thin
line and live in the same Canvas as the boxes/arrows.

Bracket:
  start ─┐
         │
         ├── label
         │
   end ─┘

  A square bracket (a "rake") whose spine sits `depth` mm perpendicular
  to the line from start to end, with an optional label centered at the
  apex plus `label_offset` mm further out.

Annotation:
  Text label at (x, y) with an optional leader line drawn from the text
  bounding box edge to a target coordinate. The leader is omitted if
  `leader_to` is None.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import drawsvg as dw

from .metrics import MM_PER_PT, measure_text_mm
from .shapes import BASELINE_ASCENT_FRACTION, _FONT_FAMILY_SVG  # noqa: F401


def _perp_unit(start: complex, end: complex) -> complex:
    """Unit vector perpendicular to start->end, rotated 90° CCW (in math
    coords; in SVG y-down this means turning left as you walk from start
    to end)."""
    chord = end - start
    length = abs(chord)
    if length == 0:
        return complex(0, -1)
    return complex(-chord.imag, chord.real) / length


@dataclass
class Bracket:
    """Square-style bracket primitive ("rake").

    The spine runs parallel to the start-end segment, offset by `depth` mm
    perpendicular to that segment. Positive `depth` puts the spine on the
    CCW (left) side of the start-end direction in math coordinates — which
    in SVG y-down means visually-up when start and end are horizontal.
    """

    start: tuple[float, float]
    end: tuple[float, float]
    depth: float                # mm; sign chooses which side
    label: str | None = None
    label_offset: float = 2.0   # mm beyond the spine apex
    font_size: float = 7.0      # pt
    stroke: str = "#1F3A5F"
    stroke_width: float = 0.6
    font_path: str | None = None
    strict_metrics: bool = False

    _start_c: complex = field(init=False, repr=False)
    _end_c: complex = field(init=False, repr=False)
    _normal: complex = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.font_size <= 0:
            raise ValueError(f"font_size must be positive, got {self.font_size}")
        self._start_c = complex(*self.start)
        self._end_c = complex(*self.end)
        self._normal = _perp_unit(self._start_c, self._end_c)

    def _spine_endpoints(self) -> tuple[complex, complex]:
        """Two corner points of the spine — directly opposite start and end."""
        offset = self._normal * self.depth
        return (self._start_c + offset, self._end_c + offset)

    def _apex(self) -> complex:
        """Midpoint of the spine; where the label sits perpendicular to."""
        a, b = self._spine_endpoints()
        return (a + b) / 2

    def _label_anchor(self) -> complex:
        # Push the label further in the same direction the spine is offset
        # from the start-end line so it sits on the closed side of the
        # bracket (away from the elements being grouped), regardless of
        # the sign of `depth`.
        if self.depth == 0:
            return self._apex()
        sign = 1 if self.depth > 0 else -1
        return self._apex() + self._normal * sign * self.label_offset

    def to_drawsvg(self) -> dw.Group:
        g = dw.Group()
        a, b = self._spine_endpoints()
        # Two tick marks (start->a and end->b) plus the spine (a->b).
        path_d = (
            f"M {self._start_c.real:.3f} {self._start_c.imag:.3f} "
            f"L {a.real:.3f} {a.imag:.3f} "
            f"L {b.real:.3f} {b.imag:.3f} "
            f"L {self._end_c.real:.3f} {self._end_c.imag:.3f}"
        )
        p = dw.Path(stroke=self.stroke, stroke_width=self.stroke_width, fill="none")
        p.args["d"] = path_d
        g.append(p)
        if self.label:
            anchor = self._label_anchor()
            fs_mm = self.font_size * MM_PER_PT
            _, h = measure_text_mm(self.label, self.font_size, self.font_path, self.strict_metrics)
            # Place the text baseline so the visual center sits at anchor.
            baseline_y = anchor.imag + h * (BASELINE_ASCENT_FRACTION - 0.5)
            g.append(dw.Text(
                self.label, x=anchor.real, y=baseline_y,
                font_size=fs_mm, font_family=_FONT_FAMILY_SVG,
                text_anchor="middle", fill=self.stroke,
            ))
        return g


@dataclass
class Annotation:
    """Text label at (x, y) with an optional leader line to a target point."""

    x: float
    y: float
    text: str
    leader_to: tuple[float, float] | None = None
    font_size: float = 7.0      # pt
    text_anchor: Literal["start", "middle", "end"] = "middle"
    fill: str = "#1F3A5F"
    leader_stroke: str = "#1F3A5F"
    leader_stroke_width: float = 0.3
    font_path: str | None = None
    strict_metrics: bool = False
    leader_gap: float = 1.0     # mm gap between text bbox and leader start

    def __post_init__(self) -> None:
        if self.font_size <= 0:
            raise ValueError(f"font_size must be positive, got {self.font_size}")
        if self.text_anchor not in ("start", "middle", "end"):
            raise ValueError(f"text_anchor must be start/middle/end, got {self.text_anchor!r}")

    def _text_bbox_edge_toward(self, target: complex) -> complex:
        """Compute the point on the text bounding box edge closest to `target`,
        leaving a small gap. Used to start the leader line."""
        w, h = measure_text_mm(self.text, self.font_size, self.font_path, self.strict_metrics)
        # Box bounds relative to anchor and text-anchor mode.
        if self.text_anchor == "middle":
            left, right = self.x - w / 2, self.x + w / 2
        elif self.text_anchor == "start":
            left, right = self.x, self.x + w
        else:
            left, right = self.x - w, self.x
        top, bottom = self.y - h * BASELINE_ASCENT_FRACTION, self.y + h * (1 - BASELINE_ASCENT_FRACTION)
        cx = (left + right) / 2
        cy = (top + bottom) / 2
        # Direction from center to target.
        dx = target.real - cx
        dy = target.imag - cy
        if dx == 0 and dy == 0:
            return target
        # Scale so the vector hits the bbox edge.
        sx = (right - cx) / dx if dx > 0 else (left - cx) / dx if dx < 0 else float("inf")
        sy = (bottom - cy) / dy if dy > 0 else (top - cy) / dy if dy < 0 else float("inf")
        s = min(abs(sx), abs(sy))
        edge = complex(cx + dx * s, cy + dy * s)
        # Add a small gap toward the target.
        ux = dx / (dx * dx + dy * dy) ** 0.5
        uy = dy / (dx * dx + dy * dy) ** 0.5
        return complex(edge.real + ux * self.leader_gap, edge.imag + uy * self.leader_gap)

    def to_drawsvg(self) -> dw.Group:
        g = dw.Group()
        if self.leader_to is not None:
            target = complex(*self.leader_to)
            start = self._text_bbox_edge_toward(target)
            line = dw.Line(start.real, start.imag, target.real, target.imag,
                           stroke=self.leader_stroke, stroke_width=self.leader_stroke_width)
            g.append(line)
        fs_mm = self.font_size * MM_PER_PT
        g.append(dw.Text(
            self.text, x=self.x, y=self.y,
            font_size=fs_mm, font_family=_FONT_FAMILY_SVG,
            text_anchor=self.text_anchor, fill=self.fill,
        ))
        return g


__all__ = ["Bracket", "Annotation"]
