"""Overlay labels, arrows, and scale bars on top of an AI-generated substrate.

The output is an SVG that embeds the raster substrate via base64-encoded
`<image>` data and adds `<text>`, `<line>`, and arrow-marker geometry on
top. The SVG's viewBox matches the substrate's pixel dimensions, so all
overlay coordinates are pixel-addressed. The `width`/`height` attributes
use a `mm` value derived from --width-mm so the SVG can be composed by
scientific-figure without rescaling math.

Usage:
    uv run --with pillow python overlay_labels.py substrate.png \\
        --label "lateral sulcus@600,420" \\
        --label "central sulcus@800,300" \\
        --scale-bar "1 cm@200,950" \\
        --width-mm 100 \\
        -o out/labeled.svg

Batch labels via JSON file:
    overlay_labels.py substrate.png --labels-file labels.json -o out/labeled.svg

Labels JSON schema:
    {
      "width_mm": 100,
      "labels": [
        {"text": "...", "x": 600, "y": 420, "color": "#1F3A5F", "font_size_pt": 8,
         "arrow_to": [650, 460]}
      ],
      "scale_bars": [{"text": "1 cm", "x": 200, "y": 950, "length_px": 80}]
    }

Exit codes: 0 success, 2 on input error.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_FONT_SIZE_PT = 8
DEFAULT_COLOR = "#1F3A5F"

# CSS hex colors only (3/4/6/8 digits). Reject anything else so untrusted JSON
# input cannot inject extra SVG attributes via the color field.
_HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def _read_image_size(path: Path) -> tuple[int, int]:
    from PIL import Image  # type: ignore[import-not-found]

    with Image.open(str(path)) as img:
        return img.size


def _parse_label_shorthand(s: str) -> dict[str, Any]:
    """Accept 'text@x,y' and return a label dict."""
    m = re.match(r"^(.*?)@(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$", s.strip())
    if not m:
        raise ValueError(
            f"label must be in 'text@x,y' form, got '{s}'"
        )
    return {"text": m.group(1).strip(), "x": float(m.group(2)), "y": float(m.group(3))}


def _parse_scale_bar_shorthand(s: str, default_length_px: int = 80) -> dict[str, Any]:
    """Accept 'caption@x,y' and return a scale-bar dict with a default length."""
    m = re.match(r"^(.*?)@(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$", s.strip())
    if not m:
        raise ValueError(
            f"scale-bar must be in 'caption@x,y' form, got '{s}'"
        )
    return {
        "text": m.group(1).strip(),
        "x": float(m.group(2)),
        "y": float(m.group(3)),
        "length_px": default_length_px,
    }


def _embed_image_data_uri(path: Path) -> str:
    """Read a PNG and return a data: URI for SVG <image href=...>."""
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _safe_color(value: str | None, default: str = DEFAULT_COLOR) -> str:
    """Return value if it is a CSS hex color, else default. Raises ValueError when
    a value is provided but is not a valid hex (so user-supplied JSON labels with
    unsafe color values fail loudly instead of injecting SVG attributes)."""
    if value is None:
        return default
    if not _HEX_COLOR_RE.match(value):
        raise ValueError(f"unsafe color value (must be hex): {value!r}")
    return value


def _safe_marker_id(color: str) -> str:
    """Stable, attribute-safe id derived from a validated hex color."""
    return "overlay-arrow-" + color.lstrip("#").lower()


def _label_svg(label: dict[str, Any], font_size: float = DEFAULT_FONT_SIZE_PT) -> str:
    """Emit a <text> element (and optional leader arrow) for one label.
    The marker referenced is color-specific so arrowhead and stroke match."""
    text = label["text"]
    x = float(label["x"])
    y = float(label["y"])
    color = _safe_color(label.get("color"))
    size = float(label.get("font_size_pt", font_size))
    arrow_to = label.get("arrow_to")
    marker_id = _safe_marker_id(color)

    out: list[str] = []
    if arrow_to:
        ax, ay = float(arrow_to[0]), float(arrow_to[1])
        out.append(
            f'<line x1="{x}" y1="{y}" x2="{ax}" y2="{ay}" '
            f'stroke="{color}" stroke-width="1.2" marker-end="url(#{marker_id})"/>'
        )
    out.append(
        f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="{size}" '
        f'fill="{color}" stroke="white" stroke-width="2" paint-order="stroke">'
        f"{_xml_escape(text)}</text>"
    )
    return "\n  ".join(out)


def _scale_bar_svg(bar: dict[str, Any]) -> str:
    x = float(bar["x"])
    y = float(bar["y"])
    length_px = float(bar.get("length_px", 80))
    color = _safe_color(bar.get("color"))
    text = bar.get("text", "")
    size = float(bar.get("font_size_pt", DEFAULT_FONT_SIZE_PT))
    return (
        f'<g class="scale-bar">\n'
        f'    <line x1="{x}" y1="{y}" x2="{x + length_px}" y2="{y}" '
        f'stroke="{color}" stroke-width="3"/>\n'
        f'    <text x="{x + length_px / 2}" y="{y - 8}" text-anchor="middle" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="{size}" '
        f'fill="{color}" stroke="white" stroke-width="2" paint-order="stroke">'
        f"{_xml_escape(text)}</text>\n  </g>"
    )


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def compose_svg(
    substrate_path: Path,
    width_mm: float,
    labels: list[dict[str, Any]],
    scale_bars: list[dict[str, Any]],
) -> str:
    pw, ph = _read_image_size(substrate_path)
    height_mm = width_mm * (ph / pw)
    image_uri = _embed_image_data_uri(substrate_path)

    # Collect every distinct, validated color used by labels and scale bars,
    # plus DEFAULT_COLOR as a baseline. Emit one <marker> per color so the
    # arrowhead matches its line's stroke rather than always being the default.
    colors: set[str] = {DEFAULT_COLOR}
    for lbl in labels:
        colors.add(_safe_color(lbl.get("color")))
    for bar in scale_bars:
        colors.add(_safe_color(bar.get("color")))

    marker_defs = "\n    ".join(
        f'<marker id="{_safe_marker_id(c)}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>'
        for c in sorted(colors)
    )

    label_blocks = "\n  ".join(_label_svg(label) for label in labels)
    bar_blocks = "\n  ".join(_scale_bar_svg(bar) for bar in scale_bars)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width_mm}mm" height="{height_mm:.3f}mm"
     viewBox="0 0 {pw} {ph}">
  <defs>
    {marker_defs}
  </defs>
  <image href="{image_uri}" x="0" y="0" width="{pw}" height="{ph}"/>
  {label_blocks}
  {bar_blocks}
</svg>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Overlay labels, arrows, and scale bars on an AI substrate; emit composable SVG.",
    )
    parser.add_argument("substrate", type=Path, help="Input PNG substrate")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output SVG path")
    parser.add_argument(
        "--width-mm", type=float, default=89.0,
        help="Final SVG width in mm (default: 89, Nature 1-column). Height is derived from substrate aspect.",
    )
    parser.add_argument(
        "--label", action="append", default=[],
        help="Label shorthand 'text@x,y' (repeatable). Coordinates are substrate pixels.",
    )
    parser.add_argument(
        "--scale-bar", action="append", default=[],
        help="Scale-bar shorthand 'caption@x,y' (repeatable).",
    )
    parser.add_argument(
        "--labels-file", type=Path,
        help="JSON file with {width_mm, labels[], scale_bars[]} for batch overlay.",
    )
    args = parser.parse_args(argv)

    if not args.substrate.exists():
        print(f"error: substrate not found: {args.substrate}", file=sys.stderr)
        return 2

    labels: list[dict[str, Any]] = []
    scale_bars: list[dict[str, Any]] = []
    width_mm = args.width_mm

    if args.labels_file:
        try:
            doc = json.loads(args.labels_file.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not load labels file '{args.labels_file}': {exc}", file=sys.stderr)
            return 2
        labels = doc.get("labels", [])
        scale_bars = doc.get("scale_bars", [])
        width_mm = float(doc.get("width_mm", width_mm))

    try:
        labels.extend(_parse_label_shorthand(s) for s in args.label)
        scale_bars.extend(_parse_scale_bar_shorthand(s) for s in args.scale_bar)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        svg = compose_svg(args.substrate, width_mm, labels, scale_bars)
    except Exception as exc:
        print(f"error ({type(exc).__name__}): could not compose SVG: {exc}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg)
    print(
        f"wrote {args.output} ({len(svg)} bytes, {len(labels)} label(s), "
        f"{len(scale_bars)} scale-bar(s))",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
