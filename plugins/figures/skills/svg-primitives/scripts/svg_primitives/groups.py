"""Group: virtual container exposing the union-bbox geometry of its members.

A Group is not added to a Layer (it is not rendered). It satisfies the
`Shape` Protocol so `Arrow.connect(group, other_box)` works the same as
connecting two boxes, but the arrow snaps to the rectangle that bounds
all members of the group.

Useful when an arrow should target a cluster of boxes as one visual
unit ("decoding pipeline") rather than picking one box arbitrarily.

Group members must additionally expose `left`, `right`, `top`, `bottom`
properties beyond the bare `Shape` Protocol — `LabeledBox`, `Pill`, and
`Diamond` all do; a custom shape that only implements the four Protocol
methods is not enough.
"""

from __future__ import annotations

from svgpathtools import Line, Path

from .shapes import Shape, Side


class Group:
    """Virtual container whose geometry is the union bbox of its members."""

    def __init__(self, *shapes: Shape) -> None:
        if not shapes:
            raise ValueError("Group requires at least one shape")
        for i, s in enumerate(shapes):
            if not isinstance(s, Shape):
                raise TypeError(
                    f"Group argument {i} is {type(s).__name__!r}, not a Shape. "
                    "Pass shapes as positional args (Group(a, b, c)), not as a "
                    "single sequence (Group([a, b, c]))."
                )
            for prop in ("left", "right", "top", "bottom"):
                if not hasattr(s, prop):
                    raise TypeError(
                        f"Group argument {i} ({type(s).__name__!r}) does not expose "
                        f"a {prop!r} property — required by Group beyond the bare "
                        "Shape Protocol."
                    )
        self._shapes: tuple[Shape, ...] = tuple(shapes)

    @property
    def members(self) -> tuple[Shape, ...]:
        return self._shapes

    @property
    def left(self) -> float:
        return min(s.left for s in self._shapes)  # type: ignore[attr-defined]

    @property
    def right(self) -> float:
        return max(s.right for s in self._shapes)  # type: ignore[attr-defined]

    @property
    def top(self) -> float:
        return min(s.top for s in self._shapes)  # type: ignore[attr-defined]

    @property
    def bottom(self) -> float:
        return max(s.bottom for s in self._shapes)  # type: ignore[attr-defined]

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def cx(self) -> float:
        return (self.left + self.right) / 2

    @property
    def cy(self) -> float:
        return (self.top + self.bottom) / 2

    def anchor_point(self, side: Side) -> complex:
        if side == "N": return complex(self.cx, self.top)
        if side == "S": return complex(self.cx, self.bottom)
        if side == "E": return complex(self.right, self.cy)
        if side == "W": return complex(self.left, self.cy)
        raise ValueError(f"unknown side: {side!r}")

    def outline_path(self) -> Path:
        """Rectangle outline of the union bbox (sharp corners, like LabeledBox)."""
        tl = complex(self.left, self.top)
        tr = complex(self.right, self.top)
        br = complex(self.right, self.bottom)
        bl = complex(self.left, self.bottom)
        return Path(Line(tl, tr), Line(tr, br), Line(br, bl), Line(bl, tl))


__all__ = ["Group"]
