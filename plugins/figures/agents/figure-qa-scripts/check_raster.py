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


def _white_background_report(img) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """For opaque images, sample corners to detect an unintended pure-white
    background. Many journals reject white-bordered raster figures unless the
    border was deliberate."""
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
    return {
        "applicable": True,
        "corner_pixels": [list(c) for c in corners],
        "pure_white_corner_count": pure_white,
        "note": (
            "all four corners pure-white suggests a likely-unintended white background; "
            "consider exporting with transparent=True or cropping."
            if pure_white == 4
            else "no all-white border detected."
        ),
    }


def _resolution_report(img, journal: str | None) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """Report image size in pixels and DPI vs the journal's minimum."""
    out: dict[str, Any] = {"size_px": list(img.size)}
    dpi = img.info.get("dpi")
    if dpi:
        out["dpi"] = list(dpi) if isinstance(dpi, tuple) else dpi
        min_dpi = JOURNAL_MIN_DPI.get((journal or "generic").lower(), 300)
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
    """Use colorthief (when installed) to extract the dominant colors. The
    agent compares these against an allow-list at synthesis time."""
    try:
        from colorthief import ColorThief  # type: ignore[import-not-found]
    except ImportError:
        return {"available": False, "reason": "colorthief not installed; pass --with colorthief"}
    try:
        ct = ColorThief(str(image_path))
        dominant = ct.get_color(quality=10)
        palette = ct.get_palette(color_count=6, quality=10)
    except Exception as exc:
        return {"available": True, "error": f"colorthief failed: {exc}"}
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
            "white_background": _white_background_report(img),
            "resolution": _resolution_report(img, journal),
            "palette": _palette_report(image_path),
        },
    }


def _summarize(report: dict[str, Any]) -> int:
    issues = 0
    for section in report.get("checks", {}).values():
        if isinstance(section, dict) and section.get("issue"):
            issues += 1
    return issues


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
    except Exception as exc:
        print(f"error: could not analyze '{args.image}': {exc}", file=sys.stderr)
        return 2

    issues = _summarize(report)
    report["summary"] = {"issue_count": issues}
    json.dump(report, sys.stdout, indent=2)
    print(file=sys.stdout)
    if issues:
        print(f"check_raster: {issues} issue(s) detected.", file=sys.stderr)
        return 1
    print("check_raster: clean.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
