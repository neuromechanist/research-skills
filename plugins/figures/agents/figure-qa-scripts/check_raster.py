"""Programmatic raster (PNG/JPG/TIFF) checks for figure-qa.

Detects:
- Alpha-channel correctness (does the file claim transparency? are the corners
  actually transparent?)
- Pure-white border (only reported as an issue when --expect-transparent is
  set; otherwise informational, since ai-full-figure substrates and journal-
  margined PNGs legitimately have white backgrounds)
- Resolution and DPI vs the journal target
- Dominant colors vs a bible palette (--palette <preset|theme.json>): each
  dominant color's nearest palette color and RGB distance
- On-image text (--expect-text, repeatable): OCR via tesseract, fuzzy match
  (Levenshtein <= 1) against expected strings, bounding boxes, unexpected
  text, and (with --width-mm) cap height vs the journal's minimum point size

Run from anywhere:

    uv run --with pillow --with pytesseract \\
        python check_raster.py FIGURE.png [--journal nature] \\
        [--expect-transparent] [--palette okabe-ito|theme.json] \\
        [--expect-text "EEG recording" --width-mm 89] [--json]

Default output is a single JSON document (the per-check report) on stdout.
With --json, stdout carries only the unified finding envelope described in
_build_envelope(); human-readable summaries always go to stderr.

Exit codes: 0 ship (no findings), 1 revise (warn-severity findings only),
2 block (a block-severity finding, e.g. missing verbatim text, or a script
error such as a corrupt image / failed OCR run).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

# We import Pillow and pytesseract lazily so the help screen runs
# even if uv's --with block is missing one of them.

JOURNAL_MIN_DPI: dict[str, int] = {
    "nature": 300,  # 300 DPI halftone; 600 DPI line art
    "science": 300,  # 300 DPI halftone; 1200 DPI line art
    "cell": 300,
    "pnas": 300,
    "poster": 150,  # large format, viewed from a distance
    "slide": 96,  # screen projection
    "generic": 300,
}

# Fallback minimum point size, used only when lib/theme.py cannot be imported.
_FALLBACK_MIN_PT: dict[str, float] = {
    "nature": 5.0,
    "science": 5.0,
    "cell": 5.0,
    "pnas": 5.0,
    "poster": 18.0,
    "slide": 18.0,
    "generic": 5.0,
}

_FALLBACK_PALETTE_PRESETS: dict[str, list[str]] = {
    "okabe-ito": [
        "#000000",
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
    ],
    "tol-bright": [
        "#4477AA",
        "#EE6677",
        "#228833",
        "#CCBB44",
        "#66CCEE",
        "#AA3377",
        "#BBBBBB",
    ],
    "neuro-flat": [
        "#1F3A5F",
        "#E07A5F",
        "#F4F1DE",
        "#C45146",
        "#2A6F3D",
        "#7E57C2",
    ],
}
_FALLBACK_PALETTE_PRESETS["wong"] = _FALLBACK_PALETTE_PRESETS["okabe-ito"]


def _load_theme_lib():  # type: ignore[no-untyped-def]
    """Import plugins/figures/lib/theme.py by file path under a unique module
    name (a bare ``import theme`` could collide with an unrelated module).
    Returns the module, or None when the lib is missing or fails to import."""
    import importlib.util

    lib_path = Path(__file__).resolve().parents[2] / "lib" / "theme.py"
    if not lib_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("figures_theme_lib", lib_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, SyntaxError, OSError):
        return None
    return module


def _open(image_path: Path):  # type: ignore[no-untyped-def]
    from PIL import Image  # type: ignore[import-not-found]

    return Image.open(str(image_path))


def _alpha_report(img, expect_transparent: bool) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """Check whether the image actually has a usable alpha channel and whether
    transparent corners suggest a transparent background as expected."""
    mode = img.mode
    has_alpha = mode in ("RGBA", "LA", "PA")
    info: dict[str, Any] = {"mode": mode, "has_alpha_channel": has_alpha}

    if not has_alpha:
        if expect_transparent:
            info["issue"] = (
                "image is opaque but caller expected transparency. "
                f"mode={mode}; convert to RGBA and apply background removal."
            )
        return info

    # Sample the four corners; a transparent-background icon should be alpha=0
    # there. We don't sample interior points because flat icons with thin lines
    # have lots of legitimately-zero alpha pixels inside.
    w, h = img.size
    rgba = img.convert("RGBA")
    corners = {
        "top_left": rgba.getpixel((0, 0)),
        "top_right": rgba.getpixel((w - 1, 0)),
        "bottom_left": rgba.getpixel((0, h - 1)),
        "bottom_right": rgba.getpixel((w - 1, h - 1)),
    }
    info["corner_pixels"] = {k: list(v) for k, v in corners.items()}
    transparent_corners = sum(1 for v in corners.values() if v[3] == 0)
    info["transparent_corner_count"] = transparent_corners
    if expect_transparent and transparent_corners < 4:
        info["issue"] = (
            f"expected transparent background; only {transparent_corners}/4 corners "
            "have alpha=0. The threshold method may have left a near-white tint; "
            "consider rembg/BiRefNet for cleaner edges."
        )
    return info


def _white_background_report(img, expect_transparent: bool) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """For opaque images, sample corners to report whether all four are pure-white.
    Flag as an issue only when the caller asserted `--expect-transparent`; otherwise
    a pure-white border is plausibly intentional (e.g., ai-full-figure substrates,
    journal-required white margins)."""
    if img.mode in ("RGBA", "LA", "PA"):
        return {
            "applicable": False,
            "reason": "image has alpha channel; use alpha_report instead",
        }
    rgb = img.convert("RGB")
    w, h = rgb.size
    corners = [
        rgb.getpixel((0, 0)),
        rgb.getpixel((w - 1, 0)),
        rgb.getpixel((0, h - 1)),
        rgb.getpixel((w - 1, h - 1)),
    ]
    pure_white = sum(1 for c in corners if all(v >= 250 for v in c[:3]))
    out: dict[str, Any] = {
        "applicable": True,
        "corner_pixels": [list(c) for c in corners],
        "pure_white_corner_count": pure_white,
    }
    if pure_white == 4 and expect_transparent:
        out["issue"] = (
            "expected transparent background but all four corners are pure-white; "
            "the image appears opaque. Re-export with transparent=True or run "
            "rembg/BiRefNet."
        )
    elif pure_white == 4:
        out["note"] = (
            "all four corners pure-white — image is opaque. Intentional for "
            "ai-full-figure substrates and journal-margined PNGs; pass "
            "--expect-transparent to flag as an issue."
        )
    else:
        out["note"] = "no all-white border detected."
    return out


def _resolution_report(img, journal: str | None) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """Report image size in pixels and DPI vs the journal's minimum."""
    out: dict[str, Any] = {"size_px": list(img.size)}
    dpi = img.info.get("dpi")
    if dpi:
        out["dpi"] = list(dpi) if isinstance(dpi, tuple) else dpi
        min_dpi = JOURNAL_MIN_DPI.get((journal or "generic").lower(), 300)
        # Guard against malformed metadata (e.g., empty TIFF DPI tuple).
        if isinstance(dpi, tuple) and not dpi:
            out["note"] = "DPI metadata present but empty; treat as missing."
            out["dpi"] = None
        else:
            x_dpi = dpi[0] if isinstance(dpi, tuple) else dpi
            # Pillow stores DPI as a float and 300 round-trips slightly under
            # (299.9994 on save/load). Allow 0.1 DPI slack so common honest cases
            # don't trip the threshold.
            if x_dpi < min_dpi - 0.1:
                out["issue"] = f"DPI {x_dpi} below journal minimum {min_dpi}."
    else:
        out["dpi"] = None
        out["note"] = (
            "no DPI metadata; raster files without DPI default to ~72 in many "
            "print workflows. Re-export with explicit dpi=300 or higher."
        )
    return out


