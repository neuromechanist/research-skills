"""CI coverage for check_svg.py's geometry section (issue #47).

Drives the same synthetic cases as the standalone fixture
(plugins/figures/agents/figure-qa-scripts/examples/check_svg_failure_cases.py) through
pytest, plus a regression that the shipped clean schematic produces zero geometry
findings. Real SVG parsing, no mocks. Needs svgelements / svgpathtools / shapely.

Run: uv run --with pytest --with lxml --with svgelements --with svgpathtools --with shapely pytest tests/ -q
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
from check_svg import check_svg  # noqa: E402


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
