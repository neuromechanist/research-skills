# Icon Bible

## Overview

The icon bible is a catalog of predefined icon templates stored as JSON. Each template defines the visual elements, their shapes, colors, spatial relationships, and composition rules so that the image generator produces consistent, high-quality scientific icons.

## JSON Schema

Each icon template follows this structure:

```json
{
  "id": "brain-eeg",
  "name": "Brain with EEG Electrodes",
  "category": "neuroscience",
  "tags": ["brain", "eeg", "electrodes", "recording"],
  "description": "Side-view brain silhouette with electrode dots on the scalp surface",
  "elements": [
    {
      "id": "brain",
      "shape": "organic-silhouette",
      "description": "Simplified brain silhouette in side view with visible cortical folds",
      "fill": "#2D7D9A",
      "stroke": "none",
      "position": "center",
      "size": "primary",
      "z_index": 0
    },
    {
      "id": "electrodes",
      "shape": "circle-array",
      "description": "6-8 small circles arranged along the top surface of the brain",
      "fill": "#E8734A",
      "stroke": "none",
      "position": "on:brain:top-surface",
      "size": "tiny",
      "count": 7,
      "z_index": 1
    },
    {
      "id": "wires",
      "shape": "thin-lines",
      "description": "Thin lines extending from each electrode upward, bundled together",
      "stroke": "#4A4A4A",
      "stroke_width": 1,
      "position": "from:electrodes:top",
      "z_index": 0.5
    }
  ],
  "composition": {
    "background": "transparent",
    "canvas_size": 1024,
    "margin_percent": 12,
    "alignment": "center",
    "style": "flat-minimalist"
  },
  "palette": {
    "primary": "#2D7D9A",
    "secondary": "#E8734A",
    "accent": "#F5C242",
    "neutral": "#4A4A4A"
  },
  "prompt_hints": [
    "side view",
    "simplified cortical folds",
    "electrodes as small dots",
    "no text or labels"
  ]
}
```

## Schema Field Reference

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique identifier (kebab-case) |
| `name` | string | yes | Human-readable name |
| `category` | string | yes | Domain category |
| `tags` | string[] | yes | Search tags |
| `description` | string | yes | One-sentence description of the complete icon |
| `elements` | Element[] | yes | Visual components of the icon |
| `composition` | Composition | yes | Layout and canvas rules |
| `palette` | Palette | yes | Color definitions |
| `prompt_hints` | string[] | no | Additional prompt modifiers |

### Element Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Element identifier |
| `shape` | string | yes | Shape type (see Shape Types below) |
| `description` | string | yes | Detailed description for the generator |
| `fill` | string | no | Fill color (hex or palette reference) |
| `stroke` | string | no | Stroke color |
| `stroke_width` | number | no | Stroke width in relative units |
| `position` | string | yes | Positioning rule (see Position Syntax) |
| `size` | string | yes | Relative size: tiny, small, medium, large, primary |
| `z_index` | number | no | Layer order (higher = on top) |
| `count` | number | no | For array/repeated elements |
| `rotation` | number | no | Rotation in degrees |

### Shape Types

| Shape | Description |
|-------|-------------|
| `circle` | Simple circle |
| `circle-array` | Multiple circles in a pattern |
| `rectangle` | Simple rectangle |
| `rounded-rectangle` | Rectangle with rounded corners |
| `organic-silhouette` | Free-form organic shape (brain, cell, organ) |
| `helix` | Double helix (DNA) or single helix |
| `line` | Single straight line |
| `thin-lines` | Multiple thin lines |
| `curve` | Bezier curve or arc |
| `arrow` | Directional arrow |
| `star` | Star/burst shape |
| `polygon` | Regular polygon (triangle, hexagon, etc.) |
| `wave` | Sinusoidal wave pattern |
| `grid` | Grid of elements |
| `tree` | Branching tree structure |
| `network` | Nodes and edges |

### Position Syntax

| Syntax | Meaning |
|--------|---------|
| `center` | Centered on canvas |
| `top-left` | Top-left quadrant |
| `top-right` | Top-right quadrant |
| `bottom-left` | Bottom-left quadrant |
| `bottom-right` | Bottom-right quadrant |
| `on:<element_id>:<location>` | Positioned relative to another element |
| `from:<element_id>:<anchor>` | Extends from another element |
| `inside:<element_id>` | Contained within another element |
| `surrounding:<element_id>` | Wraps around another element |
| `adjacent:<element_id>:<direction>` | Next to another element (left/right/above/below) |

### Size Scale

| Size | Approximate % of canvas |
|------|------------------------|
| `tiny` | 3-5% |
| `small` | 8-12% |
| `medium` | 20-30% |
| `large` | 40-50% |
| `primary` | 55-70% |

## Categories

### Neuroscience
- brain-eeg, brain-fmri, neuron, synapse, electrode-array, eeg-cap, brain-regions, neural-network-bio, spinal-cord, motor-cortex

### Molecular Biology
- dna-helix, rna-strand, protein, cell, mitochondria, ribosome, gene-expression, crispr, antibody, receptor

### Physiology
- heart, lung, muscle-fiber, emg-sensor, blood-vessel, skeleton, joint, tendon, eye, ear

### Data Science
- scatter-plot, network-graph, heatmap, pipeline, database, algorithm, bar-chart, distribution, matrix, tensor

### Laboratory
- microscope, petri-dish, flask, centrifuge, pipette, gel-electrophoresis, pcr-machine, spectrophotometer

### Clinical
- patient-silhouette, hospital, clinical-trial, medication, mri-scanner, stethoscope, wheelchair, prosthetic

### Engineering
- sensor, wearable-device, circuit-board, robot-arm, 3d-printer, laser, electrode, amplifier

## Using Templates with generate_icon.py

The script can read templates from the icon bible:

```bash
# Generate from a template
uv run scripts/generate_icon.py --template brain-eeg -o brain_eeg.png

# Override colors from template
uv run scripts/generate_icon.py --template brain-eeg --colors "#3498DB,#E74C3C" -o brain_eeg_alt.png

# Generate all icons in a category
uv run scripts/generate_icon.py --category neuroscience -o icons/neuro/

# List available templates
uv run scripts/generate_icon.py --list-templates
```