def _dominant_colors(
    image_path: Path, count: int = 6
) -> tuple[tuple[int, int, int], list[tuple[int, int, int]]]:
    """Dominant colour and a small palette via Pillow's median-cut quantizer
    (no third-party colour library). Fully transparent pixels are composited
    onto white first so an icon's cutout background does not count as a colour."""
    from PIL import Image

    img = Image.open(image_path).convert("RGBA")
    img.thumbnail((200, 200))
    if img.getchannel("A").getextrema()[0] == 0:
        opaque = Image.new("RGBA", img.size, (255, 255, 255, 255))
        opaque.paste(img, mask=img.getchannel("A"))
        img = opaque
    rgb = img.convert("RGB")
    quantized = rgb.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = sorted(quantized.getcolors(maxcolors=count * 4) or [], reverse=True)
    colors: list[tuple[int, int, int]] = []
    for _n, index in counts:
        base = index * 3
        colors.append((palette[base], palette[base + 1], palette[base + 2]))
    if not colors:
        raise ValueError("image has no colours")
    return colors[0], colors


def _palette_report(image_path: Path) -> dict[str, Any]:
    """Extract the dominant colors with Pillow. This is informational only:
    the section reports the observed palette so the agent can pass it through
    VLM judgment. Failures are surfaced as 'script_error'."""
    try:
        dominant, palette = _dominant_colors(image_path)
    except (OSError, ValueError) as exc:
        return {
            "available": True,
            "script_error": True,
            "error": f"dominant-colour extraction failed: {exc}",
        }
    return {
        "available": True,
        "dominant_rgb": list(dominant),
        "palette_rgb": [list(c) for c in palette],
    }


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    elif len(s) == 4:
        s = "".join(c * 2 for c in s[:3])
    elif len(s) == 8:
        s = s[:6]
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def _rgb_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _is_near_gray(rgb: tuple[int, int, int], tol: int = 15) -> bool:
    return (
        abs(rgb[0] - rgb[1]) <= tol
        and abs(rgb[1] - rgb[2]) <= tol
        and abs(rgb[0] - rgb[2]) <= tol
    )


