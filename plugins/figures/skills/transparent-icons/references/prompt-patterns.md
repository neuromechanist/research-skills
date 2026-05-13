# Creating Icon Elements for Scientific Figures

Generate flat, minimalist scientific icons in the style of Nature, Science, and Cell journal figures using OpenAI's gpt-image-2 model.

## Backends

`scripts/generate_icon.py` auto-selects one of two backends:

1. **codex** (preferred): invokes the local Codex CLI's platform-native `image_gen` tool inside a temp workspace, then returns the saved PNG. Works with a ChatGPT subscription or API-key login (`codex login`); no `OPENAI_API_KEY` is required.
2. **api**: calls `client.images.generate(model="gpt-image-2", ...)` against the OpenAI API. Requires `OPENAI_API_KEY`.

Auto rule: codex is used when both the `codex` binary is on PATH and `~/.codex/auth.json` (or `CODEX_HOME/auth.json`) exists; otherwise the API path is used. Override with `--backend codex` or `--backend api`.

## When to Use Icons

Icons serve as visual shorthand in multi-panel figures, graphical abstracts, and workflow diagrams. They represent concepts (brain, neuron, sensor, patient) without photographic detail.

## Visual Characteristics

- Flat design: no gradients, shadows, or 3D effects
- Minimalist: simple geometric shapes, reduced detail
- Limited palette: 2-4 colors per icon, from the figure's shared palette
- Consistent stroke weight throughout
- Clean, sharp edges
- Square canvas: 1024x1024 px default
- Transparent background (PNG) for compositing

## Generation Approaches

### Template-based (preferred for consistency)

Predefined templates in `icon-templates.json` define elements, shapes, colors, and spatial relationships. Schema documented in `icon-bible.md`.

```bash
# Generate from template
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template brain-eeg -o elements/brain.png --transparent

# Override colors
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template neuron --colors "#0072B2,#D55E00" -o elements/neuron.png

# Generate all icons in a category
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --category neuroscience -o elements/

# List available templates
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --list-templates
```

### Free-form generation

For one-off icons not in the template catalog:

```bash
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py "a human brain with EEG electrodes" -o elements/brain.png --transparent

# With specific colors
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py "a neuron" -o elements/neuron.png --colors "teal,white" --transparent

# Batch generation
uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py "a flat icon of a {item}" -o elements/ --batch "brain,heart,lung"
```

## Prompt Engineering

### Base prompt template
```
A flat, minimalist scientific icon of [SUBJECT], in the style of Nature/Science journal figures.
Simple geometric shapes, [COLOR_PALETTE], no gradients, no shadows, no 3D effects,
no text, no labels, clean edges, centered on transparent background.
```

### Effective modifiers
- "pictogram style" -- more abstract, symbolic
- "infographic icon" -- slightly more detail, good for graphical abstracts
- "schematic" -- technical, engineering-oriented
- "silhouette" -- single-color, maximum simplicity
- "line art" -- outline only, no fill

### Pitfalls to avoid
- Never use "realistic" or "photorealistic"
- Never use "detailed" or "complex"; prefer "simple" and "minimalist"
- Never request text within the icon (add labels in the composition step)
- Avoid multiple disconnected elements per icon

## Refinement

Common adjustments after generation:
- Too detailed: add "extremely minimalist, simple geometric shapes"
- Wrong colors: specify exact hex codes
- Bad proportions: add "centered, symmetrical, well-proportioned"
- Unwanted elements: add "no text, no labels, no background elements"

## Preparing Icons for Composition

- Always use `--transparent` flag
- Maintain consistent canvas size across related icons (1024x1024)
- Name files descriptively: `brain_eeg.png`, `emg_sensor.png`
- Icons will be scaled down in figure composition (typically 60-100pt display width)

## Configuration

When the **codex** backend is selected, the script invokes `codex exec` and relies on the existing Codex CLI login (`~/.codex/auth.json` or `CODEX_HOME/auth.json`). Run `codex login` once if not already authenticated.

When the **api** backend is selected, the script reads `OPENAI_API_KEY` from:
1. `.env` file in the current directory
2. `~/.env` file
3. Environment variable

Dependencies are handled on-the-fly via `uv run --with openai --with python-dotenv --with pillow`. The `openai` package is only required for the `api` backend; `python-dotenv` and `pillow` are used by both.

## Available Template Categories

- **neuroscience**: brain-eeg, neuron, eeg-cap, brain-regions
- **molecular-biology**: dna-helix, rna-strand, protein, cell
- **physiology**: muscle-emg, heart, lung
- **laboratory**: microscope, petri-dish, flask
- **clinical**: patient-silhouette, hospital, clinical-trial
- **data-science**: network-graph, scatter-plot, pipeline
- **engineering**: wearable-sensor, circuit-board, electrode

Full template schema and element definitions: `icon-bible.md`

## Prompt Templates by Category

### Biological Structure
```
A flat minimalist icon of [structure], simple geometric shapes,
[palette], white background, no text, clean vector style,
centered, Nature journal figure aesthetic
```

### Laboratory Equipment
```
A flat minimalist pictogram of [equipment], schematic style,
simple lines, [palette], no gradients, no shadows, centered,
scientific illustration style
```

### Data/Computational
```
A flat minimalist icon representing [concept], abstract geometric design,
[palette], clean edges, infographic style, no text labels,
centered on white background
```

### Clinical/Patient
```
A flat minimalist pictogram of [clinical element], simple silhouette style,
[palette], no facial details, gender-neutral where applicable,
medical infographic aesthetic
```
