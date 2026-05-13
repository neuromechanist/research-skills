"""Programmatic raster (PNG/JPG/TIFF) checks for figure-qa.

Detects:
- Alpha-channel correctness (does the file claim transparency? are the corners
  actually transparent?)
- Unintended white background (file lacks RGBA, but corners are pure white)
- Resolution and DPI vs the journal target
- Dominant colors vs an allow-list (via colorthief if available)

Run from anywhere:

    uv run --with pillow [--with colorthief] python check_raster.py FIGURE.png \\
        [--journal nature] [--expect-transparent]

Emits a single JSON document on stdout. Exit 0 clean, 1 issues, 2 IO/parse error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


JOURNAL_MIN_DPI: dict[str, int] = {
    "nature": 300,    # 300 DPI halftone; 600 DPI line art
    "science": 300,   # 300 DPI halftone; 1200 DPI line art
    "cell": 300,
    "pnas": 300,
    "generic": 300,
}


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
        return {"applicable": False, "reason": "image has alpha channel; use alpha_report instead"}
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


def _palette_report(image_path: Path) -> dict[str, Any]:
    """Use colorthief (when installed) to extract the dominant colors. This is
    informational only — the section reports the observed palette so the agent
    can pass it through VLM judgment. Colorthief failures are surfaced as
    'script_error' so the caller can decide whether to fail the run."""
    try:
        from colorthief import ColorThief  # type: ignore[import-not-found]
    except ImportError:
        return {"available": False, "reason": "colorthief not installed; pass --with colorthief"}
    try:
        ct = ColorThief(str(image_path))
        dominant = ct.get_color(quality=10)
        palette = ct.get_palette(color_count=6, quality=10)
    except Exception as exc:
        return {
            "available": True,
            "script_error": True,
            "error": f"colorthief failed: {exc}",
        }
    return {
        "available": True,
        "dominant_rgb": list(dominant),
        "palette_rgb": [list(c) for c in palette],
    }


def check_raster(
    image_path: Path,
    journal: str | None,
    expect_transparent: bool,
) -> dict[str, Any]:
    img = _open(image_path)
    return {
        "input": str(image_path),
        "checks": {
            "alpha": _alpha_report(img, expect_transparent),
            "white_background": _white_background_report(img, expect_transparent),
            "resolution": _resolution_report(img, journal),
            "palette": _palette_report(image_path),
        },
    }


def _summarize(report: dict[str, Any]) -> tuple[int, int]:
    """Return (issue_count, script_error_count). Script errors signal that a
    section's check itself failed (e.g., colorthief crashed); they propagate
    to exit code 2 in main()."""
    issues = 0
    script_errors = 0
    for section in report.get("checks", {}).values():
        if not isinstance(section, dict):
            continue
        if section.get("issue"):
            issues += 1
        if section.get("script_error"):
            script_errors += 1
    return issues, script_errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Programmatic raster checks for figure-qa.")
    parser.add_argument("image", type=Path, help="Raster image to inspect (.png, .jpg, .tif)")
    parser.add_argument(
        "--journal",
        choices=["nature", "science", "cell", "pnas", "generic"],
        help="Target journal (sets DPI minimum).",
    )
    parser.add_argument(
        "--expect-transparent",
        action="store_true",
        help="Caller asserts the image should have a transparent background; corners flagged if not.",
    )
    args = parser.parse_args(argv)

    if not args.image.exists():
        print(f"error: image not found: {args.image}", file=sys.stderr)
        return 2
    try:
        report = check_raster(args.image, args.journal, args.expect_transparent)
    except ImportError as exc:
        print(
            f"error: missing dependency for check_raster.py — re-run with "
            f"--with pillow [--with colorthief]: {exc}",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:
        # Pillow raises UnidentifiedImageError or OSError on corrupt/truncated images;
        # name the exception so the user can self-diagnose.
        print(
            f"error ({type(exc).__name__}): could not analyze '{args.image}': {exc}",
            file=sys.stderr,
        )
        return 2

    issues, script_errors = _summarize(report)
    report["summary"] = {"issue_count": issues, "script_error_count": script_errors}
    json.dump(report, sys.stdout, indent=2)
    print(file=sys.stdout)
    if script_errors:
        print(
            f"check_raster: {script_errors} section(s) failed to run; see report.",
            file=sys.stderr,
        )
        return 2
    if issues:
        print(f"check_raster: {issues} issue(s) detected.", file=sys.stderr)
        return 1
    print("check_raster: clean.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
