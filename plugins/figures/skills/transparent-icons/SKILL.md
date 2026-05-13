---
name: transparent-icons
description: This skill should be used when the user asks to "make an icon", "generate an icon", "create a scientific icon", "make a transparent icon", "make a minimal icon", "icon for a figure", "icon for a paper", or wants flat scientific icons (brain, neuron, DNA, EEG cap, etc.) in the Nature/Science journal style with transparent backgrounds. Generates PNG icons via the Codex CLI image_gen tool (preferred) or the OpenAI Images API (fallback), then applies transparency via a Pillow threshold by default or rembg + BiRefNet (opt-in, higher edge quality).
version: 0.1.0
---

# Transparent Icons

Generate flat scientific icons (Nature/Science journal style) with transparent backgrounds. Used as panel elements by the `[[scientific-figure]]` composer or as standalone graphics for posters, presentations, and grants.

## Backends

Two generation backends, auto-selected:

1. **Codex CLI `image_gen` tool** (preferred). Uses the local Codex authentication (`~/.codex/auth.json`). No `OPENAI_API_KEY` required. Internally uses gpt-image-2 (April 2026). Default when `codex` is on `$PATH` and authenticated.
2. **OpenAI Images API** (fallback). Calls `client.images.generate(model="gpt-image-2", ...)` directly. Requires `OPENAI_API_KEY` in environment or `.env`.

Why two backends: many researchers have a ChatGPT subscription and `codex login` but no separate API key. Auto-selection routes through Codex first to keep the no-API-key path working; explicit `--backend codex` or `--backend api` overrides.

## Transparency

`gpt-image-2` (April 2026) does **not** accept `background="transparent"` — both backends always generate opaque PNGs. Transparency is applied as a post-process. Two methods:

- **`threshold`** (default) — drop near-white pixels via Pillow. Fast, no extra deps. Works well for flat 2-color icons on a clean white background. Can leave fringes on anti-aliased edges and may erase highlights where the foreground itself is near-white.
- **`birefnet`** (opt-in) — `rembg` + BiRefNet ONNX model with alpha matting. Cleaner edges, handles complex foregrounds. One-time ~400 MB model download on first run; requires extra deps (`rembg`, `onnxruntime`).

Pick `threshold` for the canonical flat-icon use case. Pick `birefnet` when the icon contains light-colored content (white parts of a brain MRI, light reflections on glass) that the threshold method would erase, or when the icon will be composited at large sizes where fringes are visible.

## Usage

Free-form prompt:

```bash
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py \
    "a human brain with EEG electrodes" -o brain_eeg.png --transparent
```

From the icon bible (curated templates with palettes, descriptions, and prompt hints):

```bash
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py \
    --template brain-eeg -o brain_eeg.png --transparent
```

With BiRefNet transparency (higher edge quality, extra deps):

```bash
uv run --with openai --with python-dotenv --with pillow --with rembg --with onnxruntime \
    python scripts/generate_icon.py --template neuron -o neuron.png \
    --transparent --transparency-method birefnet
```

List templates:

```bash
uv run --with python-dotenv python scripts/generate_icon.py --list-templates
```

Force a specific backend:

```bash
... --backend codex   # or --backend api
```

## Theme bible: keep an icon set consistent

When generating multiple icons that need to look like they belong together (same line weight, same color palette, same perspective), use a `theme.json` file. The schema is in `references/theme.schema.json` and is shared with the `[[ai-full-figure]]` skill (Phase 6). At a minimum:

```json
{
  "theme_id": "neuro-flat-v1",
  "palette": {"primary": "#1F3A5F", "accent": "#E07A5F", "neutral": "#F4F1DE", "bg": "transparent"},
  "stroke": {"weight_px": 4, "linejoin": "round"},
  "style_tokens": ["flat 2D", "single continuous line", "no shading", "centered"],
  "negative_tokens": ["text", "labels", "watermark", "gradient", "3D", "shadow"],
  "composition": {"aspect": "1:1", "padding_pct": 12, "perspective": "orthographic"}
}
```

`examples/icon_set.py` demonstrates loading a theme and generating an icon set with consistent prompts.

## When to use this skill vs the icon bible

- **Bible templates** (`--template <id>`) are curated for common research subjects (brain, neuron, EEG cap, DNA, microscope, etc.) and produce predictable output. Use them first.
- **Free-form prompts** are right when the subject is not in the bible or needs a specific composition not captured by a template.
- **`--category`** generates every template in a category at once; useful for stocking a project's icon directory.

See `references/icon-bible.md` for the template schema and `references/prompt-patterns.md` for what works and what to avoid in prompts.

## Quality assurance

Phase 4 of epic #31 introduces the `figure-qa` agent that proactively runs on generated icons to check for transparency correctness, palette compliance, and the absence of stray label text. Until then, inspect each icon visually before incorporating it into a figure.

## Additional resources

- `references/icon-bible.md` — icon template schema and category catalog
- `references/prompt-patterns.md` — model-specific prompt patterns and failure modes
- `references/theme.schema.json` — JSON schema for the theme bible (shared with ai-full-figure)
- `scripts/generate_icon.py` — CLI entry point with auto backend selection
- `scripts/icon-templates.json` — bible templates loaded by `--template` / `--category`
- `examples/icon_set.py` — generate a 3-icon set with a shared theme
