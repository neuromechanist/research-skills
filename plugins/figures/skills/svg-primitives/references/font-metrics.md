# Font metrics in svg-primitives

The `LabeledBox` auto-fit logic needs to know how wide a string will render at a given font size **before** the SVG is parsed by a renderer. This document explains how that measurement is computed and how the fallback chain behaves.

## Measurement strategy

Implemented in `scripts/svg_primitives/metrics.py`. Three tiers, in order:

1. **fontTools** (primary).
2. **Pillow `ImageFont.truetype`** (fallback when fontTools can't open the file — rare `.ttc` collection-index issues).
3. **Heuristic** (last resort): `width ≈ 0.55 em × len(text)`. Logs a single `logging.warning` so the user notices.

## fontTools measurement

Given a font file:

```python
tt = TTFont(font_path, fontNumber=0, lazy=True)
cmap = tt.getBestCmap()                      # ord(c) -> glyphName
hmtx = tt["hmtx"]                            # glyphName -> (advanceWidth, lsb)
upem = tt["head"].unitsPerEm                 # em size in font units

advance_units = sum(hmtx[cmap[ord(c)]][0] for c in text)
em_mm = font_size_pt * (25.4 / 72)           # 1 pt = 25.4/72 mm
width_mm = (advance_units / upem) * em_mm

ascent = tt["hhea"].ascent
descent = tt["hhea"].descent                 # negative
line_height_units = ascent - descent
line_height_mm = (line_height_units / upem) * em_mm
```

The visual text bbox is tighter than the line box. We scale the line height by **0.72** to approximate the cap-height + descender extent that visual text actually occupies — this keeps `LabeledBox` auto-fit tight without clipping descenders.

## Font search path

When `font_path` is not supplied to `LabeledBox` or `measure_text_mm`, the metrics module searches:

1. `/System/Library/Fonts` (macOS)
2. `/System/Library/Fonts/Supplemental` (macOS)
3. `/Library/Fonts` (macOS)
4. `~/Library/Fonts` (macOS)
5. `/usr/share/fonts` (Linux)
6. `/usr/local/share/fonts` (Linux)
7. `~/.fonts` (legacy Linux)
8. `~/.local/share/fonts` (freedesktop)

Accepted file extensions: `.ttf`, `.otf`, `.ttc`.

Filename stems searched (in priority order):

1. Helvetica
2. HelveticaNeue
3. Arial / ArialMT / Arial Unicode
4. Liberation Sans
5. DejaVu Sans
6. Free Sans
7. Noto Sans (Regular)
8. Segoe UI
9. Roboto Regular

The first match wins. If none are found, the heuristic kicks in.

## .ttc handling

TrueType Collections (`.ttc`) contain multiple fonts (e.g. `Helvetica.ttc` ships Regular, Bold, Light, Oblique, etc. under one file). fontTools requires a `fontNumber` index. The metrics module probes 0, 1, 2, 3 until one opens cleanly. Pillow gets the same treatment in the fallback path.

If you need a specific weight (e.g. you want metrics for the Bold face), pass the explicit font file path:

```python
LabeledBox(x=10, y=10, text="bold label",
           font_path="/System/Library/Fonts/Helvetica.ttc")
```

Currently the metrics module always uses index 0 (Regular) for `.ttc` files. Hooking up a `font_weight` parameter that maps to the right index is a follow-up if it comes up.

## Why not just use Pillow?

The Phase 0 prototype used Pillow only. Two problems:

1. Pillow ImageFont requires a font file; on Linux containers without a system font installed, this fails entirely. fontTools works on any TTF/OTF file the user can name.
2. Pillow measurement is rasterizer-based: it renders at a chosen px size and reads the pixel bbox. That's a ~10x slowdown vs reading advance-width tables directly. For figures with hundreds of labeled elements, the savings add up.

The Pillow path remains as a fallback for fonts that fontTools can't open (rare).

## Verifying the metrics

The E2E tests render boxes at multiple font sizes and label lengths, then assert text containment against the rendered SVG. If a metrics regression makes labels overflow, the relevant test (`test_text_inside_box_for_all_examples` or `test_no_text_overflow_extreme`) fails.

A quick sanity check from a Python REPL:

```python
from svg_primitives.metrics import measure_text_mm
print(measure_text_mm("Hello", font_size_pt=7))
# expected ~ (5.5 mm, 1.78 mm) for Helvetica
```
