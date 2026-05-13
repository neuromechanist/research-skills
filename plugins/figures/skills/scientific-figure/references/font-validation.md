# Font Validation

How `validate_fonts.py` checks every `<text>` element in a composed SVG against the target journal's font minimum.

## The problem

Journals reject figures where axis labels, legends, or annotations fall below their published minimum legible font size. Two common ways a figure produces sub-minimum text:

1. **Source plot was authored at a small font.** A matplotlib plot saved with `font.size: 7` is already at the threshold for Nature (5 pt min) and below Science/Cell/PNAS (6 pt min).
2. **Compose-time scaling.** A 10 pt font in a panel scaled by 0.5 becomes 5 pt. Most react-pdf / HTML composition pipelines do this scaling uniformly when content overflows, producing 3-4 pt text that the figure author never sees until journal proofing.

This skill prevents both by inspecting the composed SVG before export.

## Journal minimums

| Journal | Body min (pt) | Panel label min (pt) |
|---|---|---|
| Nature | 5 | 8 |
| Science | 6 | 8 |
| Cell | 6 | 8 |
| PNAS | 6 (no label below 2 mm tall) | 8 |

Source: each journal's current author instructions; see `references/journal-specs.md`.

The validator enforces the **body** minimum across all `<text>` elements (panel labels usually run 10-12 pt and trivially pass).

## How the validator works

1. **Parse the SVG** with `lxml.etree`.
2. **Walk every element** depth-first, accumulating a scale factor from each ancestor's `transform="..."`.
   - `scale(s)` and `scale(sx, sy)` are parsed directly.
   - `matrix(a b c d e f)` is decomposed; the x-axis scale is `sqrt(a^2 + b^2)` and y-axis is `sqrt(c^2 + d^2)`.
   - Translations and rotations do not affect font size.
3. **For each `<text>` element**, extract the specified font size from the `font-size` attribute or the `style="font-size: ..."` property. Recognized units:
   - `pt` (and unitless — matplotlib's SVG output is bare pt by default)
   - `px` (converted: 1 pt = 96/72 px)
   - `em` (treated as 12 pt parent — coarse heuristic, only relevant if the source SVG used em)
   - `%` (treated as `value/100 * 12 pt`)
4. **Compute effective pt** = specified_pt × min(scale_x, scale_y). The smaller axis governs legibility because text always has both width and height.
5. **Compare** to the journal minimum and emit a JSON report.

## Reading the report

```json
{
  "svg": "figure.svg",
  "journal": "nature",
  "minimum_pt": 5.0,
  "checked_count": 47,
  "issue_count": 2,
  "issues": [
    {
      "text": "Frequency (Hz)",
      "specified_pt": 9.0,
      "effective_pt": 4.5,
      "scale_x": 0.5,
      "scale_y": 0.5,
      "minimum_pt": 5.0,
      "tag_id": ""
    },
    {
      "text": "0",
      "specified_pt": 8.0,
      "effective_pt": 4.0,
      "scale_x": 0.5,
      "scale_y": 0.5,
      "minimum_pt": 5.0,
      "tag_id": ""
    }
  ]
}
```

`scale_x` / `scale_y` tell you the cumulative transform applied to that text — usually the panel scale.

## Remediation

When the validator reports issues:

1. **Increase the source plot's font size.** If the panel must stay at scale 0.5, bump the source matplotlib rcparam from 9 pt to 12 pt. Re-save the panel SVG, recompose, revalidate.
2. **Increase the panel scale.** If the source font is already a sensible 10 pt and the panel sits at 0.5, raise the panel scale and either shrink other panels or accept a larger total figure height.
3. **Move to a wider canvas.** If you started on a 1-column canvas (89 mm) but the content really needs 1.5- or 2-column width, switching to 183 mm typically lets every panel sit at scale 1.0.

The remedies are mutually exclusive in priority order: try source-font fix first because it propagates to every reuse of the same source.

## Limitations

- The validator does not enforce the panel-label minimum separately from body text. Panel labels are typically 12 pt bold and pass trivially; if you intentionally use a tiny label, add an explicit check.
- `font-size` set via CSS class selectors in a `<style>` element is not resolved. Matplotlib does not use class selectors by default; if a source SVG uses them, run it through `svgutils` first to inline the styles, or set font-size directly on each `<text>`.
- The percent-em conversion is heuristic. Avoid em/% font sizing in source plots.

## Why pt and not px

The composed SVG declares its physical size in mm (e.g., `width="183mm"`). When a renderer (Inkscape, cairosvg, a browser) lays out the SVG, font-size values are interpreted as user units inside the SVG's viewBox. For matplotlib-generated SVGs the `font-size` attribute is in pt by default, so a direct pt interpretation matches the actual rendered size on a page printed at the journal's specified mm width.

If you author SVGs by hand and use `font-size="12px"`, the validator converts to pt before comparison (12 px → 9 pt).
