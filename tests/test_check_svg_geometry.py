"""CI coverage for check_svg.py's geometry section (issue #47).

Drives the same synthetic cases as the standalone fixture
(plugins/figures/agents/figure-qa-scripts/examples/check_svg_failure_cases.py) through
pytest, plus a regression that the shipped clean schematic produces zero geometry
findings. Real SVG parsing, no mocks. Needs svgelements / svgpathtools / shapely.

Run: uv run --with pytest --with lxml --with svgelements --with shapely pytest tests/ -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "figures" / "agents" / "figure-qa-scripts"
EXAMPLES = SCRIPTS / "examples"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(EXAMPLES))

pytest.importorskip("svgelements")
pytest.importorskip("shapely")
pytest.importorskip("lxml")

import check_svg_failure_cases as fc  # noqa: E402  (after sys.path setup + importorskip)
from check_svg import check_svg, _viewbox_mm_per_unit, main  # noqa: E402
from lxml import etree  # noqa: E402


@pytest.mark.parametrize("case", fc.CASES, ids=[c[0] for c in fc.CASES])
def test_geometry_case(tmp_path, case):
    label, svg, exp_text, exp_arrow, exp_bbox = case
    p = tmp_path / "case.svg"
    p.write_text(svg)
    geom = check_svg(p, journal=None, palette=None)["checks"]["geometry"]
    assert geom.get("available") and not geom.get("error"), f"{label}: {geom}"
    assert len(geom["text_overflow"]) == exp_text, f"{label}: text_overflow"
    assert len(geom["arrow_tip_issues"]) == exp_arrow, f"{label}: arrow_tip_issues"
    assert len(geom["bbox_overlaps"]) == exp_bbox, f"{label}: bbox_overlaps"


def test_clean_schematic_has_zero_geometry_findings():
    schematic = ROOT / "plugins" / "figures" / "skills" / "svg-figure" / "examples" / "schematic.svg"
    geom = check_svg(schematic, journal="nature", palette=None)["checks"]["geometry"]
    assert geom["available"] and not geom.get("error")
    assert geom["text_overflow"] == []
    assert geom["arrow_tip_issues"] == []
    assert geom["bbox_overlaps"] == []


@pytest.mark.parametrize(
    "width,vb_w,expected",
    [
        ("100mm", 100, 1.0),
        ("100", 100, 1.0),            # unitless: user units assumed to be mm
        ("960px", 100, 25.4 / 96.0 * 960 / 100),  # 2.54 mm/unit
        ("100pt", 100, 25.4 / 72.0),
        ("10cm", 100, 1.0),
    ],
)
def test_viewbox_mm_per_unit(width, vb_w, expected):
    root = etree.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" viewBox="0 0 {vb_w} 50"/>'.encode()
    )
    assert _viewbox_mm_per_unit(root) == pytest.approx(expected, rel=1e-3)


def test_viewbox_mm_per_unit_comma_separated():
    root = etree.fromstring(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" viewBox="0,0,100,50"/>'.encode()
    )
    assert _viewbox_mm_per_unit(root) == pytest.approx(1.0)


def test_main_exit_codes(tmp_path):
    clean = tmp_path / "clean.svg"
    clean.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="30mm" viewBox="0 0 50 30">'
        '<rect x="5" y="5" width="40" height="20" fill="#fff" stroke="#000"/></svg>'
    )
    assert main([str(clean)]) == 0  # clean -> 0

    collide = tmp_path / "collide.svg"
    collide.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'
        '<rect x="10" y="10" width="20" height="20" fill="#0072B2"/>'
        '<rect x="25" y="15" width="20" height="20" fill="#009E73"/></svg>'
    )
    assert main([str(collide)]) == 1  # one bbox collision -> 1

    assert main([str(tmp_path / "missing.svg")]) == 2  # IO error -> 2


def test_arrows_without_targets_is_surfaced(tmp_path):
    # An arrow aimed at an open <path> box (not a closed Rect/Circle/Ellipse/Polygon):
    # the arrow-tip check cannot run, and that must be reported, not silently clean.
    svg = tmp_path / "a.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="60mm" height="30mm" viewBox="0 0 60 30">'
        '<path d="M40,5 L55,5 L55,25 L40,25" fill="none" stroke="#000"/>'
        '<line x1="5" y1="15" x2="20" y2="15" stroke="#000" marker-end="url(#a)"/></svg>'
    )
    geom = check_svg(svg, journal=None, palette=None)["checks"]["geometry"]
    assert geom["arrow_tip_issues"] == []
    assert geom["arrows_without_targets"] == 1
