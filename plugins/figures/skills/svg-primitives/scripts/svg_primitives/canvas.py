"""Canvas and Layer: deterministic paint-order SVG composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import drawsvg as dw


def _color_slug(c: str) -> str:
    """Slug a CSS color into an id-safe token (e.g. '#1F3A5F' -> '1f3a5f')."""
    return c.lstrip("#").lower() or "default"


@dataclass
class Layer:
    """An ordered bucket of elements. The Canvas paints layers in registration
    order, so elements in later-registered layers visually sit on top of
    elements in earlier layers."""

    name: str
    elements: list[Any] = field(default_factory=list)

    def add(self, element: Any) -> Any:
        """Append an element. Returns the element so callers can chain."""
        self.elements.append(element)
        return element


@dataclass
class Canvas:
    """An SVG canvas with mm-precise user units and named layers.

    The viewBox is set so 1 user unit == 1 mm; font_size values used by the
    primitive shapes are accepted in pt and emitted in mm so the rendered
    text matches journal-typography conventions regardless of viewer DPI.

    Arrow markers are generated lazily during `to_drawsvg()` — one `<marker>`
    per unique stroke color used by any Arrow in any layer — so a red arrow
    automatically receives a red arrowhead.
    """

    width_mm: float
    height_mm: float
    layers: list[Layer] = field(default_factory=list)
    background: str | None = "#FFFFFF"

    def add_layer(self, layer: Layer) -> "Canvas":
        """Explicit insertion. Returns self for chaining."""
        self.layers.append(layer)
        return self

    def layer(self, name: str) -> Layer:
        """Get a layer by name, creating it if missing."""
        for L in self.layers:
            if L.name == name:
                return L
        L = Layer(name)
        self.layers.append(L)
        return L

    def _collect_arrow_colors(self) -> list[str]:
        seen: list[str] = []
        for L in self.layers:
            for el in L.elements:
                stroke = getattr(el, "stroke", None)
                # Arrow elements expose `stroke` and a `to_drawsvg()` that
                # emits a path with `marker-end`. Anything else is opaque.
                if stroke and getattr(el, "_is_arrow", False) and stroke not in seen:
                    seen.append(stroke)
        return seen

    def to_drawsvg(self) -> dw.Drawing:
        d = dw.Drawing(self.width_mm, self.height_mm, origin=(0, 0))
        d.view_box = (0, 0, self.width_mm, self.height_mm)
        d.width = f"{self.width_mm}mm"
        d.height = f"{self.height_mm}mm"

        marker_ids: dict[str, str] = {}
        for color in self._collect_arrow_colors():
            mid = f"arrow-{_color_slug(color)}"
            marker_ids[color] = mid
            # Triangle tip at (0,0); refX/refY=0 places the tip exactly on the
            # path endpoint. orient="auto" lets the SVG renderer compute the
            # tangent at the endpoint and rotate the marker — this is the
            # mechanism that keeps the arrowhead aligned with curved paths.
            marker = dw.Marker(-2, -1, 0, 1, scale=1, orient="auto", id=mid)
            marker.args["markerUnits"] = "userSpaceOnUse"
            marker.args["markerWidth"] = 2.4
            marker.args["markerHeight"] = 2.4
            marker.args["refX"] = 0.0
            marker.args["refY"] = 0.0
            marker.append(dw.Lines(-2, -1, 0, 0, -2, 1, close=True, fill=color))
            d.append_def(marker)

        if self.background:
            d.append(dw.Rectangle(0, 0, self.width_mm, self.height_mm, fill=self.background))

        for L in self.layers:
            g = dw.Group(id=f"layer-{L.name}")
            for el in L.elements:
                if hasattr(el, "to_drawsvg"):
                    if getattr(el, "_is_arrow", False):
                        el._marker_url = f"url(#{marker_ids[el.stroke]})"
                    g.append(el.to_drawsvg())
                else:
                    g.append(el)
            d.append(g)
        return d

    def save(self, path: str | Path, output_png: bool = False, png_width: int = 1800) -> None:
        """Write the SVG to `path`. If `output_png` is True, also write a PNG
        next to it via cairosvg. PNG width in px is `png_width`; height is
        derived to preserve aspect."""
        d = self.to_drawsvg()
        svg_path = Path(path)
        d.save_svg(str(svg_path))
        if output_png:
            try:
                import cairosvg
            except ImportError as e:
                raise RuntimeError(
                    "output_png=True requires cairosvg. Install with: "
                    "uv add cairosvg, or include `--with cairosvg` on the uv run line."
                ) from e
            png_path = svg_path.with_suffix(".png")
            cairosvg.svg2png(url=str(svg_path), output_width=png_width, write_to=str(png_path))
