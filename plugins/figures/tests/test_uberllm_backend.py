"""Deterministic contract coverage for the explicit UberLLM icon backend."""

from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path

import pytest

_FIGURES_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_ROOT = _FIGURES_ROOT / "skills" / "transparent-icons" / "scripts"
sys.path.insert(0, str(_SCRIPT_ROOT))

import generate_icon as icon_cli


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _png_bytes() -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_uberllm_requires_explicit_api_key(monkeypatch):
    monkeypatch.delenv("UBERLLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="UBERLLM_API_KEY"):
        icon_cli.generate_icon_uberllm("a test icon")


def test_uberllm_sends_one_request_and_returns_the_inline_png(monkeypatch):
    monkeypatch.setenv("UBERLLM_API_KEY", "ull-test")
    png = _png_bytes()
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        body = {"created": 1, "data": [{"b64_json": base64.b64encode(png).decode()}]}
        return _Response(json.dumps(body).encode())

    monkeypatch.setattr(icon_cli, "urlopen", fake_urlopen)
    assert icon_cli.generate_icon_uberllm("a neuron", size=1024, timeout_s=60) == png

    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.full_url == "https://api.uberllm.dev/v1/images/generations"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == "Bearer ull-test"
    assert timeout == 60
    assert json.loads(request.data) == {
        "model": icon_cli.UBERLLM_DEFAULT_MODEL,
        "prompt": "a neuron",
        "size": "1024x1024",
        "n": 1,
        "response_format": "b64_json",
    }


def test_uberllm_normalizes_jpeg_output_to_png(monkeypatch):
    from PIL import Image

    monkeypatch.setenv("UBERLLM_API_KEY", "ull-test")
    source = io.BytesIO()
    Image.new("RGB", (4, 4), (12, 34, 56)).save(source, format="JPEG")
    body = {"data": [{"b64_json": base64.b64encode(source.getvalue()).decode()}]}
    monkeypatch.setattr(
        icon_cli, "urlopen", lambda request, timeout: _Response(json.dumps(body).encode())
    )
    assert icon_cli.generate_icon_uberllm("a neuron").startswith(b"\x89PNG\r\n\x1a\n")


def test_uberllm_reports_a_response_without_an_image(monkeypatch):
    monkeypatch.setenv("UBERLLM_API_KEY", "ull-test")
    monkeypatch.setattr(
        icon_cli, "urlopen", lambda request, timeout: _Response(b'{"data": []}')
    )
    with pytest.raises(RuntimeError, match="did not include an image"):
        icon_cli.generate_icon_uberllm("a neuron")


def test_uberllm_rejects_invalid_image_data_as_user_error(monkeypatch):
    monkeypatch.setenv("UBERLLM_API_KEY", "ull-test")
    body = {"data": [{"b64_json": base64.b64encode(b"not-an-image").decode()}]}
    monkeypatch.setattr(
        icon_cli, "urlopen", lambda request, timeout: _Response(json.dumps(body).encode())
    )
    with pytest.raises(RuntimeError, match="UberLLM returned invalid image data"):
        icon_cli.generate_icon_uberllm("a neuron")
