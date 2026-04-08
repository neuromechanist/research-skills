---
description: Create an interactive Reveal.js presentation from a topic or outline
argument-hint: <topic-or-outline> [--theme default|light|dark|academic|minimal] [--slides N]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Create Presentation

Create a presentation JSON file using the Agentic Presentation Builder. Load the `presentation:presentation-builder` skill for schema reference and authoring guidance.

## Process

### 1. Understand the Request
!echo "Topic: $ARGUMENTS"

Determine:
- Subject matter and audience
- Approximate number of slides (default: 8-12)
- Theme preference (default: `academic` for research talks, `default` otherwise)
- Whether speaker notes are needed

### 2. Locate or Set Up the Builder

Check if the Agentic Presentation Builder is available locally:
!ls -d ~/Documents/git/casual-vibers/agent-presentation 2>/dev/null || ls -d ./agent-presentation 2>/dev/null || echo "Builder not found locally"

If not found, clone it:
```bash
git clone https://github.com/neuromechanist/agentic-presentation-builder.git
cd agentic-presentation-builder && bun install
```

### 3. Author the Presentation JSON

Using the schema reference and authoring guide from the skill:
- Create a `presentation.json` file with proper metadata, slides, and elements
- Use appropriate layouts (title slide first, two-column for comparisons, single-column for content)
- Add speaker notes for each slide
- Use Mermaid diagrams for workflows and architectures
- Use callouts for key takeaways
- Keep content density low (advisory warnings flag dense slides)

### 4. Validate

```bash
bun run validate -- presentation.json --json
```

Fix any schema errors and address advisory warnings (dense-copy, dense-bullets, missing-image-alt, etc.).

### 5. Serve and Preview

```bash
bun run dev
# Open http://localhost:3000/?presentation=./public/presentation.json
```

### 6. Report

Provide:
- Path to the generated JSON file
- Validation summary (errors, warnings)
- Instructions to view the presentation