def _is_pure_bw(rgb: tuple[int, int, int], tol: int = 5) -> bool:
    return all(c <= tol for c in rgb) or all(c >= 255 - tol for c in rgb)


def _resolve_palette_hexes(spec: str, theme_lib) -> tuple[str, list[str]]:  # type: ignore[no-untyped-def]
    if theme_lib is not None:
        return theme_lib.resolve_palette(spec)
    key = spec.lower()
    if key in _FALLBACK_PALETTE_PRESETS:
        return key, list(_FALLBACK_PALETTE_PRESETS[key])
    path = Path(spec)
    if path.exists():
        theme = json.loads(path.read_text())
        palette = theme.get("palette") or {}
        hexes = [
            v for v in palette.values() if isinstance(v, str) and v.startswith("#")
        ]
        for arr_key in ("categorical", "sequential", "diverging"):
            hexes += [
                c
                for c in palette.get(arr_key, [])
                if isinstance(c, str) and c.startswith("#")
            ]
        if not hexes:
            raise ValueError(f"{path}: theme has no usable hex colors in its palette")
        return str(theme.get("theme_id") or path.stem), hexes
    raise ValueError(
        f"'{spec}' is neither a known palette preset ({sorted(_FALLBACK_PALETTE_PRESETS)}) "
        "nor an existing theme.json path"
    )


def _palette_compliance_report(
    image_path: Path, palette_spec: str, theme_lib
) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """Dominant-color compliance against a bible palette. Near-gray and
    pure-black/white samples are exempt, matching check_svg.py's rule."""
    try:
        name, hexes = _resolve_palette_hexes(palette_spec, theme_lib)
    except ValueError as exc:
        return {"palette": palette_spec, "available": False, "reason": str(exc)}
    try:
        dominant, palette_rgb = _dominant_colors(image_path)
    except (OSError, ValueError) as exc:
        return {
            "palette": name,
            "available": True,
            "script_error": True,
            "error": f"dominant-colour extraction failed: {exc}",
        }

    allowed_rgb = [_hex_to_rgb(h) for h in hexes]
    colors_checked: list[dict[str, Any]] = []
    off_palette: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int]] = set()
    for rgb in [tuple(dominant), *[tuple(c) for c in palette_rgb]]:
        if rgb in seen:
            continue
        seen.add(rgb)
        if _is_near_gray(rgb) or _is_pure_bw(rgb):
            continue
        distances = [(_rgb_distance(rgb, a), h) for a, h in zip(allowed_rgb, hexes)]
        dist, nearest_hex = min(distances, key=lambda t: t[0])
        entry = {"rgb": list(rgb), "nearest": nearest_hex, "distance": round(dist, 2)}
        colors_checked.append(entry)
        if dist > 30:
            off_palette.append(entry)

    return {
        "palette": name,
        "available": True,
        "colors_checked": colors_checked,
        "off_palette_count": len(off_palette),
        "off_palette": off_palette,
    }


