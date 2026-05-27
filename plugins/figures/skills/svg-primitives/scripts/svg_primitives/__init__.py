"""Mm-precise SVG primitive layer.

Public API:
    Canvas(width_mm, height_mm, background=...)
        - .layer(name) -> Layer (gets or creates)
        - .add_layer(Layer) -> Canvas
        - .save(path, output_png=False, validate='warn'|'strict'|'off')
        - .validate() -> list[Finding]
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

    Finding, ValidationError — validation result types
    validate_all(svg_root) — run every check on a parsed SVG

The viewBox is in mm; font_size on shapes is in pt and emitted in mm.
Layers paint in registration order — later layers visually sit on top.
"""

from .annotations import Annotation, Bracket  # noqa: F401
from .arrows import Arrow  # noqa: F401
from .canvas import Canvas, Layer  # noqa: F401
from .groups import Group  # noqa: F401
from .metrics import MetricsFallbackError  # noqa: F401
from .shapes import Diamond, LabeledBox, Pill, Shape, Side  # noqa: F401
from .validation import (  # noqa: F401
    Finding,
    ValidationCategory,
    ValidationError,
    validate_all,
    validate_arrow_tip_distance,
    validate_marker_orient,
    validate_sibling_overlap,
    validate_text_containment,
)

__version__ = "0.3.0"
__all__ = [
    "Annotation", "Arrow", "Bracket", "Canvas", "Diamond", "Finding",
    "Group", "Layer", "LabeledBox", "MetricsFallbackError", "Pill",
    "Shape", "Side", "ValidationCategory", "ValidationError",
    "validate_all", "validate_arrow_tip_distance", "validate_marker_orient",
    "validate_sibling_overlap", "validate_text_containment",
]
