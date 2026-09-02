---
name: figure-bible
description: Use this skill when the user asks to "make a figure bible", "set up a style bible", "create a figure theme", "make a theme for my figures", "set up a figure style", "palette for my paper figures", or wants a consistent figure style. Scaffolds and validates figures/theme.json; run before any figures skill generates images.
version: 0.1.0
---

# Figure Bible

Authors one `figures/theme.json` per project: the palette, typography, composition rules, and image-model preferences that every figure, icon, and plot should share.
This is step zero.
Run it before any generation skill produces output, not after.

## When to use

- Starting a new paper, grant, or poster and no `figures/theme.json` exists yet.
- The user wants a consistent look across many figures (same colors, same font cue, same AI model settings).
- A generation or QA skill reports palette drift (`check_svg.py`/`check_raster.py` finding `palette_off`) and the project has no bible to point them at.

Skip it for a single one-off figure with no reuse; the generation skill's own defaults are fine there.

## Scripts

Both scripts live in `scripts/` (relative to this skill's base directory) and import the plugin's shared `lib/theme.py` by resolving their own path, so they work from a plugin install or a checkout.

Scaffold a theme:

```bash
uv run python scripts/init_theme.py --journal nature --out figures/theme.json \
    --preset okabe-ito --font Helvetica \
    --style "flat vector, minimal" --negative "gradients,shadows"
```

`--journal` is required: `nature`, `science`, `cell`, `pnas`, `poster`, or `slide` (drives the default page width and minimum text size).
`--preset` picks a starting palette: `okabe-ito` (default, colorblind-safe 8-color set), `tol-bright`, `wong` (alias of okabe-ito), or `neuro-flat` (navy/terracotta/cream plus three accents).
Override individual roles with `--primary`, `--accent`, `--neutral` (hex).
Add reference images for style transfer with repeated `--reference img.png`.
Set the image-model defaults with `--codex-model` and `--codex-effort`.
Re-running with `--force` overwrites an existing file; without it, the script refuses to clobber a theme someone already tuned.

Validate a theme (CI, pre-commit, or before trusting an edited theme.json):

```bash
uv run --with jsonschema python scripts/validate_theme.py figures/theme.json
```

Add `--json` for a machine-readable `{"valid": bool, "problems": [...], "checked": [...]}`.
Exit 0 means valid.
Exit 1 prints the list of problems.
Exit 2 is a usage or IO error (file missing, not JSON).
`jsonschema` is optional; without `--with jsonschema`, validation falls back to a hand-written structural check covering the same required keys, hex format, and enums.

See `references/theme-fields.md` for the full field table (type, default, meaning) and `examples/nature-neuro.theme.json` for a complete worked theme.

## How other skills consume the theme

- **Generators** (`figures:ai-full-figure`, `figures:transparent-icons`, `figures:scientific-figure`, `figures:svg-primitives`, `figures:plot-styling`) read `palette`, `typography`, `style_tokens`/`negative_tokens`, `composition`, `text`, and `model_preferences` from the theme to build prompts and defaults consistently.
  Invoke them with the Skill tool by those names once the bible exists.
- **QA** (`figures:figure-qa`, and directly `check_svg.py`/`check_raster.py`) accepts `--palette figures/theme.json` in place of a preset name, so palette-compliance findings are checked against the project's own bible instead of a hardcoded allow-list.
- `plugins/figures/lib/theme.py` is the single implementation shared by all of the above: `load_theme`, `validate_theme`, `palette_hexes`, `theme_defaults`, `resolve_palette`, `JOURNAL_PROFILES`, `PALETTE_PRESETS`.

## The one-bible rule

A project keeps exactly one `figures/theme.json`, checked into version control alongside the figures it governs.
Do not scaffold a second theme for a second figure in the same paper; edit the existing one instead, then re-run `validate_theme.py`.
Multiple themes are appropriate only across genuinely separate projects (a paper and an unrelated poster), never within one.

## Additional resources

- `references/theme-fields.md`: full field table with types, defaults, and validation rules
- `examples/nature-neuro.theme.json`: a complete, valid theme for a Nature-format neuroscience paper
- `scripts/init_theme.py`: scaffold a new theme
- `scripts/validate_theme.py`: validate an existing theme
- `../../lib/theme.py`: shared implementation used by this skill, the generators, and figure-qa
- `../../schemas/theme.schema.json`: the draft-07 JSON Schema itself