def _levenshtein(a: str, b: str) -> int:
    """Standard edit distance (insert/delete/substitute), iterative DP."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[-1]


def _run_ocr(image_path: Path, mode: str) -> tuple[list[dict[str, Any]], str | None]:
    """Return (words, skip_reason). skip_reason is None on a successful OCR
    run, even one that found zero words; it is set whenever OCR did not run
    at all (disabled, binary missing, or a runtime failure)."""
    if mode == "off":
        return [], "ocr disabled via --ocr off"

    tesseract_bin = shutil.which("tesseract")
    if tesseract_bin is None:
        reason = "tesseract binary not found on PATH"
        if mode == "tesseract":
            reason += " (explicitly requested via --ocr tesseract)"
        return [], reason

    try:
        import pytesseract  # type: ignore[import-not-found]
    except ImportError:
        return (
            [],
            "pytesseract not installed; re-run with --with pytesseract --with pillow",
        )

    img = _open(image_path)
    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    except Exception as exc:  # noqa: BLE001 - tesseract subprocess can fail many host-specific ways; name it, don't crash
        return [], f"tesseract OCR failed: {type(exc).__name__}: {exc}"

    words: list[dict[str, Any]] = []
    for i, raw_text in enumerate(data.get("text", [])):
        text = raw_text.strip()
        if not text:
            continue
        try:
            conf = float(data["conf"][i])
        except (KeyError, IndexError, ValueError):
            conf = -1.0
        words.append(
            {
                "text": text,
                "conf": conf,
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
            }
        )
    return words, None


def _bbox_union(words: list[dict[str, Any]]) -> dict[str, int]:
    lefts = [w["left"] for w in words]
    tops = [w["top"] for w in words]
    rights = [w["left"] + w["width"] for w in words]
    bottoms = [w["top"] + w["height"] for w in words]
    return {
        "left": min(lefts),
        "top": min(tops),
        "right": max(rights),
        "bottom": max(bottoms),
    }


def _match_expected_text(
    expected: str, ocr_words: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Sliding word-window fuzzy match: try window lengths near the expected
    word count (OCR sometimes splits or merges tokens) and accept the lowest
    Levenshtein distance <= 1."""
    expected_norm = " ".join(expected.lower().split())
    n_words = max(1, len(expected_norm.split()))
    best: dict[str, Any] | None = None
    for window_len in sorted({max(1, n_words - 1), n_words, n_words + 1}):
        for start in range(max(0, len(ocr_words) - window_len + 1)):
            window = ocr_words[start : start + window_len]
            joined = " ".join(w["text"] for w in window).lower()
            dist = _levenshtein(joined, expected_norm)
            if dist <= 1 and (best is None or dist < best["distance"]):
                best = {
                    "distance": dist,
                    "words": window,
                    "matched_text": " ".join(w["text"] for w in window),
                }
    if best is None:
        return None
    return {
        "distance": best["distance"],
        "matched_text": best["matched_text"],
        "bbox": _bbox_union(best["words"]),
        "word_ids": {id(w) for w in best["words"]},
    }


def _journal_min_pt(journal: str | None, theme_lib) -> float:  # type: ignore[no-untyped-def]
    key = (journal or "generic").lower()
    if theme_lib is not None and key in theme_lib.JOURNAL_PROFILES:
        return float(theme_lib.JOURNAL_PROFILES[key]["min_pt"])
    return _FALLBACK_MIN_PT.get(key, 5.0)


def _text_report(
    image_path: Path,
    img,  # type: ignore[no-untyped-def]
    expect_text: list[str],
    ocr_mode: str,
    width_mm: float | None,
    journal: str | None,
    theme_lib,  # type: ignore[no-untyped-def]
) -> dict[str, Any]:
    words, skip_reason = _run_ocr(image_path, ocr_mode)
    out: dict[str, Any] = {
        "ocr_engine": "tesseract" if skip_reason is None else "skipped",
        "ocr_skip_reason": skip_reason,
        "expected": [],
        "unexpected_text": [],
    }
    if skip_reason is not None:
        return out

    used_ids: set[int] = set()
    min_pt = _journal_min_pt(journal, theme_lib)
    img_w_px = img.size[0]
    for expected in expect_text:
        match = _match_expected_text(expected, words)
        entry: dict[str, Any] = {"expected": expected, "found": match is not None}
        if match is not None:
            used_ids |= match["word_ids"]
            entry["matched_text"] = match["matched_text"]
            entry["distance"] = match["distance"]
            entry["bbox_px"] = match["bbox"]
            if width_mm:
                px_to_mm = width_mm / img_w_px
                height_px = match["bbox"]["bottom"] - match["bbox"]["top"]
                # OCR boxes span ascender to descender; the cap height of common
                # sans-serif faces is about 0.7 of that box (Helvetica 0.72,
                # Arial 0.72, DejaVu Sans 0.73), so this errs slightly conservative.
                cap_height_mm = height_px * 0.7 * px_to_mm
                cap_height_pt = cap_height_mm * 72.0 / 25.4
                entry["cap_height_mm"] = round(cap_height_mm, 3)
                entry["cap_height_pt"] = round(cap_height_pt, 2)
                entry["min_pt_required"] = min_pt
                entry["too_small"] = cap_height_pt < min_pt
        out["expected"].append(entry)

    out["unexpected_text"] = [
        {"text": w["text"], "conf": w["conf"]}
        for w in words
        if id(w) not in used_ids and w["conf"] > 60
    ]
    return out


