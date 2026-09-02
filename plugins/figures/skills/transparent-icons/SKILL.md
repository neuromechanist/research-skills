---
name: transparent-icons
description: Use this skill when the user asks to "make an icon", "generate an icon", "create a scientific icon", "make a transparent icon", "make a minimal icon", "icon for a figure", "icon for a paper", "generate an icon set", "batch icons", or wants flat scientific icons (brain, neuron, DNA, EEG cap, microscope) with transparent backgrounds in a journal style. Generates PNG icons with gpt-image-2 through the Codex CLI (or the OpenAI Images API), keeps the model's native alpha, and reads palette and model settings from the project theme made by figures:figure-bible.
version: 0.2.0
---

# Transparent Icons

Generate flat scientific icons with transparent backgrounds, styled by the project's `figures/theme.json`,
for use as panel elements in `figures:scientific-figure`, in `figures:svg-primitives` schematics, or on their own in posters, slides, and grants.
Sister skills are invoked with the Skill tool by their `figures:` names.

## Backends

Generation goes through the shared backend in `plugins/figures/lib/image_backend.py`, the same one `figures:ai-full-figure` uses.

1. **Codex CLI `image_gen`** (default when `codex` is logged in). No API key needed.
   The model and effort come from the theme's `model_preferences` (default `gpt-5.6-luna` at `xhigh`), which lands good icons at the cheapest tier in one to two minutes each.
2. **OpenAI Images API** (`--backend api`) with `OPENAI_API_KEY`.

The backend preflights Codex with a 10 second timeout and explains the fix when the binary hangs (approve it once from Terminal.app, or copy `codex` and `codex-code-mode-host` to a folder you own, `xattr -c` both, and set `CODEX_BIN`).
`--backend fake` renders placeholder icons for tests.

## Transparency

Icons are requested with a transparent background and the model's alpha channel is kept as is.
`--transparency-method auto` (default) runs no local processing when the PNG already has a clean cutout, so light strokes are never eaten by a second threshold pass.
If the returned image is opaque, `auto` falls back to `threshold` (Pillow near-white removal);
`birefnet` (opt-in, `--with rembg --with onnxruntime`) gives cleaner edges on complex foregrounds.

## Usage

Free-form subject with the project theme:

```bash
uv run --with pillow python scripts/generate_icon.py \
    "a human brain with EEG electrodes" --theme figures/theme.json -o icons/brain_eeg.png
```

From the icon bible (curated templates with prompt hints):

```bash
uv run --with pillow python scripts/generate_icon.py --template brain-eeg --theme figures/theme.json -o icons/brain_eeg.png
uv run --with pillow python scripts/generate_icon.py --list-templates
uv run --with pillow python scripts/generate_icon.py --category neuroscience --theme figures/theme.json -o icons/
```

Batch with a placeholder:

```bash
uv run --with pillow python scripts/generate_icon.py "a flat icon of a {item}" \
    --batch "neuron,synapse,electrode" --theme figures/theme.json -o icons/
```

Other flags: `--colors "teal,coral"` overrides the theme palette for one run; `--size 1024` (square);
`--backend auto|codex|api|fake`; `--codex-bin`; `--timeout`; `--verbose`; `--print-prompt`.
A log is written next to each output as `<out>.codex.log`.

## Theme bible

Icons should never be generated without a theme when they need to match other figures.
Invoke `figures:figure-bible` to scaffold and validate `figures/theme.json` (schema at `plugins/figures/schemas/theme.schema.json`).
The icon prompt uses `palette`, `stroke.weight_px`, `style_tokens`, `negative_tokens`, `composition`, and `model_preferences`.
`examples/icon_set.py` generates a small consistent set from one theme.

## Quality assurance

Invoke `figures:figure-qa` after generation unless the user passed `no-qa`.
Its raster branch checks the alpha channel and corners (`--expect-transparent`), palette compliance against the theme (`--palette figures/theme.json`), resolution, and dominant colours,
and the vision pass judges whether the icon reads as the intended concept, which is the most common miss.

## Additional resources

- `references/icon-bible.md`: template schema and category catalog
- `references/prompt-patterns.md`: prompt patterns and failure modes for icons
- `scripts/generate_icon.py`: CLI entry point
- `scripts/icon-templates.json`: bible templates loaded by `--template` and `--category`
- `examples/icon_set.py`: themed icon set (`--smoke` for a one-icon check)
- Shared code: `../../lib/image_backend.py`, `../../lib/prompting.py`, `../../lib/theme.py`
