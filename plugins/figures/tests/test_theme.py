"""Coverage for plugins/figures/lib/theme.py: the shared theme-bible helpers
used by figure-bible's scripts and by check_svg.py/check_raster.py's
--palette resolution.

Real JSON/schema validation, no mocks. Runs with or without jsonschema
installed (validate_theme() falls back to a hand-written structural check).

Run: uv run --with pytest --with jsonschema pytest plugins/figures/tests/test_theme.py -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FIGURES_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FIGURES_ROOT / "lib"))

import theme as theme_lib


@pytest.mark.parametrize("journal", sorted(theme_lib.JOURNAL_PROFILES))
@pytest.mark.parametrize("preset", sorted(theme_lib.PALETTE_PRESETS))
def test_theme_defaults_validate(journal, preset):
    theme = theme_lib.theme_defaults(journal, preset, theme_id="t-" + journal)
    problems = theme_lib.validate_theme(theme)
    errors = [p for p in problems if not p.startswith("warning:")]
    assert errors == [], f"{journal}/{preset}: {errors}"


def test_theme_defaults_unknown_journal_raises():
    with pytest.raises(ValueError):
        theme_lib.theme_defaults("not-a-journal")


def test_theme_defaults_unknown_preset_raises():
    with pytest.raises(ValueError):
        theme_lib.theme_defaults("nature", preset="not-a-preset")


def test_bad_hex_fails_validation():
    theme = theme_lib.theme_defaults("nature", "okabe-ito", "bad-hex-theme")
    theme["palette"]["primary"] = "not-a-hex-color"
    problems = theme_lib.validate_theme(theme)
    errors = [p for p in problems if not p.startswith("warning:")]
    assert errors, "expected a validation problem for an invalid hex color"
    assert any("primary" in e for e in errors)


def test_missing_required_key_fails_validation():
    theme = {"palette": {"primary": "#000000"}}  # missing theme_id and style_tokens
    problems = theme_lib.validate_theme(theme)
    errors = [p for p in problems if not p.startswith("warning:")]
    assert errors


def test_low_contrast_background_primary_warns():
    theme = theme_lib.theme_defaults("nature", "neuro-flat", "low-contrast")
    theme["palette"]["background"] = "#FFFFFF"
    theme["palette"]["primary"] = "#F4F1DE"  # cream on white: low contrast
    problems = theme_lib.validate_theme(theme)
    warnings = [p for p in problems if p.startswith("warning:")]
    assert warnings, "expected a low-contrast warning for near-white-on-white"


def test_resolve_palette_preset():
    name, hexes = theme_lib.resolve_palette("okabe-ito")
    assert name == "okabe-ito"
    assert hexes == theme_lib.PALETTE_PRESETS["okabe-ito"]


def test_resolve_palette_preset_case_insensitive():
    name, hexes = theme_lib.resolve_palette("Neuro-Flat")
    assert name == "neuro-flat"
    assert hexes[0] == "#1F3A5F"


def test_resolve_palette_theme_file(tmp_path):
    theme = theme_lib.theme_defaults("nature", "tol-bright", "from-file")
    theme_path = tmp_path / "theme.json"
    theme_path.write_text(json.dumps(theme))
    name, hexes = theme_lib.resolve_palette(str(theme_path))
    assert name == "from-file"
    assert hexes[0] == theme["palette"]["primary"]
    assert set(theme["palette"]["categorical"]).issubset(set(hexes))


def test_resolve_palette_unknown_raises():
    with pytest.raises(ValueError):
        theme_lib.resolve_palette("definitely-not-a-known-preset-or-path.json")


def test_palette_hexes_role_order():
    theme = {
        "theme_id": "order-test",
        "style_tokens": [],
        "palette": {
            "primary": "#111111",
            "accent": "#222222",
            "neutral": "#333333",
            "background": "#444444",
            "categorical": ["#555555", "#666666"],
        },
    }
    assert theme_lib.palette_hexes(theme) == [
        "#111111",
        "#222222",
        "#333333",
        "#444444",
        "#555555",
        "#666666",
    ]


def test_palette_hexes_skips_transparent_and_legacy_bg():
    theme = {
        "theme_id": "legacy",
        "style_tokens": [],
        "palette": {"primary": "#111111", "bg": "#AAAAAA"},
    }
    hexes = theme_lib.palette_hexes(theme)
    assert hexes == ["#111111", "#AAAAAA"]


def test_load_theme_round_trips(tmp_path):
    theme = theme_lib.theme_defaults("science", "wong", "round-trip")
    theme_path = tmp_path / "theme.json"
    theme_path.write_text(json.dumps(theme))
    loaded = theme_lib.load_theme(theme_path)
    assert loaded == theme


def test_load_theme_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        theme_lib.load_theme(tmp_path / "does-not-exist.json")
