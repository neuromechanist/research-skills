"""Mm-precise SVG primitive layer.

Public API:
    Canvas(width_mm, height_mm, background=...)
        - .layer(name) -> Layer (gets or creates)
        - .add_layer(Layer) -> Canvas
        - .save(path, output_png=False)
    Layer(name)
        - .add(element) -> element

    LabeledBox, Pill, Diamond — auto-sized labeled shapes (commit 3)
    Arrow.connect(src, dst, curve=...) — tangent-correct arrows (commit 4)

The viewBox is in mm; font_size on shapes is in pt and emitted in mm.
Layers paint in registration order — later layers visually sit on top.
"""

from .canvas import Canvas, Layer  # noqa: F401

__version__ = "0.1.0"
__all__ = ["Canvas", "Layer"]
