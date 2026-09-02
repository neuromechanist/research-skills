"""Coverage for check_svg.py's <image>-as-shape and closed-<path>-as-shape
geometry handling (figure-bible epic): these matter for ai-full-figure
overlay compositions whose substrate is a single <image> and whose labels
sit on hand-drawn <path> boxes rather than <rect>.

Real SVG parsing via svgelements/shapely, no mocks.

Run: uv run --with pytest --with lxml --with svgelements --with shapely --with pillow \\
    pytest plugins/figures/tests/test_check_svg_shapes.py -q
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest

pytest.importorskip("svgelements")
pytest.importorskip("shapely")
pytest.importorskip("lxml")
pytest.importorskip("PIL")

FIGURES_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = FIGURES_ROOT / "agents" / "figure-qa-scripts"
sys.path.insert(0, str(SCRIPTS))

from check_svg import check_svg

# A valid 1x1 red PNG, embedded so svgelements can decode real pixel data and
# resolve a non-zero <image> bounding box (Image.bbox() reports all-zero
# until the raster is loaded).
_PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
_DATA_URI = "data:image/png;base64," + base64.b64encode(_PNG_1X1).decode()


def _overlay_svg() -> str:
    # 120x60 mm canvas: a small <image> substrate in the bottom-right corner
    # (an ai-full-figure background tile), a closed <path> label box in the
    # top-left, and a <text> whose estimated width badly overflows that path
    # box without touching the image.
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="60mm" viewBox="0 0 120 60">
<image href="{_DATA_URI}" x="90" y="40" width="25" height="15"/>
<path id="labelbox" d="M10,10 L50,10 L50,30 L10,30 Z" fill="none" stroke="#000000"/>
<text x="12" y="25" font-size="20">Overflowing long label text</text>
</svg>"""


def test_image_and_closed_path_count_as_shapes(tmp_path):
    svg = tmp_path / "overlay.svg"
    svg.write_text(_overlay_svg())
    geom = check_svg(svg, journal=None, palette=None)["checks"]["geometry"]
    assert geom["available"] and not geom.get("error")
    # The <image> substrate and the closed <path> label box are both shapes.
    assert geom["shape_count"] == 2


def test_text_overflows_closed_path_box(tmp_path):
    svg = tmp_path / "overlay.svg"
    svg.write_text(_overlay_svg())
    geom = check_svg(svg, journal=None, palette=None)["checks"]["geometry"]
    assert len(geom["text_overflow"]) == 1
    overflow = geom["text_overflow"][0]
    assert overflow["container_id"] == "labelbox"


def test_open_path_is_not_treated_as_a_shape(tmp_path):
    # Same box but without the closing 'Z': arrows/text aimed at it must be
    # reported as unresolved, not silently treated as a closed target.
    svg_text = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="60mm" height="40mm" viewBox="0 0 60 40">'
        '<path id="openbox" d="M10,10 L40,10 L40,30" fill="none" stroke="#000000"/>'
        "</svg>"
    )
    svg = tmp_path / "open.svg"
    svg.write_text(svg_text)
    geom = check_svg(svg, journal=None, palette=None)["checks"]["geometry"]
    assert geom["shape_count"] == 0


def test_image_only_svg_has_no_geometry_findings(tmp_path):
    svg_text = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40mm" height="40mm" viewBox="0 0 40 40">'
        f'<image href="{_DATA_URI}" x="0" y="0" width="40" height="40"/>'
        "</svg>"
    )
    svg = tmp_path / "image_only.svg"
    svg.write_text(svg_text)
    geom = check_svg(svg, journal=None, palette=None)["checks"]["geometry"]
    assert geom["shape_count"] == 1
    assert geom["text_overflow"] == []
    assert geom["arrow_tip_issues"] == []
    assert geom["bbox_overlaps"] == []
