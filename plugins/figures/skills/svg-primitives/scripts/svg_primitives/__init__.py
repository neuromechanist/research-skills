"""Mm-precise SVG primitive layer.

Public API:
    Canvas(width_mm, height_mm, background=...)
        - .layer(name) -> Layer (gets or creates)
        - .add_layer(Layer) -> Canvas
        - .save(path, output_png=False)
    Layer(name)
        - .add(element) -> element

    LabeledBox, Pill, Diamond — auto-sized labeled shapes
    Arrow.connect(src, dst, curve=...) — tangent-correct arrows
        curve='straight' | 'cubic' | 'orthogonal-h' | 'orthogonal-v'
        via=[(x, y), ...] for multi-waypoint paths (straight only)
        corner_radius for rounded interior corners

    Bracket(start, end, depth, label=...) — labeled grouping bracket
    Annotation(x, y, text, leader_to=...) — text + optional leader line
    Group(*shapes) — virtual container exposing the union-bbox geometry

The viewBox is in mm; font_size on shapes is in pt and emitted in mm.
Layers paint in registration order — later layers visually sit on top.
"""

from .annotations import Annotation, Bracket  # noqa: F401
from .arrows import Arrow  # noqa: F401
from .canvas import Canvas, Layer  # noqa: F401
from .groups import Group  # noqa: F401
from .metrics import MetricsFallbackError  # noqa: F401
from .shapes import Diamond, LabeledBox, Pill, Shape, Side  # noqa: F401

__version__ = "0.2.0"
__all__ = [
    "Annotation", "Arrow", "Bracket", "Canvas", "Diamond", "Group",
    "Layer", "LabeledBox", "MetricsFallbackError", "Pill", "Shape", "Side",
]
