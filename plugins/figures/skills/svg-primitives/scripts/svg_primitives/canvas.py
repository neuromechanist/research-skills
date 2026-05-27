"""Canvas and Layer: deterministic paint-order SVG composition."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import drawsvg as dw

ValidateMode = Literal["off", "warn", "strict"]

log = logging.getLogger(__name__)


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

    def __post_init__(self) -> None:
        if self.width_mm <= 0 or self.height_mm <= 0:
            raise ValueError(
                f"Canvas dimensions must be positive: "
                f"width_mm={self.width_mm}, height_mm={self.height_mm}"
            )

    def add_layer(self, layer: Layer) -> "Canvas":
        """Explicit insertion. Returns self for chaining."""
        for existing in self.layers:
            if existing.name == layer.name:
                raise ValueError(
                    f"Canvas already has a layer named {layer.name!r}; "
                    "use Canvas.layer(name) to get or create a layer by name."
                )
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

        # Detect Group accidentally added to a layer. Group is a virtual
        # routing container — its members should be added individually.
        # We import here to avoid a circular import at module load.
        from .groups import Group as _Group

        for L in self.layers:
            g = dw.Group(id=f"layer-{L.name}")
            for el in L.elements:
                if isinstance(el, _Group):
                    raise TypeError(
                        f"Layer {L.name!r} contains a Group object. Group is a "
                        "virtual container for Arrow.connect; add the member "
                        "shapes (Group.members) to the layer individually."
                    )
                if hasattr(el, "to_drawsvg"):
                    if getattr(el, "_is_arrow", False):
                        marker_url = marker_ids.get(el.stroke)
                        if marker_url is None:
                            raise RuntimeError(
                                f"Arrow with stroke={el.stroke!r} was added but its "
                                "color was not collected — this indicates a sentinel "
                                "or color was modified after Canvas built its marker set."
                            )
                        el._marker_url = f"url(#{marker_url})"
                    g.append(el.to_drawsvg())
                else:
                    g.append(el)
            d.append(g)
        return d

    def save(
        self,
        path: str | Path,
        output_png: bool = False,
        png_width: int = 1800,
        validate: ValidateMode = "warn",
    ) -> list:
        """Write the SVG to `path` and optionally validate the rendered output.

        Returns the list of `Finding`s produced by validation (empty when
        validate='off' or the SVG is clean).

        validate:
          * 'off'    — skip validation; return [].
          * 'warn'   — run validation; log findings at WARNING; return them.
          * 'strict' — run validation; raise ValidationError if any findings.

        If `output_png` is True, also write a sibling PNG via cairosvg.
        """
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
            try:
                cairosvg.svg2png(url=str(svg_path), output_width=png_width, write_to=str(png_path))
            except Exception as e:
                raise RuntimeError(
                    f"cairosvg failed to render {svg_path} to PNG: {e}. "
                    "The SVG was written successfully; only the PNG export failed."
                ) from e
        return self._run_validation(d, validate, source=str(svg_path))

    def validate(self, *, emit_warnings: bool = False) -> list:
        """Render the canvas to an in-memory SVG, parse, run all validators,
        return the finding list. Does not write to disk. Does not raise.

        Pair with `if findings: raise ...` for strict-mode-equivalent in
        non-save contexts. Pass `emit_warnings=True` to ALSO log findings
        at WARNING (useful for long-running pipelines that want audit logs
        without disk writes)."""
        d = self.to_drawsvg()
        return self._run_validation(d, "warn", source="<in-memory>", emit_warnings=emit_warnings)

    def _run_validation(self, drawing, mode: ValidateMode, *, source: str, emit_warnings: bool = True) -> list:
        """Shared validation entry point used by save() and validate()."""
        if mode == "off":
            return []
        from .validation import parse_svg, validate_all, ValidationError

        svg_text = drawing.as_svg()
        try:
            root = parse_svg(svg_text)
        except Exception as exc:
            # If the rendered SVG isn't valid XML, surface a clear error
            # that names svg-primitives and the most likely cause rather
            # than letting a raw lxml exception escape.
            raise RuntimeError(
                f"svg-primitives: the rendered SVG from {source!r} is not valid XML. "
                "This usually means a label or attribute contains an unescaped special "
                f"character such as '&', '<', or '>'. Original error: {exc}"
            ) from exc
        findings = validate_all(root)
        if findings and emit_warnings and mode == "warn":
            log.warning(
                "svg-primitives validation: %d finding(s) in %s",
                len(findings), source,
            )
            for f in findings:
                log.warning("  %s", f)
        if findings and mode == "strict":
            raise ValidationError(findings)
        return findings
