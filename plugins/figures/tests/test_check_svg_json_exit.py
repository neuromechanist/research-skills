"""The exit code of check_svg.py must agree with the JSON status: a blocking
finding exits 2 and an unusable palette spec exits 1, in both output modes.

Run: uv run --with pytest --with lxml --with svgelements --with shapely --with pillow \
    pytest plugins/figures/tests/test_check_svg_json_exit.py -q
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

CHECK_SVG = (
    Path(__file__).resolve().parents[1]
    / "agents"
    / "figure-qa-scripts"
    / "check_svg.py"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "figures_check_svg_for_exit_test", CHECK_SVG
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _svg_with_tiny_label(path: Path) -> Path:
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="30mm" viewBox="0 0 50 30">'
        '<rect x="5" y="5" width="40" height="20" fill="#fff" stroke="#000"/>'
        '<text x="10" y="15" font-size="0.8" fill="#000">tiny label</text></svg>'
    )
    return path


def test_font_block_exits_2_in_both_modes(tmp_path, capsys):
    mod = _load()
    svg = _svg_with_tiny_label(tmp_path / "tiny.svg")
    code_json = mod.main([str(svg), "--journal", "nature", "--json"])
    out = capsys.readouterr().out
    envelope = json.loads(out)
    assert envelope["status"] == "block"
    assert any(
        f["check"] == "font_too_small" and f["action"] == "rescale"
        for f in envelope["findings"]
    )
    assert code_json == 2
    code_plain = mod.main([str(svg), "--journal", "nature"])
    capsys.readouterr()
    assert code_plain == 2


def test_unusable_palette_spec_is_not_clean(tmp_path, capsys):
    mod = _load()
    svg = tmp_path / "plain.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="30mm" viewBox="0 0 50 30">'
        '<rect x="5" y="5" width="40" height="20" fill="#0072B2"/></svg>'
    )
    code = mod.main([str(svg), "--palette", "not-a-real-preset", "--json"])
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["status"] != "ship"
    assert code >= 1
