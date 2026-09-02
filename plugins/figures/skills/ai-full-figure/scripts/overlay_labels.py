"""Overlay labels, arrows, and scale bars on top of an AI-generated substrate.

The output is an SVG that embeds the raster substrate via base64-encoded
`<image>` data and adds `<text>`, `<line>`, and arrow-marker geometry on
top. The SVG's viewBox matches the substrate's pixel dimensions, so all
overlay coordinates are pixel-addressed. The `width`/`height` attributes
use a `mm` value derived from --width-mm so the SVG can be composed by
scientific-figure without rescaling math.

Unit handling: the SVG root declares a physical width in mm over a pixel
viewBox, so a bare (unit-less) `font-size` or `stroke-width` is read as one
user unit per viewBox pixel, not as a point. `validate_fonts.py`'s
`_root_unit_to_pt` computes the actual points-per-user-unit for that root as
`(width_mm * 72 / 25.4) / viewbox_width`. This module inverts that formula
into `units_per_pt = viewbox_width / (width_mm * 72 / 25.4)` once per
document and multiplies every pt-denominated value (label font sizes, the
arrow stroke width, the scale-bar stroke width, and the text legibility
halo) by it before writing the bare SVG number, so a documented "8 pt"
label actually measures 8 pt when validated.

Usage:
    uv run --with pillow python overlay_labels.py substrate.png \\
        --label "lateral sulcus@600,420" \\
        --label "central sulcus@800,300" \\
        --scale-bar "1 cm@200,950" \\
        --width-mm 100 \\
        -o out/labeled.svg

Batch labels via JSON file:
    overlay_labels.py substrate.png --labels-file labels.json -o out/labeled.svg

Validate the emitted font sizes against a journal minimum right after
writing (imports validate_fonts.py in-process; exits 1 if any label falls
below the minimum):
    overlay_labels.py substrate.png --labels-file labels.json \\
        -o out/labeled.svg --check --journal nature

Write a sibling `<output-stem>.grid.png` with a labelled 100 px grid over
the substrate, so an agent can read label coordinates from the image
itself instead of hovering a cursor in an image viewer:
    overlay_labels.py substrate.png -o out/labeled.svg --grid

Labels JSON schema:
    {
      "width_mm": 100,
      "labels": [
        {"text": "...", "x": 600, "y": 420, "color": "#1F3A5F", "font_size_pt": 8,
         "arrow_to": [650, 460], "stroke_under": "#000000"}
      ],
      "scale_bars": [{"text": "1 cm", "x": 200, "y": 950, "length_px": 80}]
    }

`stroke_under` overrides the default white legibility halo painted behind a
label's or scale-bar's text (useful on a light substrate where white does
not read).

Exit codes: 0 success, 1 if --check found a label below the journal
minimum, 2 on input error.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

DEFAULT_FONT_SIZE_PT = 8.0
DEFAULT_COLOR = "#1F3A5F"
DEFAULT_STROKE_UNDER = "#FFFFFF"

# Documented in pt, like font_size_pt; scaled by units_per_pt() before being
# written as a bare SVG number (see the module docstring's unit-handling note).
ARROW_LINE_STROKE_PT = 1.2
TEXT_HALO_STROKE_PT = 2.0
SCALE_BAR_LINE_STROKE_PT = 3.0

# Kept in sync with validate_fonts.JOURNAL_MIN_PT's keys.
JOURNAL_CHOICES = ("nature", "science", "cell", "pnas", "generic")
DEFAULT_JOURNAL = "nature"

GRID_SPACING_PX = 100

# CSS hex colors only (3/4/6/8 digits). Reject anything else so untrusted JSON
# input cannot inject extra SVG attributes via the color field.
_HEX_COLOR_RE = re.compile(
    r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$"
)


def _read_image_size(path: Path) -> tuple[int, int]:
    from PIL import Image  # type: ignore[import-not-found]

    with Image.open(str(path)) as img:
        return img.size


def units_per_pt(width_mm: float, viewbox_width: float) -> float:
    """User (viewBox) units per point for an SVG whose root declares a
    physical `width_mm` over a pixel `viewbox_width`.

    This is the reciprocal of `validate_fonts._root_unit_to_pt`, which reads
    points per user unit as `(width_mm * 72 / 25.4) / viewbox_width`. So
    `pt_value * units_per_pt(...)` is the bare SVG number that
    `validate_fonts.py` will read back as `pt_value` points.
    """
    if width_mm <= 0:
        raise ValueError(f"width_mm must be positive, got {width_mm}")
    if viewbox_width <= 0:
        raise ValueError(f"viewbox_width must be positive, got {viewbox_width}")
    pt_per_document_width = width_mm * 72.0 / 25.4
    return viewbox_width / pt_per_document_width


def _parse_label_shorthand(s: str) -> dict[str, Any]:
    """Accept 'text@x,y' and return a label dict."""
    m = re.match(r"^(.*?)@(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$", s.strip())
    if not m:
        raise ValueError(f"label must be in 'text@x,y' form, got '{s}'")
    return {"text": m.group(1).strip(), "x": float(m.group(2)), "y": float(m.group(3))}


def _parse_scale_bar_shorthand(s: str, default_length_px: int = 80) -> dict[str, Any]:
    """Accept 'caption@x,y' and return a scale-bar dict with a default length."""
    m = re.match(r"^(.*?)@(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$", s.strip())
    if not m:
        raise ValueError(f"scale-bar must be in 'caption@x,y' form, got '{s}'")
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


def _label_svg(
    label: dict[str, Any], upt: float, font_size_pt: float = DEFAULT_FONT_SIZE_PT
) -> str:
    """Emit a <text> element (and optional leader arrow) for one label.
    The marker referenced is color-specific so arrowhead and stroke match.
    `upt` is units_per_pt for the document; every pt-denominated value here
    (font size, arrow stroke, halo stroke) is multiplied by it before being
    written as a bare SVG number."""
    text = label["text"]
    x = float(label["x"])
    y = float(label["y"])
    color = _safe_color(label.get("color"))
    halo = _safe_color(label.get("stroke_under"), DEFAULT_STROKE_UNDER)
    size_pt = float(label.get("font_size_pt", font_size_pt))
    size = size_pt * upt
    halo_width = TEXT_HALO_STROKE_PT * upt
    arrow_to = label.get("arrow_to")
    marker_id = _safe_marker_id(color)

    out: list[str] = []
    if arrow_to:
        ax, ay = float(arrow_to[0]), float(arrow_to[1])
        arrow_width = ARROW_LINE_STROKE_PT * upt
        out.append(
            f'<line x1="{x}" y1="{y}" x2="{ax}" y2="{ay}" '
            f'stroke="{color}" stroke-width="{arrow_width:.4f}" marker-end="url(#{marker_id})"/>'
        )
    out.append(
        f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="{size:.4f}" '
        f'fill="{color}" stroke="{halo}" stroke-width="{halo_width:.4f}" paint-order="stroke">'
        f"{_xml_escape(text)}</text>"
    )
    return "\n  ".join(out)


def _scale_bar_svg(bar: dict[str, Any], upt: float) -> str:
    x = float(bar["x"])
    y = float(bar["y"])
    length_px = float(bar.get("length_px", 80))
    color = _safe_color(bar.get("color"))
    halo = _safe_color(bar.get("stroke_under"), DEFAULT_STROKE_UNDER)
    text = bar.get("text", "")
    size_pt = float(bar.get("font_size_pt", DEFAULT_FONT_SIZE_PT))
    size = size_pt * upt
    bar_width = SCALE_BAR_LINE_STROKE_PT * upt
    halo_width = TEXT_HALO_STROKE_PT * upt
    return (
        f'<g class="scale-bar">\n'
        f'    <line x1="{x}" y1="{y}" x2="{x + length_px}" y2="{y}" '
        f'stroke="{color}" stroke-width="{bar_width:.4f}"/>\n'
        f'    <text x="{x + length_px / 2}" y="{y - 8}" text-anchor="middle" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="{size:.4f}" '
        f'fill="{color}" stroke="{halo}" stroke-width="{halo_width:.4f}" paint-order="stroke">'
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
    upt = units_per_pt(width_mm, pw)

    # Collect every distinct, validated color used by labels and scale bars,
    # plus DEFAULT_COLOR as a baseline. Emit one <marker> per color so the
    # arrowhead matches its line's stroke rather than always being the default.
    # Marker geometry (viewBox/markerWidth/markerHeight) does not need pt
    # scaling: SVG markers default to markerUnits="strokeWidth", so the
    # arrowhead already scales with the (now correctly pt-scaled) line width.
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

    label_blocks = "\n  ".join(_label_svg(label, upt) for label in labels)
    bar_blocks = "\n  ".join(_scale_bar_svg(bar, upt) for bar in scale_bars)

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


def _write_grid_png(
    substrate_path: Path, grid_path: Path, spacing: int = GRID_SPACING_PX
) -> Path:
    """Write a sibling PNG with a labelled pixel grid over the substrate, so an
    agent can read label coordinates directly from the image instead of
    hovering a cursor in an image viewer."""
    from PIL import Image, ImageDraw, ImageFont  # type: ignore[import-not-found]

    with Image.open(str(substrate_path)) as src:
        img = src.convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font = ImageFont.load_default()
    grid_color = (255, 0, 0)
    for x in range(0, w, spacing):
        draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)
    for x in range(0, w, spacing):
        for y in range(0, h, spacing):
            draw.text((x + 2, y + 2), f"{x},{y}", fill=grid_color, font=font)
    grid_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(grid_path)
    return grid_path


def _load_validate_fonts() -> ModuleType:
    """Import validate_fonts.py by file path (it lives in a sibling skill, not
    an installed package) so --check can reuse its exact pt-conversion maths
    instead of re-implementing it."""
    module_path = (
        Path(__file__).resolve().parent.parent.parent
        / "scientific-figure"
        / "scripts"
        / "validate_fonts.py"
    )
    if not module_path.exists():
        raise FileNotFoundError(f"validate_fonts.py not found at {module_path}")
    spec = importlib.util.spec_from_file_location(
        "overlay_labels_validate_fonts", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build an import spec for {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Overlay labels, arrows, and scale bars on an AI substrate; emit composable SVG.",
    )
    parser.add_argument("substrate", type=Path, help="Input PNG substrate")
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Output SVG path"
    )
    parser.add_argument(
        "--width-mm",
        type=float,
        default=89.0,
        help="Final SVG width in mm (default: 89, Nature 1-column). Height is derived from substrate aspect.",
    )
    parser.add_argument(
        "--label",
        action="append",
        default=[],
        help="Label shorthand 'text@x,y' (repeatable). Coordinates are substrate pixels.",
    )
    parser.add_argument(
        "--scale-bar",
        action="append",
        default=[],
        help="Scale-bar shorthand 'caption@x,y' (repeatable).",
    )
    parser.add_argument(
        "--labels-file",
        type=Path,
        help="JSON file with {width_mm, labels[], scale_bars[]} for batch overlay.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="After writing, validate the emitted font sizes against --journal's minimum "
        "(imports validate_fonts.py in-process); exit 1 if any label is below it.",
    )
    parser.add_argument(
        "--journal",
        default=DEFAULT_JOURNAL,
        choices=JOURNAL_CHOICES,
        help=f"Journal font-size minimum used by --check (default: {DEFAULT_JOURNAL}).",
    )
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Also write a sibling '<output-stem>.grid.png' with a "
        f"{GRID_SPACING_PX} px labelled grid over the substrate, so label "
        "coordinates can be read from the image.",
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
            print(
                f"error: could not load labels file '{args.labels_file}': {exc}",
                file=sys.stderr,
            )
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
    except (OSError, ValueError) as exc:
        print(
            f"error ({type(exc).__name__}): could not compose SVG: {exc}",
            file=sys.stderr,
        )
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg)
    print(
        f"wrote {args.output} ({len(svg)} bytes, {len(labels)} label(s), "
        f"{len(scale_bars)} scale-bar(s))",
        file=sys.stderr,
    )

    exit_code = 0

    if args.grid:
        grid_path = args.output.parent / f"{args.output.stem}.grid.png"
        try:
            _write_grid_png(args.substrate, grid_path)
        except OSError as exc:
            print(f"error: could not write grid PNG: {exc}", file=sys.stderr)
            return 2
        print(f"wrote {grid_path}", file=sys.stderr)

    if args.check:
        try:
            vf = _load_validate_fonts()
        except (FileNotFoundError, ImportError) as exc:
            print(
                f"error: --check requested but validate_fonts.py could not be loaded: {exc}",
                file=sys.stderr,
            )
            return 2
        try:
            report = vf.validate(args.output, args.journal)
        except vf.etree.XMLSyntaxError as exc:
            print(
                f"error: --check could not parse '{args.output}': {exc}",
                file=sys.stderr,
            )
            return 2
        except OSError as exc:
            print(
                f"error: --check could not open '{args.output}': {exc}", file=sys.stderr
            )
            return 2

        if report["issue_count"]:
            print(
                f"--check: {report['issue_count']} of {report['checked_count']} label(s) "
                f"below {report['minimum_pt']} pt for journal '{args.journal}'.",
                file=sys.stderr,
            )
            for issue in report["issues"]:
                print(
                    f"  - {issue['text']!r}: {issue['effective_pt']} pt",
                    file=sys.stderr,
                )
            exit_code = 1
        else:
            print(
                f"--check: all {report['checked_count']} label(s) meet the "
                f"{report['minimum_pt']} pt minimum for journal '{args.journal}'.",
                file=sys.stderr,
            )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
