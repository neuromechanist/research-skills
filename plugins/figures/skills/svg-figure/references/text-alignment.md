# Text Alignment

> The bbox arithmetic for hand-authored SVG labels. `[[svg-primitives]]`'s `LabeledBox` auto-fits text via measured font metrics and centers automatically — read this document when authoring SVG by hand or when debugging a text-overflow finding from `figure-qa` or `Canvas.validate()`.

How to place SVG `<text>` so it sits inside its container shape, with the right anchor and baseline. The `figure-qa` SVG branch's geometry section will check text-bbox-inside-shape when issue #47 lands; for now these patterns prevent the failures by construction and the agent falls back to VLM judgment.

## Anchor and baseline at a glance

SVG text positioning is specified by three things:

1. **`x, y`** — the position of the text's *anchor point*.
2. **`text-anchor`** — which point on the text's horizontal extent is the anchor: `start` (left edge; default), `middle` (center), or `end` (right edge).
3. **`dominant-baseline`** — which horizontal line through the text the y coordinate lands on: `auto` (the alphabetic baseline, default), `middle` (the math-style midline), `central` (similar but Unicode-aware), `hanging` (the top of x-height), `text-bottom` (bottom of the descender), etc.

The defaults (`text-anchor="start" dominant-baseline="auto"`) place the text such that the **bottom-left of the baseline** is at `x, y`. This is rarely what you want for box labels.

## Centered-in-box pattern (most common)

```svg
<rect x="10" y="10" width="30" height="14" fill="#F4F1DE" stroke="#1F3A5F" stroke-width="0.8" rx="1.5"/>
<text x="25" y="17" text-anchor="middle" dominant-baseline="middle"
      font-family="Helvetica, Arial, sans-serif" font-size="6">Cortex</text>
```

- `x = rect.x + rect.width / 2 = 25`
- `y = rect.y + rect.height / 2 = 17`
- `text-anchor="middle"` centers horizontally on x.
- `dominant-baseline="middle"` centers vertically on y.

This works in Inkscape, Chrome, Firefox, Safari, librsvg, and cairosvg. It does **not** work the same way in WeasyPrint, which treats `dominant-baseline="middle"` as `auto` for some versions — if WeasyPrint is in your toolchain, fall back to `dy` math (see "Manual offset" below).

## Top-aligned title pattern

For a title at the top of the figure (above all shapes):

```svg
<text x="40" y="6" text-anchor="middle" dominant-baseline="hanging"
      font-family="Helvetica, Arial, sans-serif" font-weight="bold" font-size="8">
  Cortical recording chain
</text>
```

`dominant-baseline="hanging"` puts the text's top edge at `y=6`, so the title hangs below that line. With `font-size="8"`, the text descends to about `y=14`.

## Left-aligned legend text

For a legend or caption-style annotation aligned to a known column:

```svg
<text x="10" y="50" text-anchor="start" dominant-baseline="auto"
      font-family="Helvetica, Arial, sans-serif" font-size="5">
  EEG = electroencephalography
</text>
```

Defaults are usually fine here — `start` and `auto` place the baseline-bottom-left at `(10, 50)`. The text descends to about `y=51.5` (descenders) and rises to about `y=46` (cap height).

## Multi-line text

SVG has no native text wrapping. For multi-line labels, use `<tspan>` children with explicit `dy` for each new line:

```svg
<text x="25" y="14" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="6">
  <tspan x="25" dy="0">Primary motor</tspan>
  <tspan x="25" dy="7">cortex</tspan>
</text>
```

`dy="7"` advances the second line by 7 user units (mm) below the first. For tight line spacing use ~1.2 × font-size; for legible body text use 1.4 ×. Repeat `x="25"` on each `<tspan>` so a previous line's `text-anchor` doesn't carry over wrong width into the next line's positioning.

The `figure-qa` `validate_fonts.py` correctly handles `<tspan>` font-size — including this case, where the parent `<text>` has no `font-size` but each `<tspan>` does.

## Manual offset pattern (for WeasyPrint compatibility)

When `dominant-baseline="middle"` is unreliable, compute the offset manually:

```svg
<!-- Approximate: y_center + cap_height/2 - descender/2 ≈ y_center + 0.3*font_size -->
<text x="25" y="17" dy="0.3em" text-anchor="middle"
      font-family="Helvetica, Arial, sans-serif" font-size="6">Cortex</text>
```

`dy="0.3em"` shifts the baseline-anchored text down by 30% of the current font size, which approximates vertical centering. The result isn't pixel-perfect across fonts but is universally renderable.

## Common failure modes

| Failure | Cause | Fix |
|---|---|---|
| Text appears far below the box | `dominant-baseline="auto"` (default) treats y as the baseline | Set `dominant-baseline="middle"` or compute `y = box_center + 0.3*font_size` |
| Text is left-justified inside a centered box | `text-anchor="start"` (default) | Set `text-anchor="middle"` and `x = box_center_x` |
| Text extends past the right edge of the box | Text width > box width at the chosen font-size | Reduce font-size or break into two `<tspan>` lines |
| Descender (g, p, y) drops below the box | `dominant-baseline="middle"` excludes descenders from the centering math | Add 0.5–1 mm to y, or use `dominant-baseline="central"` |
| Cyrillic / CJK text misaligned | `Helvetica, Arial` fall-back to a different metric font | Specify a font family that includes the script (`Noto Sans CJK`, `Source Han Sans`) and verify with `[[figure-qa]]` raster branch (rasterize then OCR-check) |
| `<tspan>` with `dy` accumulates incorrectly across lines | A later `<tspan>` inherits the previous line's x (from text-anchor positioning), not the parent's x | Repeat `x="<column>"` on every `<tspan>` |
| `figure-qa` reports the text font-size as "skipped" | The `<text>` element has no `font-size` and no descendant `<tspan>` does either; font-size is inherited from a `<style>` block | Set `font-size` directly on each `<text>` or `<tspan>` |

## Bbox arithmetic for figure-qa geometry checks

The bbox-inside-shape check is tracked in issue #47. When it ships, it will compute:

- The text element's bbox via `svgelements.Text(...).bbox()`, which returns `(xmin, ymin, xmax, ymax)`.
- The containing shape's bbox the same way.
- Pass iff `text.xmin >= shape.xmin and text.xmax <= shape.xmax and text.ymin >= shape.ymin and text.ymax <= shape.ymax`.

Author with this in mind: aim for at least 1 mm clearance on every side. The exact clearance depends on font metrics, so verify with QA before submission rather than measuring in your head.
