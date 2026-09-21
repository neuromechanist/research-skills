"""Deterministic contract coverage for the explicit Atlas icon backend."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

_FIGURES_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_ROOT = _FIGURES_ROOT / "skills" / "transparent-icons" / "scripts"
sys.path.insert(0, str(_SCRIPT_ROOT))

import generate_icon as icon_cli


def test_atlas_output_url_accepts_documented_string_list():
    assert icon_cli._atlas_output_url({"outputs": ["https://example.test/icon.png"]}) == (
        "https://example.test/icon.png"
    )


def test_atlas_output_url_accepts_object_list_and_rejects_missing_output():
    assert icon_cli._atlas_output_url({"outputs": [{"url": "https://example.test/a"}]}) == (
        "https://example.test/a"
    )
    assert icon_cli._atlas_output_url({"status": "completed"}) is None


def test_atlas_requires_explicit_api_key(monkeypatch):
    monkeypatch.delenv("ATLASCLOUD_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ATLASCLOUD_API_KEY"):
        icon_cli.generate_icon_atlas("a test icon")


def test_atlas_output_is_normalized_to_png():
    from PIL import Image

    source = io.BytesIO()
    Image.new("RGB", (4, 4), (12, 34, 56)).save(source, format="JPEG")
    png = icon_cli._ensure_png(source.getvalue())
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
