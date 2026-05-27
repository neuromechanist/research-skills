"""Auto-sized labeled shapes: LabeledBox, Pill, Diamond.

Shapes measure their text via `metrics.measure_lines_mm` and grow their
container to fit text + padding on every side. `min_width` / `min_height`
clamp the lower bound for cases where the user wants chunky uniform boxes
regardless of label length.

Anchor points (N, S, E, W) are exposed so `Arrow.connect` can snap to a
specific side; if the caller does not specify a side, `Arrow.connect`
picks the side facing the other endpoint.

The shape outline is exposed as an `svgpathtools.Path` so the arrow
geometry layer can intersect the connection path with the outline and
trim the endpoint to the visual edge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import drawsvg as dw
from svgpathtools import Line, Path

from .metrics import MM_PER_PT, measure_lines_mm, measure_text_mm

_FONT_FAMILY_SVG = "Helvetica, Arial, sans-serif"

Side = Literal["N", "S", "E", "W"]
Anchor = Literal["top-left", "center"]


@dataclass
class LabeledBox:
    """Rounded-rectangle box that auto-sizes to fit its label.

    The label is text-anchor='middle' and dominant-baseline-equivalent
    centered inside the box. Multi-line labels (newline-separated) stack
    with `line_spacing` em between baselines. font_size is in pt; the
    rendered SVG font-size attribute is emitted in mm.
    """

    x: float
    y: float
    text: str
    font_size: float = 7.0  # pt
    padding: float = 2.0    # mm on every side
    min_width: float = 0.0
    min_height: float = 0.0
    fill: str = "#F4F1DE"
    stroke: str = "#1F3A5F"
    stroke_width: float = 0.6
    rx: float = 1.5         # corner radius (mm)
    anchor: Anchor = "top-left"
    line_spacing: float = 1.2
    font_path: str | None = None  # optional override for the font search

    width: float = field(init=False)
    height: float = field(init=False)
    _lines: list[str] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._lines = self.text.split("\n") if self.text else [""]
        text_w, text_h = measure_lines_mm(
            self._lines, self.font_size, self.line_spacing, self.font_path,
        )
        self.width = max(text_w + 2 * self.padding, self.min_width)
        self.height = max(text_h + 2 * self.padding, self.min_height)
        if self.anchor == "center":
            self.x -= self.width / 2
            self.y -= self.height / 2
            self.anchor = "top-left"

    # Geometry helpers.
    @property
    def left(self) -> float: return self.x
    @property
    def right(self) -> float: return self.x + self.width
    @property
    def top(self) -> float: return self.y
    @property
    def bottom(self) -> float: return self.y + self.height
    @property
    def cx(self) -> float: return self.x + self.width / 2
    @property
    def cy(self) -> float: return self.y + self.height / 2

    def outline_path(self) -> Path:
        """svgpathtools Path tracing the rectangle outline.

        The corners are sharp (we ignore the rendered rx for intersection
        purposes — arrows snap to the bounding rectangle, which is within
        1 mm of the rounded corner and acceptable for visual edge snap)."""
        tl = complex(self.left, self.top)
        tr = complex(self.right, self.top)
        br = complex(self.right, self.bottom)
        bl = complex(self.left, self.bottom)
        return Path(Line(tl, tr), Line(tr, br), Line(br, bl), Line(bl, tl))

    def anchor_point(self, side: Side) -> complex:
        if side == "N": return complex(self.cx, self.top)
        if side == "S": return complex(self.cx, self.bottom)
        if side == "E": return complex(self.right, self.cy)
        if side == "W": return complex(self.left, self.cy)
        raise ValueError(f"unknown side: {side!r}")

    # Construction helper.
    @classmethod
    def next_to(
        cls, other: "LabeledBox", side: Side, gap: float, **kwargs
    ) -> "LabeledBox":
        """Build a new box positioned relative to `other` on the given side
        with `gap` mm between the touching edges."""
        # Build a probe to compute width/height, then place.
        probe = cls(x=0, y=0, **kwargs)
        if side == "E":
            probe.x = other.right + gap
            probe.y = other.top
        elif side == "W":
            probe.x = other.left - gap - probe.width
            probe.y = other.top
        elif side == "N":
            probe.x = other.left
            probe.y = other.top - gap - probe.height
        elif side == "S":
            probe.x = other.left
            probe.y = other.bottom + gap
        else:
            raise ValueError(side)
        return probe

    # Rendering.
    def to_drawsvg(self) -> dw.Group:
        g = dw.Group()
        g.append(dw.Rectangle(
            self.x, self.y, self.width, self.height,
            rx=self.rx, ry=self.rx,
            fill=self.fill, stroke=self.stroke, stroke_width=self.stroke_width,
        ))
        self._render_text(g)
        return g

    def _render_text(self, g: dw.Group) -> None:
        fs_mm = self.font_size * MM_PER_PT
        n = len(self._lines)
        _, single_h = measure_text_mm(self._lines[0], self.font_size, self.font_path)
        line_h = single_h * self.line_spacing
        block_h = single_h + line_h * (n - 1)
        # ascent-ish baseline offset.
        first_baseline = self.cy - block_h / 2 + single_h * 0.78
        for i, ln in enumerate(self._lines):
            g.append(dw.Text(
                ln, x=self.cx, y=first_baseline + i * line_h,
                font_size=fs_mm, font_family=_FONT_FAMILY_SVG,
                text_anchor="middle",
                fill=self.stroke,
            ))


@dataclass
class Pill(LabeledBox):
    """LabeledBox whose corner radius equals half the height — a flat-sided
    capsule. Useful for terminal nodes (start/end) in flowcharts."""

    def __post_init__(self) -> None:
        super().__post_init__()
        # Override rx to a half-height pill after sizing is known.
        self.rx = self.height / 2


@dataclass
class Diamond(LabeledBox):
    """Diamond (rhombus) shape — typical "decision" node in flowcharts.

    Sizing rule: the inscribed rectangle that fits the text must be no
    larger than half the diamond's bounding rectangle (in each axis).
    Equivalently, the diamond's width is 2 * (text_w + 2*padding) and
    height is 2 * (text_h + 2*padding). Text remains center-anchored
    inside the diamond's bounding box.
    """

    def __post_init__(self) -> None:
        # Initial measurement (computes self.width/height for text bbox + padding)
        super().__post_init__()
        # Scale up so inscribed rect (half size) still fits text + padding.
        self.width *= 2
        self.height *= 2

    def outline_path(self) -> Path:
        """Diamond outline: four edges from N -> E -> S -> W -> N."""
        n = complex(self.cx, self.top)
        e = complex(self.right, self.cy)
        s = complex(self.cx, self.bottom)
        w = complex(self.left, self.cy)
        return Path(Line(n, e), Line(e, s), Line(s, w), Line(w, n))

    def anchor_point(self, side: Side) -> complex:
        if side == "N": return complex(self.cx, self.top)
        if side == "S": return complex(self.cx, self.bottom)
        if side == "E": return complex(self.right, self.cy)
        if side == "W": return complex(self.left, self.cy)
        raise ValueError(side)

    def to_drawsvg(self) -> dw.Group:
        g = dw.Group()
        # Diamond as a polygon: N, E, S, W.
        pts = [
            self.cx, self.top,
            self.right, self.cy,
            self.cx, self.bottom,
            self.left, self.cy,
        ]
        g.append(dw.Lines(
            *pts, close=True,
            fill=self.fill, stroke=self.stroke, stroke_width=self.stroke_width,
        ))
        self._render_text(g)
        return g


__all__ = ["LabeledBox", "Pill", "Diamond", "Side"]
