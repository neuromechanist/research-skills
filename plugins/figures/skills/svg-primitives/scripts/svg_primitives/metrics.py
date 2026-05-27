"""Text-bbox measurement.

Strategy: fontTools advance-width tables first (platform-neutral, exact
em-relative measurements), Pillow `ImageFont.truetype` second (works when
fontTools can't open the file), heuristic last (logs a warning).

Width is the sum of glyph advances in font units divided by `unitsPerEm`
and multiplied by the em-mm size. Height is `(ascent - descent) /
unitsPerEm * em_mm` from the `hhea` table.

font_size is accepted in pt; mm conversion uses 1 pt = 25.4/72 mm.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

PT_PER_MM = 72.0 / 25.4
MM_PER_PT = 25.4 / 72.0

# Font search path: macOS first, then Linux/freedesktop, then user-local.
_FONT_SEARCH_DIRS: tuple[str, ...] = (
    "/System/Library/Fonts",
    "/System/Library/Fonts/Supplemental",
    "/Library/Fonts",
    str(Path.home() / "Library" / "Fonts"),
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    str(Path.home() / ".fonts"),
    str(Path.home() / ".local/share/fonts"),
)

# Filename stems we accept as "Helvetica or close" in priority order.
_FALLBACK_STEMS: tuple[str, ...] = (
    "Helvetica", "HelveticaNeue", "Arial", "ArialMT", "Arial Unicode",
    "LiberationSans", "DejaVuSans", "FreeSans", "NotoSans-Regular",
    "SegoeUI", "Roboto-Regular",
)


def _find_font_file() -> str | None:
    """Walk the search path, return the first file whose stem matches one
    of the fallback stems (case-insensitive, ignoring -Regular suffix)."""
    candidates_lower = [s.lower() for s in _FALLBACK_STEMS]
    for d in _FONT_SEARCH_DIRS:
        if not os.path.isdir(d):
            continue
        try:
            for fname in os.listdir(d):
                stem, ext = os.path.splitext(fname)
                if ext.lower() not in (".ttf", ".otf", ".ttc"):
                    continue
                stem_low = stem.lower().replace("-regular", "")
                if any(stem_low == c or stem_low.startswith(c) for c in candidates_lower):
                    return os.path.join(d, fname)
        except OSError:
            continue
    return None


def _measure_fonttools(text: str, font_size_pt: float, font_path: str) -> tuple[float, float] | None:
    """fontTools-based measurement. Returns (width_mm, height_mm) or None
    on failure (e.g. .ttc collection index issues, missing tables)."""
    try:
        from fontTools.ttLib import TTFont, TTLibError
    except ImportError:
        return None
    # .ttc font collections need a fontNumber; try 0 first, then probe.
    for font_number in (0, 1, 2, 3):
        try:
            tt = TTFont(font_path, fontNumber=font_number, lazy=True)
            break
        except (TTLibError, OSError, IndexError):
            continue
    else:
        log.debug(
            "fontTools could not open any collection index (0-3) in %s; "
            "falling back to next metric backend.", font_path,
        )
        return None
    try:
        cmap = tt.getBestCmap()
        if not cmap or "hmtx" not in tt or "head" not in tt:
            return None
        hmtx = tt["hmtx"]
        upem = tt["head"].unitsPerEm
        # advance for each char; missing chars fall back to space or 'M'
        space_glyph = cmap.get(ord(" "))
        fallback_glyph = space_glyph if space_glyph else cmap.get(ord("M"))
        total_units = 0
        for ch in text:
            glyph = cmap.get(ord(ch), fallback_glyph)
            if glyph and glyph in hmtx.metrics:
                total_units += hmtx.metrics[glyph][0]
        if total_units == 0:
            return None
        em_mm = font_size_pt * MM_PER_PT
        width_mm = (total_units / upem) * em_mm
        # height: use cap-height-ish (ascent - descent) for the line box
        if "hhea" in tt:
            hhea = tt["hhea"]
            height_units = hhea.ascent - hhea.descent
        else:
            height_units = upem
        height_mm = (height_units / upem) * em_mm
        # Visual text-bbox height is typically narrower than the full line
        # height; use 0.72 of the line box as a closer approximation of the
        # cap-height + descender that visual text occupies. This keeps box
        # auto-fit tight without clipping descenders.
        return (width_mm, height_mm * 0.72)
    finally:
        tt.close()


def _measure_pillow(text: str, font_size_pt: float, font_path: str | None) -> tuple[float, float] | None:
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    if font_path is None:
        return None
    MEASURE_PX = 200
    # .ttc: try a few collection indices.
    for idx in (0, 1, 2, 3):
        try:
            font = ImageFont.truetype(font_path, size=MEASURE_PX, index=idx)
            break
        except (OSError, IOError):
            continue
    else:
        return None
    try:
        left, top, right, bottom = font.getbbox(text)
    except (OSError, IOError, ValueError) as e:
        log.debug("Pillow getbbox failed on %s: %s", font_path, e)
        return None
    width_px = right - left
    height_px = bottom - top
    if width_px <= 0 or height_px <= 0:
        return None
    height_mm = font_size_pt * MM_PER_PT
    scale = height_mm / height_px
    return (width_px * scale, height_mm)


class MetricsFallbackError(RuntimeError):
    """Raised when `strict=True` and no exact font metric backend succeeded."""


def _measure_heuristic(text: str, font_size_pt: float) -> tuple[float, float]:
    """Last resort when no font metrics are available."""
    log.warning(
        "svg_primitives.metrics: no usable font found in search path; "
        "falling back to heuristic measurement (0.55 em per character). "
        "Text bbox may be off by up to ~20%%; install a system font (e.g. "
        "`apt-get install fonts-liberation` on Linux), pass an explicit "
        "font_path to LabeledBox, or set strict=True to raise instead."
    )
    em_mm = font_size_pt * MM_PER_PT
    return (0.55 * em_mm * max(1, len(text)), em_mm)


def measure_text_mm(
    text: str,
    font_size_pt: float,
    font_path: str | None = None,
    strict: bool = False,
) -> tuple[float, float]:
    """Return (width_mm, height_mm) for `text` rendered at `font_size_pt`.

    `font_path` is optional; if omitted, the search path is consulted for
    Helvetica → Arial → Liberation Sans → DejaVu Sans → first available.

    Tries fontTools, then Pillow, then a heuristic. If `strict=True`, raises
    `MetricsFallbackError` rather than using the heuristic — recommended for
    CI and journal-submission workflows where 20% measurement error in box
    sizing is unacceptable.
    """
    if not text:
        return (0.0, 0.0)
    if font_path is None:
        font_path = _find_font_file()
    if font_path:
        r = _measure_fonttools(text, font_size_pt, font_path)
        if r is not None:
            return r
        r = _measure_pillow(text, font_size_pt, font_path)
        if r is not None:
            return r
    if strict:
        raise MetricsFallbackError(
            f"No exact font metric backend succeeded for text {text!r} at "
            f"{font_size_pt} pt (font_path={font_path!r}). Install a system "
            "font or pass an explicit font_path to use exact metrics."
        )
    return _measure_heuristic(text, font_size_pt)


def measure_lines_mm(
    lines: list[str],
    font_size_pt: float,
    line_spacing: float = 1.2,
    font_path: str | None = None,
    strict: bool = False,
) -> tuple[float, float]:
    """Measure a multi-line block. Width is the widest line; height is the
    block height including line spacing."""
    if not lines:
        return (0.0, 0.0)
    widths_heights = [measure_text_mm(ln, font_size_pt, font_path, strict) for ln in lines]
    max_w = max((w for w, _ in widths_heights), default=0.0)
    single_h = widths_heights[0][1] if widths_heights else 0.0
    block_h = single_h * line_spacing * (len(lines) - 1) + single_h
    return (max_w, block_h)
