---
description: Academic literature search and citation management
allowed-tools: Bash, Read, Write, Glob, Grep
argument-hint: <search|lookup|cite|canonical|pdf|convert|ids|batch-fetch|config> [args...]
---

# OpenCite CLI

You are helping the user run opencite commands for academic literature search and citation management.

## Setup Check

First, verify opencite is installed:

```bash
uvx opencite --version
```

If not installed, run `uv pip install opencite` or `pip install opencite`. PDF conversion support (markitdown, markit-mistral) is included by default.

## Routing

Based on the user's request, determine which subcommand to use:

- **search** - Find papers matching a query across Semantic Scholar, OpenAlex, PubMed, arXiv, and bioRxiv/medRxiv
- **lookup** - Look up a specific paper by DOI, PMID, PMCID, or other identifier
- **cite** - Get citing/cited-by papers for a given identifier (citation graph)
- **canonical** - Find the most-cited papers in a field or topic
- **pdf** - Download a PDF for a paper by identifier
- **convert** - Convert a PDF file to markdown
- **ids** - Convert between identifier types (DOI, PMID, PMCID)
- **batch-fetch** - Download PDFs for multiple papers from a file, JSON, or stdin
- **config** - Manage opencite configuration (init, show, path)

## Research Workflow

When the user asks for literature research, follow this workflow:

### 1. Search for papers

Based on user needs, use the appropriate search strategy:
- `canonical` for foundational/most-cited papers in a field
- `search` for recent or topic-specific papers
- `cite` to explore the citation graph of a known paper
- Combine strategies as needed (e.g., canonical + recent search)

### 2. Evaluate and select

Review the results and identify which papers to retrieve. Consider citation count, relevance, recency, and open access availability.

### 3. Download and convert

**For multiple papers (preferred):** save search results as JSON and use batch-fetch:

```bash
uvx opencite search "topic" --max 10 -f json -o results.json
uvx opencite batch-fetch --from-json results.json --convert -o ./papers --summary report.json
```

`batch-fetch --convert` automatically creates this directory structure:

```
papers/
├── pdf/          # downloaded PDFs
└── markdown/     # converted markdown files
    └── img/      # per-paper image directories (mistral only)
```

**For individual papers:**

```bash
uvx opencite pdf "10.1234/example" -o papers/pdf/ --convert
```

Note: `pdf --convert` places the markdown file next to the PDF and does not extract images. For the organized subdirectory layout with image extraction, use `batch-fetch`.

### 4. Read and synthesize

Read the generated markdown files for analysis and synthesis. When using `batch-fetch`, markdown is in `papers/markdown/` and extracted images (if using markit-mistral) are in per-paper subdirectories under `papers/markdown/img/`.

### PDF Conversion

Conversion uses markit-mistral when `MISTRAL_API_KEY` is set (better for math, tables, and complex layouts with image extraction support). Otherwise, it falls back to markitdown (free, local). Both are included by default.

## Common Patterns

### Search and export BibTeX
```bash
uvx opencite search "neural oscillations" -f bibtex -o refs.bib
```

### Look up by DOI
```bash
uvx opencite lookup "10.1038/s41586-024-07487-w"
```

### Citation graph
```bash
uvx opencite cite "10.1038/s41586-024-07487-w" --direction both
```

### Find canonical papers
```bash
uvx opencite canonical "transformer architecture" --max 10
```

### Download PDF and convert
```bash
uvx opencite pdf "10.1038/s41586-024-07487-w" -o paper.pdf --convert
uvx opencite convert paper.pdf -o paper.md --converter auto
```

### Batch download with conversion
```bash
uvx opencite search "tDCS" -f json -o results.json
uvx opencite batch-fetch --from-json results.json --convert -o ./papers --summary report.json
```

### Convert IDs
```bash
uvx opencite ids "10.1038/s41586-024-07487-w" -f json
```

### Configure API keys
```bash
uvx opencite config init   # creates ~/.opencite/config.toml template
uvx opencite config show   # display resolved config (keys masked)
uvx opencite config path   # show config file location
```

## Output Formats

All search/lookup/cite/canonical commands support `-f`/`--format`:
- `text` (default) - human-readable table
- `json` - structured JSON
- `bibtex` - BibTeX entries for citation managers
- `csv` - comma-separated values

Use `-o`/`--output <file>` to write to a file instead of stdout.

Run the appropriate command based on the user's request. If the user's intent is ambiguous, ask which subcommand they need.
