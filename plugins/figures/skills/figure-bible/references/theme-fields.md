# theme.json field reference

Full schema: `plugins/figures/schemas/theme.schema.json` (draft-07).
Loaded and validated through `plugins/figures/lib/theme.py`.
Required keys are `theme_id`, `palette`, `style_tokens`; everything else is optional and defaults are filled in by `init_theme.py`.

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `theme_id` | string | derived from `--out` stem | Must match `^[a-z0-9][a-z0-9_-]*$`. |
| `journal` | enum | set by `--journal` | `nature`, `science`, `cell`, `pnas`, `poster`, `slide`, `custom`. |
| `palette.primary` | hex | preset color 1 | Main brand/data color. |
| `palette.accent` | hex | preset color 2 | Secondary color, callouts. |
| `palette.neutral` | hex | preset color 3 | Backgrounds, muted elements. |
| `palette.background` | hex or `transparent` | `#FFFFFF` | Figure canvas color. |
| `palette.categorical` | hex array | full preset | Ordered colors for categorical series. |
| `palette.sequential` | hex array | none | Optional low-to-high scale. |
| `palette.diverging` | hex array | none | Optional two-sided scale. |
| `typography.family` | string | `Helvetica` | Font family cue passed to the image model and to SVG/plot styling. |
| `typography.min_pt` | number | journal profile minimum | 5 pt for journals, 18 pt for poster/slide. |
| `typography.panel_letter.weight` | `bold`\|`regular` | `bold` | Panel letter (a, b, c...) weight. |
| `typography.panel_letter.case` | `lower`\|`upper` | `lower` | Panel letter case. |
| `stroke.weight_px` | number | `4` | Line weight for icons/overlays. |
| `stroke.linejoin` | `miter`\|`round`\|`bevel` | `round` | |
| `stroke.linecap` | `butt`\|`round`\|`square` | `round` | |
| `style_tokens` | string array | `["flat vector", "minimal", "no shading"]` | Positive prompt fragments. |
| `negative_tokens` | string array | `["gradient", "3D", "shadow", "watermark"]` | Negative prompt fragments. |
| `composition.aspect` | string | `"4:3"` | e.g. `1:1`, `16:9`. |
| `composition.padding_pct` | number 0-50 | `8` | Margin around the subject. |
| `composition.perspective` | `orthographic`\|`isometric`\|`perspective` | `orthographic` | |
| `text.max_words_per_label` | integer | `4` | Word budget for a single on-image label. |
| `text.max_words_per_title` | integer | `8` | Word budget for a headline/title. |
| `text.headline_size_class` | `large`\|`medium` | `medium` | Relative size class for the largest on-image text. |
| `reference_images` | path array (max 16) | `[]` | Canonical images attached for style transfer. |
| `model_preferences.codex_model` | string | `gpt-5.6-luna` | Passed to the Codex CLI `image_gen` tool. |
| `model_preferences.codex_effort` | string | `xhigh` | Codex reasoning effort for prompt planning. |
| `model_preferences.image_quality` | string | `high` | Image generation quality parameter. |
| `model_preferences.icons` / `.figures` / `.poster_text` | string | none | Legacy per-use-case overrides, kept optional for themes written before the bible existed. |
| `postprocess.bg_removal` | `auto`\|`pillow`\|`rembg`\|`none` | `auto` | `auto` picks Pillow-threshold unless the theme calls for BiRefNet edge quality. |
| `postprocess.alpha_matting` | boolean | none | Passed through to `rembg` when `bg_removal` is `rembg`. |
| `postprocess.threshold` | integer 0-255 | none | Passed through to the Pillow-threshold method. |

## Validation

`validate_theme.py` (and `lib/theme.py`'s `validate_theme()`) checks, in order:

1. Required keys present.
2. Every hex value matches the CSS 3/4/6/8-digit pattern (or is `transparent` where allowed).
3. `journal` and `postprocess.bg_removal` are in their enums.
4. WCAG contrast ratio between `palette.background` and `palette.primary`; below 3.0 is a `warning:`-prefixed line, not a hard failure.

With `jsonschema` installed (`uv run --with jsonschema ...`), the full schema in `schemas/theme.schema.json` runs instead of the hand-written checks above; both report the same class of problems.
