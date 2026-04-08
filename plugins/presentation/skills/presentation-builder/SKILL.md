---
name: presentation-builder
description: This skill should be used when the user asks to "create a presentation", "make slides", "build a slide deck", "create a talk", "make a keynote", "create a Reveal.js presentation", "generate presentation slides", "make a conference talk", "create a lecture", "build a poster presentation", "create presentation JSON", or mentions presentations, slides, slide decks, Reveal.js, talk preparation, conference presentations, or lecture slides.
version: 0.1.0
---

# Presentation Builder

Create interactive Reveal.js presentations from JSON using the [Agentic Presentation Builder](https://github.com/neuromechanist/agentic-presentation-builder). The builder transforms structured JSON definitions into professional, interactive web-based presentations with Mermaid diagrams, LaTeX math, syntax-highlighted code, and animated progressive reveals.

## Pipeline Overview

```
1. Plan structure  -->  2. Author JSON  -->  3. Validate  -->  4. Serve & present
   (outline, theme)     (schema-driven)      (CLI validator)    (Vite dev server)
```

## Prerequisites

The Agentic Presentation Builder must be available locally. Check common locations:

```bash
ls -d ~/Documents/git/casual-vibers/agent-presentation 2>/dev/null || \
ls -d ./agent-presentation 2>/dev/null || \
echo "Not found -- clone from https://github.com/neuromechanist/agentic-presentation-builder"
```

If not present:
```bash
git clone https://github.com/neuromechanist/agentic-presentation-builder.git
cd agentic-presentation-builder && bun install
```

## Step 1: Plan the Presentation

Before writing JSON, determine:

- **Topic and audience**: Shapes content depth and vocabulary
- **Slide count**: 8-12 for a short talk, 15-25 for a full session
- **Theme**: `academic` for research talks, `default` for general, `dark` for tech demos
- **Key visuals**: Which slides need Mermaid diagrams, images, code blocks, or tables
- **Speaker notes**: Include delivery guidance for each slide

## Step 2: Author the Presentation JSON

Write a `presentation.json` following the schema. See `references/schema-reference.md` for the complete field reference and `references/authoring-guide.md` for best practices.

### Minimal structure

```json
{
  "presentation": {
    "metadata": {
      "title": "My Presentation",
      "author": "Author Name",
      "theme": "academic",
      "aspectRatio": "16:9",
      "controls": {
        "slideNumbers": true,
        "progress": true
      }
    },
    "slides": [
      {
        "id": "title",
        "layout": "title",
        "elements": [
          {
            "type": "text",
            "content": "# Presentation Title",
            "style": { "fontSize": "xxl", "alignment": "center" },
            "position": { "area": "center" }
          },
          {
            "type": "text",
            "content": "Author Name -- Conference 2026",
            "style": { "fontSize": "large", "alignment": "center", "color": "#64748B" },
            "position": { "area": "center", "order": 1 }
          }
        ]
      }
    ]
  }
}
```

### Slide patterns

**Content slide (single-column):**
```json
{
  "id": "key-findings",
  "layout": "single-column",
  "speakerNotes": "Emphasize the 3x improvement in latency.",
  "elements": [
    {
      "type": "text",
      "content": "## Key Findings",
      "style": { "fontSize": "xl" },
      "position": { "area": "header" }
    },
    {
      "type": "bullets",
      "items": [
        "**3x reduction** in processing latency",
        "95% accuracy on held-out test set",
        "Compatible with existing EEG pipelines"
      ],
      "position": { "area": "content" }
    }
  ]
}
```

**Comparison slide (two-column):**
```json
{
  "id": "comparison",
  "layout": "two-column",
  "elements": [
    {
      "type": "text",
      "content": "## Before vs After",
      "style": { "fontSize": "xl" },
      "position": { "area": "header" }
    },
    {
      "type": "bullets",
      "items": ["Manual annotation", "Hours per session", "Inconsistent labels"],
      "position": { "area": "left" }
    },
    {
      "type": "bullets",
      "items": ["Automated pipeline", "Minutes per session", "Standardized HED tags"],
      "position": { "area": "right" }
    }
  ]
}
```

**Diagram slide (Mermaid):**
```json
{
  "id": "architecture",
  "layout": "single-column",
  "elements": [
    {
      "type": "text",
      "content": "## System Architecture",
      "style": { "fontSize": "xl" },
      "position": { "area": "header" }
    },
    {
      "type": "mermaid",
      "diagram": "graph LR\n  A[Raw EEG] --> B[Preprocessing]\n  B --> C[Feature Extraction]\n  C --> D[Classification]\n  D --> E[BCI Output]",
      "position": { "area": "content" }
    }
  ]
}
```

### Element types summary

| Type | Required fields | Key options |
|------|----------------|-------------|
| `text` | `type`, `content` | Markdown, LaTeX math, style, animation |
| `bullets` | `type`, `items` | `bulletStyle`, nested items, animation |
| `image` | `type`, `src` | `alt`, `width`, `height`, `caption` |
| `mermaid` | `type`, `diagram` | `theme` (default/dark/forest/neutral) |
| `callout` | `type`, `content` | `calloutType` (tip/warning/important/note/info), `title` |
| `code` | `type`, `code` | `language`, `caption`, `lineNumbers` |
| `table` | `type`, `headers`, `rows` | `caption` |

## Step 3: Validate

Run the CLI validator before serving:

```bash
cd <builder-directory>
bun run validate -- path/to/presentation.json --json
```

The `--json` flag returns structured output with `valid`, `summary.errorCount`, `summary.warningCount`, `errors[]`, and `warnings[]`. Each issue includes `code`, `severity`, `path`, `message`, and `suggestion`.

Fix all schema errors. Address advisory warnings to improve slide quality (see `references/authoring-guide.md` for the full list and thresholds).

## Step 4: Serve and Present

Copy the JSON file to the builder's `public/` directory (or reference it directly):

```bash
cd <builder-directory>
cp path/to/presentation.json public/
bun run dev
```

Open in browser: `http://localhost:3000/?presentation=./presentation.json`

Press `P` to toggle between authoring and presentation modes, `S` for speaker notes, `O` for slide overview. See `references/authoring-guide.md` for the full keyboard shortcuts and delivery modes.

To open a synced audience screen, use `?presentation=./presentation.json&role=audience&mode=presentation`.

## Additional Resources

### Reference files
- **`references/schema-reference.md`** -- Complete field reference for all element types
- **`references/authoring-guide.md`** -- Layout patterns, content density guidelines, theme selection, validation workflow

### External documentation
- [Agentic Presentation Builder repo](https://github.com/neuromechanist/agentic-presentation-builder)
- [Full documentation site](https://neuromechanist.github.io/agentic-presentation-builder/)
- [JSON Schema](https://github.com/neuromechanist/agentic-presentation-builder/blob/main/schema/presentation.schema.json)
