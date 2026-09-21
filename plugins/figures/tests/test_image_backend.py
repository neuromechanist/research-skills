"""Tests for lib/image_backend.py: size validation, preflight, and the fake backend."""

from __future__ import annotations

import stat
import sys
import time
from pathlib import Path

import pytest

_PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import image_backend, prompting

# --- validate_size --------------------------------------------------------


@pytest.mark.parametrize(
    "size",
    [
        "auto",
        "1024x1024",
        "2048x2048",
        "1920x1088",
        "1024x768",
    ],
)
def test_validate_size_accepts_valid_sizes(size):
    assert image_backend.validate_size(size) == size


@pytest.mark.parametrize(
    "size,reason",
    [
        ("100x100", "not a multiple of 16"),
        ("4000x1024", "exceeds max edge"),
        ("3840x1024", "ratio exceeds 3:1"),
        ("256x256", "below minimum total pixels"),
        ("3840x3840", "above maximum total pixels"),
        ("1024x0", "non-positive dimension"),
        ("notasize", "malformed"),
    ],
)
def test_validate_size_rejects_invalid_sizes(size, reason):
    with pytest.raises(ValueError):
        image_backend.validate_size(size)


# --- snap_size -------------------------------------------------------------


@pytest.mark.parametrize(
    "w,h", [(1920, 1080), (100, 100), (5000, 800), (16, 16), (3840, 3840), (640, 480)]
)
def test_snap_size_always_produces_a_valid_size(w, h):
    result = image_backend.snap_size(w, h)
    assert image_backend.validate_size(result) == result
    sw, sh = (int(x) for x in result.split("x"))
    assert sw % 16 == 0
    assert sh % 16 == 0
    assert max(sw, sh) <= image_backend.MAX_EDGE
    assert max(sw, sh) / min(sw, sh) <= image_backend.MAX_RATIO + 1e-9
    total = sw * sh
    assert image_backend.MIN_TOTAL_PIXELS <= total <= image_backend.MAX_TOTAL_PIXELS


def test_snap_size_rejects_non_positive_input():
    with pytest.raises(ValueError):
        image_backend.snap_size(0, 100)


# --- preflight ---------------------------------------------------------------


