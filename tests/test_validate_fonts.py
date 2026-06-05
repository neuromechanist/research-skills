"""CI coverage for validate_fonts.py's viewBox-aware physical-point sizing (issue #52).

Drives the same cases as the standalone fixture
(plugins/figures/skills/scientific-figure/examples/validate_failure_case.py) through
pytest, and unit-checks the root user-unit -> point scale for mm/pt/cm/unitless viewBoxes.
Real SVG parsing, no mocks. Needs lxml.

Run: uv run --with pytest --with lxml pytest tests/ -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VF_DIR = ROOT / "plugins" / "figures" / "skills" / "scientific-figure" / "scripts"
EX_DIR = ROOT / "plugins" / "figures" / "skills" / "scientific-figure" / "examples"
sys.path.insert(0, str(VF_DIR))
sys.path.insert(0, str(EX_DIR))

pytest.importorskip("lxml")

from lxml import etree  # noqa: E402
from validate_fonts import _root_unit_to_pt, validate  # noqa: E402
import validate_failure_case as vfc  # noqa: E402


@pytest.mark.parametrize("case", vfc.CASES, ids=[c[0] for c in vfc.CASES])
def test_validate_case(tmp_path, case):
    label, svg, journal, exp_issues, exp_checked, exp_skipped = case
    p = tmp_path / "case.svg"
    p.write_text(svg)
    r = validate(p, journal)
    assert r["issue_count"] == exp_issues, f"{label}: issue_count"
    assert r["checked_count"] == exp_checked, f"{label}: checked_count"
    assert r["skipped_count"] == exp_skipped, f"{label}: skipped_count"


@pytest.mark.parametrize(
    "width,vb_w,expected",
    [
        ("89mm", 89, 72.0 / 25.4),    # mm viewBox -> ~2.835 pt/unit
        ("100mm", 100, 72.0 / 25.4),
        ("10cm", 100, 72.0 / 25.4),   # 10cm = 100mm over 100 units
        ("200pt", 200, 1.0),          # pt viewBox (matplotlib) -> 1.0 pt/unit
        ("2in", 144, 1.0),            # 2in = 144pt over 144 units
        ("100", 100, 1.0),            # unit-less width -> legacy 1:1 (unaffected)
    ],
)
def test_root_unit_to_pt(width, vb_w, expected):
    root = etree.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" viewBox="0 0 {vb_w} 10"/>'.encode()
    )
    assert _root_unit_to_pt(root) == pytest.approx(expected, rel=1e-3)


def test_no_viewbox_is_neutral():
    root = etree.fromstring(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm"/>'
    )
    assert _root_unit_to_pt(root) == 1.0
