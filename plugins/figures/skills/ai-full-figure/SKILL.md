---
name: ai-full-figure
description: Use this skill when the user asks to "generate an AI figure", "make an AI-generated figure", "make a poster figure", "make a presentation figure", "generate a figure with AI", "generate figure panels with Codex", "make a multi-panel AI figure", "AI background for a figure", or wants a pictorial figure or panel (brain scene, apparatus, anatomy, pipeline illustration) rendered by gpt-image-2 through the Codex CLI with large verbatim titles and panel letters, then QA'd and iterated until it passes. Expects a theme from figures:figure-bible. Data plots, axes, numerals, and equations go to figures:plot-styling or figures:svg-primitives instead.
version: 0.2.0
---

# AI Full Figure

Generate single panels or whole multi-panel figures with the image model (gpt-image-2 through the Codex CLI, or the OpenAI Images API when a key exists),
with the titles, panel letters, and short labels rendered by the model at large size,
then run `figures:figure-qa` and iterate until the figure ships.
The output is an opaque PNG per panel plus a composed SVG, PDF, and PNG when more than one panel is built.

Sister skills are invoked with the Skill tool by their `figures:` names.

## The workflow

1. **Bible first.** A project keeps one `figures/theme.json`.
   If it does not exist, invoke `figures:figure-bible` before generating anything.
   The theme supplies the palette, typography, style and negative tokens, the text limits, and the Codex model settings.
2. **Generate.** One panel with `generate_figure.py`, or a whole figure with `build_figure.py` and a spec file.
   Text that the model should render is passed as verbatim items with a role and a placement.
3. **QA.** Invoke `figures:figure-qa` on every candidate, passing the expected verbatim strings, the theme path, and the journal.
   The report ends with a JSON block whose `status` and `findings[].action` drive the next step.
4. **Iterate.** Follow the iterate-loop reference shipped with `figures:figure-qa` (`iterate-loop.md`): N candidates in parallel, QA in one parallel dispatch, pick the best, apply one targeted change, re-QA, stop at `ship` or after three iterations.

## When to use this skill

Reach for `ai-full-figure` when the figure's picture is the point: a headset on a head, a microscope, an anatomical scene, a schematic scene for a poster or a talk, or a graphical-abstract panel.

Route elsewhere when the figure is information-dense:

| Figure type | Skill |
|---|---|
| Data plot with axes and numerals | `figures:plot-styling`, then `figures:scientific-figure` to compose |
| Boxes, arrows, and process flow with many labels | `figures:svg-primitives` |
| Flat icon to drop into another figure | `figures:transparent-icons` |
| Composing panels that already exist | `figures:scientific-figure` |

## The text ladder

The model renders text well when the prompt is explicit, so text is placed by a ladder, not banned.

1. **Model-rendered text**: panel letters, titles, and short labels.
   Labels are capped at `theme.text.max_words_per_label` words (default 4) and titles at 8; titles and panel letters default to the theme headline size (large).
2. **SVG overlay** (`overlay_labels.py`): dense labels, leader-line annotations, scale bars, and any string that must stay editable.
3. **Vector or plot skills**: numerals with units, equations, axis ticks, and anything the reader must read exactly.

The generator refuses items that break the ladder and says which rung they belong to.
Details and prompt patterns live in `references/prompt-patterns.md`.

## Prerequisites

- Codex CLI logged in (`codex login status`), no API key needed.
  The backend runs a 10 second preflight; if `codex --version` hangs, the error message gives the two remedies (approve the binary once from Terminal.app, or copy `codex` and `codex-code-mode-host` to a folder you own, run `xattr -c` on both, and set `CODEX_BIN`).
  Never disable the Codex code-mode host: `image_gen` is only reachable through it.
- Or `OPENAI_API_KEY` for the API path (`--backend api`).
- `uv` for Python, with `--with pillow` for the generators; `--with svgutils --with cairosvg` for composition.

Model defaults come from the theme's `model_preferences`: `gpt-5.6-luna` at `xhigh` effort with image quality `high`, which lands good figures at the cheapest tier.
Expect one to three minutes per image; panels run in parallel.

## Usage

### One panel or a whole figure in one image