def check_raster(
    image_path: Path,
    journal: str | None,
    expect_transparent: bool,
    palette: str | None,
    expect_text: list[str],
    ocr_mode: str,
    width_mm: float | None,
) -> dict[str, Any]:
    theme_lib = _load_theme_lib()
    img = _open(image_path)
    checks: dict[str, Any] = {
        "alpha": _alpha_report(img, expect_transparent),
        "white_background": _white_background_report(img, expect_transparent),
        "resolution": _resolution_report(img, journal),
        "palette": _palette_report(image_path),
    }
    if palette:
        checks["palette_compliance"] = _palette_compliance_report(
            image_path, palette, theme_lib
        )
    if expect_text:
        checks["text"] = _text_report(
            image_path, img, expect_text, ocr_mode, width_mm, journal, theme_lib
        )
    return {"input": str(image_path), "checks": checks}


def _findings_from_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize every check section into the shared finding shape used by
    both check_raster.py and check_svg.py's --json output."""
    findings: list[dict[str, Any]] = []
    checks = report.get("checks", {})

    alpha = checks.get("alpha") or {}
    if alpha.get("issue"):
        findings.append(
            {
                "check": "alpha",
                "severity": "warn",
                "message": alpha["issue"],
                "action": "regenerate",
                "hint": None,
            }
        )

    white_bg = checks.get("white_background") or {}
    if white_bg.get("issue"):
        findings.append(
            {
                "check": "white_background",
                "severity": "warn",
                "message": white_bg["issue"],
                "action": "regenerate",
                "hint": None,
            }
        )

    resolution = checks.get("resolution") or {}
    if resolution.get("issue"):
        findings.append(
            {
                "check": "resolution",
                "severity": "warn",
                "message": resolution["issue"],
                "action": "regenerate",
                "hint": "re-export at a higher DPI",
            }
        )

    palette_section = checks.get("palette") or {}
    if palette_section.get("script_error"):
        findings.append(
            {
                "check": "palette",
                "severity": "block",
                "message": palette_section["error"],
                "action": "none",
                "hint": None,
            }
        )

    compliance = checks.get("palette_compliance")
    if compliance is not None:
        if compliance.get("script_error"):
            findings.append(
                {
                    "check": "palette_compliance",
                    "severity": "block",
                    "message": compliance["error"],
                    "action": "none",
                    "hint": None,
                }
            )
        elif compliance.get("available") is False:
            findings.append(
                {
                    "check": "palette_compliance",
                    "severity": "warn",
                    "message": compliance["reason"],
                    "action": "none",
                    "hint": "pass a valid preset name or theme.json path to --palette",
                }
            )
        else:
            for off in compliance.get("off_palette", []):
                findings.append(
                    {
                        "check": "palette_off",
                        "severity": "warn",
                        "message": f"color rgb{tuple(off['rgb'])} is {off['distance']} from nearest palette color {off['nearest']}",
                        "action": "recolor",
                        "hint": f"nearest palette color: {off['nearest']}",
                    }
                )

    text = checks.get("text")
    if text is not None:
        if text.get("ocr_skip_reason"):
            findings.append(
                {
                    "check": "ocr_skipped",
                    "severity": "info",
                    "message": text["ocr_skip_reason"],
                    "action": "none",
                    "hint": None,
                }
            )
        for entry in text.get("expected", []):
            if not entry["found"]:
                findings.append(
                    {
                        "check": "text_missing",
                        "severity": "block",
                        "message": f"expected text not found via OCR: '{entry['expected']}'",
                        "action": "regenerate",
                        "hint": f'add literal on-image text via the model prompt: Text (verbatim): "{entry["expected"]}"',
                    }
                )
            elif entry.get("too_small"):
                findings.append(
                    {
                        "check": "text_too_small",
                        "severity": "block",
                        "message": (
                            f"'{entry['expected']}' measures {entry['cap_height_pt']} pt, "
                            f"below the {entry['min_pt_required']} pt minimum"
                        ),
                        "action": "regenerate",
                        "hint": "increase relative text size in the prompt or overlay the label instead",
                    }
                )
        if text.get("unexpected_text"):
            words = ", ".join(f"'{w['text']}'" for w in text["unexpected_text"])
            findings.append(
                {
                    "check": "unexpected_text",
                    "severity": "info",
                    "message": f"OCR found text not in --expect-text: {words}",
                    "action": "none",
                    "hint": None,
                }
            )

    return findings


