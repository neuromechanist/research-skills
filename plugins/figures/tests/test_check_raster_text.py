"""Coverage for check_raster.py's new --palette compliance and --expect-text
OCR branches (figure-bible epic).

Real Pillow-rendered images and real Pillow/tesseract calls, no mocks.
The OCR-dependent assertions are skipped (not faked) when the tesseract
binary is not on PATH; the JSON envelope shape and the ocr_skipped note are
still asserted unconditionally.

Run: uv run --with pytest --with pillow --with pytesseract \\
    pytest plugins/figures/tests/test_check_raster_text.py -q
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("PIL")

FIGURES_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = FIGURES_ROOT / "agents" / "figure-qa-scripts"
sys.path.insert(0, str(SCRIPTS))

import check_raster as cr

TESSERACT_AVAILABLE = shutil.which("tesseract") is not None
ENVELOPE_KEYS = {"file", "type", "journal", "status", "findings", "measurements"}


def _render_text_png(
    path: Path, text: str, size: tuple[int, int] = (1400, 300), font_size: int = 140
) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    font = None
    for candidate in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            font = ImageFont.truetype(candidate, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    draw.text((60, 70), text, fill="black", font=font)
    img.save(path)
    return path


def _run_json(args: list[str]) -> tuple[dict, int]:
    import contextlib
    import io

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exit_code = cr.main(args)
    return json.loads(buf.getvalue()), exit_code


def test_expect_text_json_shape_and_ocr_skip_note(tmp_path):
    png = _render_text_png(tmp_path / "eeg.png", "EEG recording")
    envelope, exit_code = _run_json(
        [str(png), "--expect-text", "EEG recording", "--width-mm", "89", "--json"]
    )

    # Shape assertions hold regardless of whether tesseract is installed.
    assert set(envelope) == ENVELOPE_KEYS
    assert envelope["type"] == "raster"
    assert envelope["file"] == str(png)
    assert isinstance(envelope["findings"], list)
    text = envelope["measurements"]["text"]
    assert "ocr_skip_reason" in text
    assert "expected" in text and len(text["expected"]) == 1
    assert "unexpected_text" in text

    if not TESSERACT_AVAILABLE:
        assert text["ocr_skip_reason"] is not None
        assert any(
            f["check"] == "ocr_skipped" and f["severity"] == "info"
            for f in envelope["findings"]
        )
        pytest.skip("tesseract not on PATH; OCR-dependent assertions skipped")

    assert text["ocr_skip_reason"] is None
    entry = text["expected"][0]
    assert entry["expected"] == "EEG recording"
    assert entry["found"] is True
    assert entry["cap_height_pt"] > 0
    assert exit_code == {"ship": 0, "revise": 1, "block": 2}[envelope["status"]]


def test_ocr_off_skips_deterministically_and_does_not_block(tmp_path):
    """--ocr off is deterministic regardless of the host's tesseract install,
    so this covers the ocr_skipped note path in every environment."""
    png = _render_text_png(tmp_path / "eeg2.png", "EEG recording")
    envelope, exit_code = _run_json(
        [str(png), "--expect-text", "EEG recording", "--ocr", "off", "--json"]
    )
    text = envelope["measurements"]["text"]
    assert text["ocr_skip_reason"] == "ocr disabled via --ocr off"
    assert text["expected"] == [{"expected": "EEG recording", "found": False}] or all(
        not e["found"] for e in text["expected"]
    )
    ocr_findings = [f for f in envelope["findings"] if f["check"] == "ocr_skipped"]
    assert len(ocr_findings) == 1
    assert ocr_findings[0]["severity"] == "info"
    # OCR did not run, so we cannot claim the text is missing: no block finding.
    assert not any(f["check"] == "text_missing" for f in envelope["findings"])
    assert envelope["status"] != "block"
    assert exit_code in (0, 1)


def _solid_two_color_png(
    path: Path, left_hex: str, right_hex: str, size: tuple[int, int] = (200, 200)
) -> Path:
    from PIL import Image

    def to_rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    img = Image.new("RGB", size, to_rgb(left_hex))
    right = Image.new("RGB", (size[0] // 2, size[1]), to_rgb(right_hex))
    img.paste(right, (size[0] // 2, 0))
    img.save(path)
    return path


def test_palette_compliance_flags_off_palette_colors(tmp_path):
    # Saturated magenta/cyan are far (RGB distance > 30) from every color in
    # okabe-ito and are not near-gray or pure black/white, so both should
    # surface as off-palette findings.
    png = _solid_two_color_png(tmp_path / "offpalette.png", "#FF00FF", "#00FFFF")
    envelope, exit_code = _run_json([str(png), "--palette", "okabe-ito", "--json"])

    compliance = envelope["measurements"]["palette_compliance"]
    assert compliance["available"] is True
    assert compliance["palette"] == "okabe-ito"
    assert compliance["off_palette_count"] >= 1
    for off in compliance["off_palette"]:
        assert off["distance"] > 30

    off_findings = [f for f in envelope["findings"] if f["check"] == "palette_off"]
    assert off_findings, "expected at least one palette_off finding"
    assert all(f["severity"] == "warn" for f in off_findings)
    assert envelope["status"] in ("revise", "block")
    assert exit_code in (1, 2)


def test_palette_compliance_theme_json_path(tmp_path):
    sys.path.insert(0, str(FIGURES_ROOT / "lib"))
    import theme as theme_lib

    theme = theme_lib.theme_defaults("nature", "neuro-flat", "compliance-test")
    theme_path = tmp_path / "theme.json"
    theme_path.write_text(json.dumps(theme))

    png = _solid_two_color_png(tmp_path / "vs_theme.png", "#FF00FF", "#00FFFF")
    envelope, _ = _run_json([str(png), "--palette", str(theme_path), "--json"])

    compliance = envelope["measurements"]["palette_compliance"]
    assert compliance["available"] is True
    assert compliance["palette"] == "compliance-test"
    assert compliance["off_palette_count"] >= 1


def test_unknown_palette_spec_is_a_warn_finding_not_a_crash(tmp_path):
    png = _solid_two_color_png(tmp_path / "plain.png", "#123456", "#654321")
    envelope, exit_code = _run_json(
        [str(png), "--palette", "not-a-real-preset", "--json"]
    )
    compliance = envelope["measurements"]["palette_compliance"]
    assert compliance["available"] is False
    findings = [f for f in envelope["findings"] if f["check"] == "palette_compliance"]
    assert findings and findings[0]["severity"] == "warn"
    assert exit_code in (1, 2)
