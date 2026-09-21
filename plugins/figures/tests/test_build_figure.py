"""Tests for build_figure.py, the multi-panel orchestrator.

Runs the script as a subprocess through `uv run` so it resolves its own
dependencies (svgutils, lxml, cairosvg) independent of whatever the outer
pytest environment has installed, matching how every other script in this
plugin declares its own `--with` requirements.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
BUILD_FIGURE = PLUGIN_ROOT / "skills" / "ai-full-figure" / "scripts" / "build_figure.py"

UV_PREFIX = [
    "uv",
    "run",
    "--with",
    "pillow",
    "--with",
    "svgutils",
    "--with",
    "lxml",
    "--with",
    "cairosvg",
    "python",
    str(BUILD_FIGURE),
]


def _run(spec_path: Path, out_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [
        *UV_PREFIX,
        "--spec",
        str(spec_path),
        "--out",
        str(out_dir),
        "--backend",
        "fake",
        *extra,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)


def test_panels_mode_produces_manifest_svg_and_pngs(tmp_path):
    spec = {
        "layout": "panels",
        "size": "1024x1024",
        "consistency": "none",
        "parallel": 2,
        "panels": [
            {
                "id": "a",
                "subject": "a neuron with dendrites",
                "text": [
                    {"role": "panel-letter", "text": "a", "placement": "top-left"}
                ],
            },
            {
                "id": "b",
                "subject": "a synapse close-up",
                "text": [
                    {"role": "panel-letter", "text": "b", "placement": "top-left"}
                ],
            },
        ],
        "compose": {
            "journal": "nature",
            "columns": 2,
            "gap_mm": 3,
            "label_style": "lowercase",
        },
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec))
    out_dir = tmp_path / "out"

    result = _run(spec_path, out_dir)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"

    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert manifest["layout"] == "panels"
    assert len(manifest["panels"]) == 2
    assert all(p["success"] for p in manifest["panels"])
    assert manifest["qa_commands"], "expected qa_commands in the manifest"
    assert any("check_raster.py" in cmd for cmd in manifest["qa_commands"])

    assert (out_dir / "figure.svg").exists()
    assert (out_dir / "panel_a.png").exists()
    assert (out_dir / "panel_b.png").exists()
    assert manifest["compose"]["svg"] == str(out_dir / "figure.svg")


def test_panels_mode_first_panel_consistency(tmp_path):
    spec = {
        "layout": "panels",
        "size": "1024x1024",
        "consistency": "first-panel",
        "parallel": 2,
        "panels": [
            {"id": "a", "subject": "a neuron"},
            {"id": "b", "subject": "a synapse"},
        ],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec))
    out_dir = tmp_path / "out"

    result = _run(spec_path, out_dir)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert all(p["success"] for p in manifest["panels"])


def test_single_mode_produces_one_png(tmp_path):
    spec = {
        "layout": "single",
        "size": "1024x1024",
        "panels": [
            {
                "id": "a",
                "subject": "a labeled recording setup",
                "text": [
                    {
                        "role": "title",
                        "text": "Setup",
                        "placement": "top-center",
                        "size_class": "large",
                    }
                ],
            }
        ],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec))
    out_dir = tmp_path / "out"

    result = _run(spec_path, out_dir)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"

    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert manifest["layout"] == "single"
    assert Path(manifest["path"]).exists()
    assert len(manifest["qa_commands"]) == 1


def test_panels_mode_rejects_text_ladder_violation(tmp_path):
    spec = {
        "layout": "panels",
        "size": "1024x1024",
        "panels": [
            {
                "id": "a",
                "subject": "a diagram",
                "text": [
                    {
                        "role": "label",
                        "text": "this label has way too many words in it",
                        "placement": "left",
                    }
                ],
            }
        ],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec))
    out_dir = tmp_path / "out"

    result = _run(spec_path, out_dir)
    assert result.returncode == 2, f"stdout={result.stdout}\nstderr={result.stderr}"
    assert not (out_dir / "manifest.json").exists()


def test_panel_failure_exits_1_with_uniform_manifest(tmp_path, monkeypatch):
    """A failed panel must not crash the run: exit 1, and every panel entry in
    manifest.json carries the same keys so downstream tooling can branch on it."""
    import os

    spec = tmp_path / "figure.json"
    spec.write_text(
        json.dumps(
            {
                "layout": "panels",
                "size": "816x816",
                "consistency": "none",
                "panels": [
                    {"id": "a", "subject": "a head", "text": []},
                    {"id": "b", "subject": "a network", "text": []},
                ],
                "compose": {"journal": "nature", "columns": 2},
            }
        )
    )
    out_dir = tmp_path / "out"
    env = dict(os.environ, FIGURES_FAKE_FAIL_SUBSTR="panel_b")
    cmd = [*UV_PREFIX, "--spec", str(spec), "--out", str(out_dir), "--backend", "fake"]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=180, check=False, env=env
    )
    assert proc.returncode == 1, proc.stderr
    manifest = json.loads((out_dir / "manifest.json").read_text())
    key_sets = {tuple(sorted(p.keys())) for p in manifest["panels"]}
    assert len(key_sets) == 1, key_sets
    by_id = {p["id"]: p for p in manifest["panels"]}
    assert by_id["a"]["success"] is True
    assert by_id["b"]["success"] is False
    assert "forced failure" in by_id["b"]["error"]


def test_spec_validation_exits_2(tmp_path):
    spec = tmp_path / "bad.json"
    spec.write_text(
        json.dumps(
            {
                "layout": "panels",
                "panels": [{"id": "a", "subject": "x", "size": "1000x1000"}],
                "compose": {"columns": 0},
            }
        )
    )
    proc = _run(spec, tmp_path / "out", "--backend", "fake")
    assert proc.returncode == 2
    assert "multiple" in proc.stderr or "columns" in proc.stderr
