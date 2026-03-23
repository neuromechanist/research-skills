---
name: icon-generation
description: This skill should be used when the user asks to "generate an icon", "create a scientific icon", "make a flat icon", "create a Nature-style icon", "generate a Science-style icon", "make an icon for a figure", "create a pictogram", or mentions scientific icons, flat icons, pictograms for papers, or icon generation for research figures.
version: 0.1.0
---

# Scientific Icon Generation

Generates flat, minimalist scientific icons in the style commonly seen in Nature, Science, and Cell journal figures, using OpenAI's gpt-image-1 model.

## When to Use

Activate when the user needs individual scientific icons or pictograms for use in research figures, graphical abstracts, or presentations. These icons follow the flat, clean aesthetic of top-tier journal figures: simple shapes, limited color palette, no gradients, no 3D effects.

## Style Guide

### Visual Characteristics
- **Flat design**: No gradients, shadows, or 3D effects
- **Minimalist**: Simple geometric shapes, reduced detail
- **Limited palette**: 2-4 colors per icon, with one accent color
- **Consistent stroke**: Uniform line weight throughout
- **Clean edges**: Sharp, precise outlines
- **Square canvas**: 1024x1024 px default, scalable
- **White or transparent background**: For compositing into figures

### Color Approach
- Use a primary color for the main subject
- Use a secondary color for accents or contrast
- White for negative space and internal details
- Avoid photorealistic colors; prefer slightly stylized tones
- Common palettes: teal/coral, navy/gold, forest/amber, slate/orange

### Subject Categories
- **Biology**: cells, neurons, DNA, organs, organisms, microscopes
- **Chemistry**: molecules, flasks, reactions, periodic elements
- **Physics**: waves, particles, magnets, circuits, lasers
- **Engineering**: sensors, devices, wearables, electrodes, robots
- **Data**: graphs, networks, databases, code, algorithms
- **Clinical**: patients, hospitals, trials, medications, scans

## Workflow

### 1. Determine icon requirements

Gather from the user:
- **Subject**: What the icon represents (e.g., "brain with EEG electrodes")
- **Color palette**: Preferred colors or "match this figure's palette"
- **Background**: Transparent (PNG) or white
- **Size**: Default 1024x1024, or specify dimensions
- **Quantity**: Single icon or batch

### 2. Generate the icon

There are two approaches: **template-based** (recommended for consistency) and **free-form**.

#### Template-based generation (preferred)

Use predefined templates from the icon bible (`references/icon-templates.json`). Each template defines elements, shapes, colors, and spatial relationships in a structured JSON format, producing consistent results.

```bash
# List available templates
uv run scripts/generate_icon.py --list-templates

# Generate from a specific template
uv run scripts/generate_icon.py --template brain-eeg -o brain_eeg.png

# Override colors from template
uv run scripts/generate_icon.py --template neuron --colors "#3498DB,#E74C3C" -o neuron.png

# Generate all icons in a category
uv run scripts/generate_icon.py --category neuroscience -o icons/neuro/

# Template with transparency
uv run scripts/generate_icon.py --template dna-helix -o dna.png --transparent
```

To add a new template, edit `references/icon-templates.json` following the schema in `references/icon-bible.md`. Each template defines:
- **elements**: Individual visual components (shapes, colors, positions, layers)
- **composition**: Canvas size, margins, alignment, background
- **palette**: Primary, secondary, accent, and neutral colors
- **prompt_hints**: Additional style modifiers

#### Free-form generation

For one-off icons not in the bible:

```bash
# Basic usage
uv run scripts/generate_icon.py "a human brain with EEG electrodes" -o brain_eeg.png

# With transparency
uv run scripts/generate_icon.py "a DNA helix" -o dna.png --transparent

# With specific colors
uv run scripts/generate_icon.py "a neuron" -o neuron.png --colors "teal,white"

# Batch generation
uv run scripts/generate_icon.py "a flat icon of a {item}" -o icons/ --batch "brain,heart,lung,kidney,liver"
```

The script reads `OPENAI_API_KEY` from:
1. `.env` file in the current directory
2. `~/.env` file
3. Environment variable

### 3. Review and iterate

Generated icons may need refinement. Common adjustments:
- Simplify if too detailed: add "extremely minimalist, simple geometric shapes" to prompt
- Adjust colors: specify exact hex codes in prompt
- Fix proportions: add "centered, symmetrical, well-proportioned" to prompt
- Remove unwanted elements: add "no text, no labels, no background elements" to prompt

### 4. Prepare for figure composition

Save icons as PNG with transparency for use in the **pdf-figures** skill:
- Use `--transparent` flag for compositing
- Maintain consistent canvas size across related icons
- Name files descriptively: `brain_eeg.png`, `emg_sensor.png`, etc.

## Prompt Engineering

### Base prompt template
```
A flat, minimalist scientific icon of [SUBJECT], in the style of Nature/Science journal figures.
Simple geometric shapes, [COLOR_PALETTE], no gradients, no shadows, no 3D effects,
no text, no labels, clean edges, centered on [white/transparent] background.
```

### Effective modifiers
- "pictogram style" - more abstract, symbolic
- "infographic icon" - slightly more detail, good for graphical abstracts
- "schematic" - technical, engineering-oriented
- "silhouette" - single-color, maximum simplicity
- "line art" - outline only, no fill

### Common pitfalls to avoid
- Avoid "realistic" or "photorealistic" in prompts
- Avoid "detailed" or "complex"; prefer "simple" and "minimalist"
- Avoid requesting text within the icon (add labels separately in figures)
- Avoid multiple disconnected elements (keep each icon as a single concept)

## Configuration

### Environment Setup
Create a `.env` file with the OpenAI API key:
```
OPENAI_API_KEY=sk-...
```

### Dependencies
The generation script requires:
```bash
uv pip install openai python-dotenv pillow
```

## Icon Bible System

The icon bible (`references/icon-templates.json`) is a structured catalog of icon templates. When generating a new icon, first check if a suitable template exists. If creating something new, consider adding it to the bible for future reuse.

### Template JSON structure (abbreviated)
```json
{
  "id": "brain-eeg",
  "name": "Brain with EEG Electrodes",
  "category": "neuroscience",
  "elements": [
    {
      "id": "brain",
      "shape": "organic-silhouette",
      "description": "Simplified brain silhouette...",
      "fill": "#2D7D9A",
      "position": "center",
      "size": "primary"
    }
  ],
  "palette": { "primary": "#2D7D9A", "secondary": "#E8734A" },
  "prompt_hints": ["side view", "no text"]
}
```

### Available categories
- **neuroscience**: brain-eeg, neuron, eeg-cap, brain-regions, etc.
- **molecular-biology**: dna-helix, rna-strand, protein, cell, etc.
- **physiology**: muscle-emg, heart, lung, etc.
- **laboratory**: microscope, petri-dish, flask, etc.
- **clinical**: patient-silhouette, hospital, clinical-trial, etc.
- **data-science**: network-graph, scatter-plot, pipeline, etc.
- **engineering**: wearable-sensor, circuit-board, electrode, etc.

## Additional Resources

### Reference Files
- **`references/icon-bible.md`** - Icon bible documentation: JSON schema, element fields, shape types, position syntax, categories
- **`references/icon-templates.json`** - Structured icon template catalog (the icon bible itself)
- **`references/style-guide.md`** - Detailed visual style examples and color palettes

### Scripts
- **`scripts/generate_icon.py`** - Icon generation script supporting both template-based and free-form generation