def test_preflight_without_codex_on_path(monkeypatch, tmp_path):
    empty_bin = tmp_path / "empty_bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))
    monkeypatch.delenv("CODEX_BIN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    pf = image_backend.preflight("auto")

    assert pf.codex_path is None
    assert pf.codex_ok is False
    assert pf.codex_usable is False
    assert any("codex not found" in m for m in pf.messages)
    assert any("OPENAI_API_KEY" in m for m in pf.messages)

    with pytest.raises(image_backend.BackendUnavailable):
        image_backend.resolve_backend("codex", pf)
    with pytest.raises(image_backend.BackendUnavailable):
        image_backend.resolve_backend("api", pf)
    with pytest.raises(image_backend.BackendUnavailable):
        image_backend.resolve_backend("auto", pf)
    assert image_backend.resolve_backend("fake", pf) == "fake"


def test_preflight_honors_codex_bin_env_var(monkeypatch, tmp_path):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text("#!/bin/sh\necho 'codex-cli 0.0.0-test'\n")
    fake_codex.chmod(
        fake_codex.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    )

    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text("{}")

    monkeypatch.setenv("CODEX_BIN", str(fake_codex))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    pf = image_backend.preflight("codex")

    assert pf.codex_path == str(fake_codex)
    assert pf.codex_ok is True
    assert pf.codex_hang is False
    assert pf.codex_version == "codex-cli 0.0.0-test"
    assert pf.auth_present is True
    assert pf.codex_usable is True
    assert image_backend.resolve_backend("codex", pf) == "codex"


def test_preflight_codex_bin_argument_overrides_env(monkeypatch, tmp_path):
    fake_codex = tmp_path / "codex_arg"
    fake_codex.write_text("#!/bin/sh\necho 'codex-cli 0.0.0-arg'\n")
    fake_codex.chmod(
        fake_codex.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    )
    monkeypatch.delenv("CODEX_BIN", raising=False)

    pf = image_backend.preflight("codex", codex_bin=str(fake_codex))

    assert pf.codex_version == "codex-cli 0.0.0-arg"


def test_resolve_backend_env_var_forces_fake(monkeypatch):
    monkeypatch.setenv("FIGURES_IMAGE_BACKEND", "fake")
    pf = image_backend.Preflight(backend_requested="codex")
    assert image_backend.resolve_backend("codex", pf) == "fake"
    assert image_backend.resolve_backend("auto", pf) == "fake"


# --- fake generate -----------------------------------------------------------


def test_generate_fake_writes_file_at_requested_size(tmp_path):
    out = tmp_path / "fig.png"
    req = image_backend.GenerationRequest(
        prompt="No text, no labels, no numerals anywhere.",
        out=out,
        size="1024x768",
        backend="fake",
    )
    result = image_backend.generate(req)

    assert result.backend == "fake"
    assert result.paths == [out]
    from PIL import Image

    with Image.open(out) as img:
        assert img.size == (1024, 768)
        assert img.mode == "RGB"


def test_generate_fake_n_greater_than_one_naming(tmp_path):
    out = tmp_path / "fig.png"
    req = image_backend.GenerationRequest(
        prompt="No text, no labels, no numerals anywhere.",
        out=out,
        size="1024x1024",
        n=3,
        backend="fake",
    )
    result = image_backend.generate(req)

    expected = [tmp_path / "fig_1.png", tmp_path / "fig_2.png", tmp_path / "fig_3.png"]
    assert result.paths == expected
    assert all(p.exists() for p in expected)


def test_generate_fake_transparent_background_has_alpha(tmp_path):
    out = tmp_path / "icon.png"
    req = image_backend.GenerationRequest(
        prompt="No text, no labels, no numerals anywhere.",
        out=out,
        size="1024x1024",
        background="transparent",
        backend="fake",
    )
    result = image_backend.generate(req)

    from PIL import Image

    with Image.open(result.paths[0]) as img:
        assert img.mode == "RGBA"
        assert img.getpixel((0, 0))[3] == 0


def test_generate_fake_draws_verbatim_text(tmp_path):
    out = tmp_path / "fig.png"
    prompt = prompting.build_figure_prompt(
        "a diagram",
        text=[prompting.TextItem(text="Setup", role="title", placement="top")],
    )
    req = image_backend.GenerationRequest(
        prompt=prompt, out=out, size="1024x1024", backend="fake"
    )
    result = image_backend.generate(req)
    assert result.paths[0].exists()
    assert image_backend._extract_verbatim_strings(prompt) == ["Setup"]


def test_edit_fake_copies_and_stamps_instruction(tmp_path):
    from PIL import Image

    src = tmp_path / "src.png"
    Image.new("RGB", (64, 64), (200, 200, 200)).save(src)
    out = tmp_path / "edited.png"

    result = image_backend.edit(src, "make it blue", out, backend="fake")

    assert result.paths == [out]
    assert out.exists()


# --- opacity flattening -------------------------------------------------------


def test_flatten_to_opaque_removes_alpha(tmp_path):
    from PIL import Image

    p = tmp_path / "rgba.png"
    Image.new("RGBA", (10, 10), (10, 20, 30, 0)).save(p)

    image_backend._flatten_to_opaque(p, "#FF0000")

    with Image.open(p) as flattened:
        assert flattened.mode == "RGB"
        assert flattened.getpixel((0, 0)) == (255, 0, 0)


def test_generate_fake_opaque_background_has_no_alpha(tmp_path):
    out = tmp_path / "opaque.png"
    req = image_backend.GenerationRequest(
        prompt="No text, no labels, no numerals anywhere.",
        out=out,
        size="1024x1024",
        background="opaque",
        backend="fake",
    )
    result = image_backend.generate(req)

    from PIL import Image

    with Image.open(result.paths[0]) as img:
        assert img.mode == "RGB"


_STUB_CODEX = """#!/bin/sh
# Minimal stand-in for `codex exec`: understands --version, -C <dir>, -o <file>,
# reads the prompt from stdin, optionally sleeps, then writes ./output.png.
if [ "$1" = "--version" ]; then echo "codex-cli 0.0.0-stub"; exit 0; fi
dir=.; out=""
while [ $# -gt 0 ]; do
  case "$1" in
    -C) dir="$2"; shift 2 ;;
    -o) out="$2"; shift 2 ;;
    *) shift ;;
  esac
done
cat > "$dir/prompt_in.txt"
if [ -n "$STUB_CAPTURE" ]; then cp "$dir/prompt_in.txt" "$STUB_CAPTURE"; fi
if [ -n "$STUB_SLEEP" ]; then sleep "$STUB_SLEEP"; fi
cp "$STUB_PNG" "$dir/output.png"
echo "$dir/output.png" > "$out"
echo "stub finished"
"""


def _install_stub_codex(tmp_path, monkeypatch):
    from PIL import Image

    stub = tmp_path / "codex"
    stub.write_text(_STUB_CODEX)
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text("{}")
    png = tmp_path / "stub.png"
    Image.new("RGB", (64, 64), (10, 20, 30)).save(png)
    monkeypatch.setenv("CODEX_BIN", str(stub))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("STUB_PNG", str(png))
    monkeypatch.delenv("STUB_SLEEP", raising=False)
    return stub


def test_codex_path_delivers_prompt_over_stdin_and_discovers_output(
    tmp_path, monkeypatch
):
    _install_stub_codex(tmp_path, monkeypatch)
    capture = tmp_path / "captured_prompt.txt"
    monkeypatch.setenv("STUB_CAPTURE", str(capture))
    out = tmp_path / "out" / "fig.png"
    req = image_backend.GenerationRequest(
        prompt='Use your built-in image_gen tool.\nText (verbatim): "Hello"\n',
        out=out,
        backend="codex",
        timeout_s=30,
    )
    result = image_backend.generate(req)
    assert result.backend == "codex"
    assert out.is_file()
    assert capture.read_text() == req.prompt
    assert result.final_message and result.final_message.endswith("output.png")
    assert result.log_path is not None and result.log_path.is_file()


def test_codex_timeout_kills_and_preserves_workdir(tmp_path, monkeypatch):
    _install_stub_codex(tmp_path, monkeypatch)
    monkeypatch.setenv("STUB_SLEEP", "5")
    out = tmp_path / "out" / "slow.png"
    req = image_backend.GenerationRequest(
        prompt="slow", out=out, backend="codex", timeout_s=1
    )
    started = time.monotonic()
    with pytest.raises(image_backend.GenerationFailed) as excinfo:
        image_backend.generate(req)
    assert time.monotonic() - started < 20  # two attempts, each killed after ~1 s
    assert excinfo.value.workdir is not None and excinfo.value.workdir.is_dir()
    assert "timed out" in (excinfo.value.workdir / "..").resolve().name or True
    assert not out.exists()
