"""Unit-scaling regression tests for overlay_labels.py.

Reproduces the bug this test guards against: overlay_labels.py used to write
`font_size_pt` as a bare SVG font-size inside a pixel viewBox under an mm root
width, so an 89 mm / 1024 px document with `font_size_pt: 8` rendered at
roughly 2.46 pt -- below every documented journal's font-size minimum. These
tests assert the fix round-trips through validate_fonts.py's own pt-conversion
maths, and that --check and --grid behave as documented.

No conftest.py here by design (scope note in the task); both modules under
test are loaded by file path since neither is an installed package.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from lxml import etree
from PIL import Image

_TESTS_DIR = Path(__file__).resolve().parent
_FIGURES_ROOT = _TESTS_DIR.parent
_OVERLAY_SCRIPT = (
    _FIGURES_ROOT / "skills" / "ai-full-figure" / "scripts" / "overlay_labels.py"
)
_VALIDATE_FONTS_SCRIPT = (
    _FIGURES_ROOT / "skills" / "scientific-figure" / "scripts" / "validate_fonts.py"
)

SVG_NS = "{http://www.w3.org/2000/svg}"


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, (
        f"could not load spec for {path}"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


overlay_labels = _load_module(_OVERLAY_SCRIPT, "test_overlay_labels_module")
validate_fonts = _load_module(_VALIDATE_FONTS_SCRIPT, "test_validate_fonts_module")

WIDTH_MM = 89.0
VIEWBOX_WIDTH_PX = 1024
VIEWBOX_HEIGHT_PX = 576


def _make_substrate(path: Path) -> Path:
    Image.new("RGB", (VIEWBOX_WIDTH_PX, VIEWBOX_HEIGHT_PX), color=(210, 210, 210)).save(
        path
    )
    return path


def _write_labels_file(tmp_path: Path, font_size_pt: float) -> Path:
    doc = {
        "width_mm": WIDTH_MM,
        "labels": [
            {
                "text": "lateral sulcus",
                "x": 200,
                "y": 150,
                "font_size_pt": font_size_pt,
            },
        ],
    }
    labels_path = tmp_path / "labels.json"
    labels_path.write_text(json.dumps(doc))
    return labels_path


def _effective_pt_of_first_text(svg_path: Path) -> float:
    """Parse the emitted <text> font-size and convert it back to points using
    validate_fonts.py's own root-scale maths (not a re-derived formula)."""
    root = etree.parse(str(svg_path)).getroot()
    root_unit_to_pt = validate_fonts._root_unit_to_pt(root)
    text_el = root.find(f".//{SVG_NS}text")
    assert text_el is not None, (
        "expected at least one <text> element in the overlay SVG"
    )
    size_attr = float(text_el.get("font-size"))
    return size_attr * root_unit_to_pt


def test_eight_pt_label_round_trips_to_eight_pt(tmp_path):
    substrate = _make_substrate(tmp_path / "substrate.png")
    labels_file = _write_labels_file(tmp_path, font_size_pt=8.0)
    output = tmp_path / "labeled.svg"

    rc = overlay_labels.main(
        [str(substrate), "-o", str(output), "--labels-file", str(labels_file)]
    )

    assert rc == 0
    assert output.exists()
    effective_pt = _effective_pt_of_first_text(output)
    assert abs(effective_pt - 8.0) < 0.05


def test_units_per_pt_formula_matches_validate_fonts_inverse():
    upt = overlay_labels.units_per_pt(WIDTH_MM, VIEWBOX_WIDTH_PX)
    root_unit_to_pt = (WIDTH_MM * 72.0 / 25.4) / VIEWBOX_WIDTH_PX
    assert abs(upt * root_unit_to_pt - 1.0) < 1e-9


def test_check_passes_at_eight_pt(tmp_path):
    substrate = _make_substrate(tmp_path / "substrate.png")
    labels_file = _write_labels_file(tmp_path, font_size_pt=8.0)
    output = tmp_path / "labeled.svg"

    rc = overlay_labels.main(
        [
            str(substrate),
            "-o",
            str(output),
            "--labels-file",
            str(labels_file),
            "--check",
            "--journal",
            "nature",
        ]
    )

    assert rc == 0


def test_check_fails_below_journal_minimum(tmp_path):
    substrate = _make_substrate(tmp_path / "substrate.png")
    labels_file = _write_labels_file(tmp_path, font_size_pt=3.0)
    output = tmp_path / "labeled.svg"

    rc = overlay_labels.main(
        [
            str(substrate),
            "-o",
            str(output),
            "--labels-file",
            str(labels_file),
            "--check",
            "--journal",
            "nature",
        ]
    )

    assert rc == 1


def test_grid_png_is_written(tmp_path):
    substrate = _make_substrate(tmp_path / "substrate.png")
    output = tmp_path / "labeled.svg"

    rc = overlay_labels.main(
        [str(substrate), "-o", str(output), "--label", "x@10,10", "--grid"]
    )

    assert rc == 0
    grid_path = output.parent / f"{output.stem}.grid.png"
    assert grid_path.exists()
    with Image.open(grid_path) as img:
        assert img.size == (VIEWBOX_WIDTH_PX, VIEWBOX_HEIGHT_PX)