def _status_and_exit(findings: list[dict[str, Any]]) -> tuple[str, int]:
    severities = {f["severity"] for f in findings}
    if "block" in severities:
        return "block", 2
    if "warn" in severities:
        return "revise", 1
    return "ship", 0


def _build_envelope(
    report: dict[str, Any], journal: str | None
) -> tuple[dict[str, Any], int]:
    findings = _findings_from_report(report)
    status, exit_code = _status_and_exit(findings)
    envelope = {
        "file": report["input"],
        "type": "raster",
        "journal": journal,
        "status": status,
        "findings": findings,
        "measurements": report["checks"],
    }
    return envelope, exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Programmatic raster checks for figure-qa."
    )
    parser.add_argument(
        "image", type=Path, help="Raster image to inspect (.png, .jpg, .tif)"
    )
    parser.add_argument(
        "--journal",
        choices=["nature", "science", "cell", "pnas", "poster", "slide", "generic"],
        help="Target journal or venue (sets DPI and text-size minimums).",
    )
    parser.add_argument(
        "--expect-transparent",
        action="store_true",
        help="Caller asserts the image should have a transparent background; corners flagged if not.",
    )
    parser.add_argument(
        "--palette",
        help="Palette preset name (okabe-ito, tol-bright, wong, neuro-flat) or a path to a theme.json.",
    )
    parser.add_argument(
        "--expect-text",
        action="append",
        default=[],
        metavar="STR",
        help="Verbatim text expected on the image (repeatable).",
    )
    parser.add_argument(
        "--ocr",
        choices=["auto", "tesseract", "off"],
        default="auto",
        help="OCR engine selection. auto (default) uses tesseract when it is on PATH, else skips with a note.",
    )
    parser.add_argument(
        "--width-mm",
        type=float,
        help="Physical width of the image in millimetres, used to convert matched text height to points.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the unified finding envelope instead of the per-check report.",
    )
    args = parser.parse_args(argv)

    if not args.image.exists():
        print(f"error: image not found: {args.image}", file=sys.stderr)
        return 2
    try:
        report = check_raster(
            args.image,
            args.journal,
            args.expect_transparent,
            args.palette,
            args.expect_text,
            args.ocr,
            args.width_mm,
        )
    except ImportError as exc:
        print(
            f"error: missing dependency for check_raster.py — re-run with "
            f"--with pillow [--with pytesseract]: {exc}",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:  # noqa: BLE001 - Pillow/OCR can fail many ways on a corrupt file; name it, don't crash
        print(
            f"error ({type(exc).__name__}): could not analyze '{args.image}': {exc}",
            file=sys.stderr,
        )
        return 2

    envelope, exit_code = _build_envelope(report, args.journal)

    if args.json:
        json.dump(envelope, sys.stdout, indent=2)
        print(file=sys.stdout)
    else:
        report["summary"] = {
            "issue_count": sum(
                1 for f in envelope["findings"] if f["severity"] == "warn"
            ),
            "script_error_count": sum(
                1 for f in envelope["findings"] if f["severity"] == "block"
            ),
        }
        json.dump(report, sys.stdout, indent=2)
        print(file=sys.stdout)

    print(
        f"check_raster: status={envelope['status']} ({len(envelope['findings'])} finding(s)).",
        file=sys.stderr,
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
