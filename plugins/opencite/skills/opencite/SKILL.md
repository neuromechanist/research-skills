---
name: opencite
description: Use this skill for "search for papers", "find citations", "look up a DOI", "get BibTeX", "download PDF", "convert PDF to markdown", "find canonical papers", "convert identifiers", "batch download papers", "configure opencite", "literature review", "find related papers", "what papers cite this", "export references", "read this paper", or mentions of opencite, Semantic Scholar, OpenAlex, PubMed, academic literature search, citation management, or paper retrieval.
version: 0.1.0
---

# OpenCite CLI

OpenCite is a CLI tool for academic literature search and citation management. It aggregates results from Semantic Scholar, OpenAlex, PubMed, arXiv, and bioRxiv/medRxiv, deduplicates them, and outputs formatted results. It also supports PDF retrieval, PDF-to-markdown conversion, and batch operations.

## Installation

```bash
# Recommended
uv pip install opencite

# Alternative: run without installing
uvx opencite --version
```

PDF conversion support (markitdown and markit-mistral) is included by default. When `MISTRAL_API_KEY` is set, markit-mistral handles math, tables, and complex layouts. Otherwise, markitdown (free, local) is the fallback.

For development:
```bash
uv sync --extra dev
```

## Research Workflow

Follow this end-to-end workflow for literature research, paper retrieval, or reading material on a topic.

### 1. Search for relevant papers

Choose the search strategy based on the request:

- **Canonical/foundational papers**: `uvx opencite canonical "topic" --max 10`
- **Recent or specific papers**: `uvx opencite search "query" --max 20 --sort citations`
- **Citation graph exploration**: `uvx opencite cite "DOI" --direction both`
- Combine strategies when appropriate (e.g., canonical for background + search for recent work)

### 2. Evaluate and select papers

Review results considering citation count, relevance, recency, and open access availability. Present a summary and confirm which papers to retrieve.

### 3. Download and convert

**For multiple papers (preferred):** Save search results as JSON and use batch-fetch:

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

Read the converted markdown files for deeper analysis:

- Summarize key findings across papers
- Identify common themes and disagreements
- When using `batch-fetch`, markdown is in `papers/markdown/` and extracted images (markit-mistral only) are in per-paper subdirectories under `papers/markdown/img/`
- Generate BibTeX for citation: `uvx opencite lookup "DOI" -f bibtex --append-bib refs.bib`

## Command Summary

| Command | Purpose |
|---------|---------|
| `search` | Find papers matching a query across multiple APIs |
| `lookup` | Look up a specific paper by DOI, PMID, PMCID, or other identifier |
| `cite` | Get citing/cited-by papers for a given identifier |
| `canonical` | Find the most-cited, foundational papers for a topic |
| `pdf` | Download a PDF for a paper by identifier |
| `convert` | Convert a local PDF file to markdown |
| `ids` | Convert between identifier types (DOI, PMID, PMCID) |
| `batch-fetch` | Download PDFs for multiple papers with optional conversion |
| `config` | Manage opencite configuration (init, show, path) |

For full option listings, see [references/cli-reference.md](references/cli-reference.md).

## Configuration Essentials

Initialize configuration and check resolved values:

```bash
uvx opencite config init   # create ~/.opencite/config.toml template
uvx opencite config show   # display resolved config (keys masked)
```

Key environment variables:
- `SEMANTIC_SCHOLAR_API_KEY` - Semantic Scholar API
- `PUBMED_API_KEY` - NCBI/PubMed API
- `OPENALEX_API_KEY` - OpenAlex API (required since Feb 2026)
- `MISTRAL_API_KEY` - Enhanced PDF-to-markdown conversion (optional)

For full configuration details including publisher tokens and loading priority, see [references/api-keys-and-config.md](references/api-keys-and-config.md).

## Error Handling

- **Rate limits**: Semantic Scholar has aggressive rate limiting (1 req/sec). When rate limit errors occur, wait and retry.
- **Missing API keys**: Commands warn about missing keys but still query available sources.
- **Timeouts**: Retry the command or try a different source with `--source`.
- **PDF not found**: opencite reports which sources were tried and why each failed. Papers behind paywalls may need institutional access or publisher API tokens.

## References

- [CLI Reference](references/cli-reference.md) - Complete option listings for all subcommands and the Python API
- [Common Workflows](references/common-workflows.md) - Worked examples for typical usage patterns
- [API Keys and Configuration](references/api-keys-and-config.md) - Configuration loading, API keys, and publisher tokens