```bash
uv run --with pillow python scripts/generate_figure.py \
    "a simplified EEG headset drawn as a head silhouette in profile with four electrodes" \
    --out figures/fig1/panel_a.png --theme figures/theme.json --size 1024x1024 \
    --text "panel-letter:top-left:a" --text "title:bottom-center:EEG recording"
```

Flags: `--size` is `auto` or `WIDTHxHEIGHT` (edges in multiples of 16, up to 3840 px, aspect up to 3:1);
`--quality low|medium|high|auto`; `--background opaque|transparent`; `--n` candidates;
`--ref image.png` (repeatable) for style or consistency conditioning; `--backend auto|codex|api|fake`;
`--model` and `--effort` override the theme; `--print-prompt` shows the prompt; `--verbose` prints a heartbeat.
A generation log is written next to the output as `<out>.codex.log`.
Exit codes: 0 success, 1 generation failure, 2 usage or text-ladder error.

Targeted edit of an existing candidate (used by the iterate loop):

```bash
uv run --with pillow python scripts/generate_figure.py --edit figures/fig1/panel_a.png \
    "recolor the electrode dots to #E07A5F and keep everything else unchanged" \
    --out figures/fig1/panel_a_v2.png --theme figures/theme.json
```

### Multi-panel figure from a spec

```json
{
  "theme": "figures/theme.json",
  "layout": "panels",
  "size": "1024x1024",
  "quality": "high",
  "consistency": "first-panel",
  "parallel": 3,
  "panels": [
    {"id": "a", "subject": "EEG headset on a head silhouette in profile",
     "text": [{"role": "panel-letter", "text": "a", "placement": "top-left"},
              {"role": "title", "text": "EEG recording", "placement": "bottom-center"}]},
    {"id": "b", "subject": "three-column neural network, output column in the accent colour",
     "text": [{"role": "panel-letter", "text": "b", "placement": "top-left"},
              {"role": "title", "text": "Foundation model", "placement": "bottom-center"}]}
  ],
  "compose": {"journal": "nature", "width": "double", "columns": 2, "gap_mm": 3}
}
```

```bash
uv run --with pillow --with svgutils --with cairosvg python scripts/build_figure.py \
    --spec figures/fig1/figure.json --out figures/fig1/
```

`layout: panels` generates the first panel alone, then the rest in parallel with the first panel attached as a reference so the style stays consistent, composes them at the journal width with `figures:scientific-figure`'s composer, and exports `figure.svg`, `figure.png`, and `figure.pdf`.
`layout: single` renders the whole grid in one image, which suits posters and slides.
`manifest.json` records every prompt, path, and timing, plus the exact `check_raster.py` commands for QA.

### Overlay for dense labels

```bash
uv run --with pillow python scripts/overlay_labels.py figures/fig1/panel_a.png \
    --labels-file labels.json --width-mm 89 --journal nature --check --grid \
    -o figures/fig1/panel_a_labeled.svg
```

`--grid` writes a coordinate grid image to read label positions from; `--check` validates the physical point size before you continue.
Recipes are in `references/overlay-recipes.md`.

## Quality assurance and iteration

Invoke `figures:figure-qa` with the Skill tool after every generation unless the user passed `no-qa`.
Give it the figure path, the journal, the theme path, and every verbatim string that was requested, so the raster text check runs.
Run one QA dispatch per candidate in a single message so they execute in parallel on the Sonnet tier, then follow the figure-qa skill's `iterate-loop.md` for ranking, the one-change rule, and the stopping conditions.

## Cross-agent notes

Codex and Copilot CLI run the same scripts; the QA procedure runs inline per candidate instead of as parallel subagents.
The fake backend (`--backend fake` or `FIGURES_IMAGE_BACKEND=fake`) renders placeholder PNGs with the requested text, for tests and dry runs.

## Additional resources

- `references/prompt-patterns.md`: the text ladder, prompt structure, style and negative tokens, reference conditioning, failure modes
- `references/overlay-recipes.md`: label, arrow, and scale-bar overlay with correct units
- `scripts/generate_figure.py`: single generation and targeted edits
- `scripts/build_figure.py`: multi-panel orchestrator and composer
- `scripts/overlay_labels.py`: SVG overlay with `--grid` and `--check`
- `examples/poster_substrate.py`: end-to-end demo ending in a composed figure
- Shared code: `../../lib/image_backend.py`, `../../lib/prompting.py`, `../../lib/theme.py`; schema at `../../schemas/theme.schema.json`
