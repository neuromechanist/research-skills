---
name: opencite
description: This skill should be used when the user asks to "search for papers", "find citations", "look up a DOI", "get BibTeX", "download PDF", "convert PDF to markdown", "find canonical papers", "convert identifiers", "batch download papers", "configure opencite", or mentions opencite, academic literature search, citation management, or paper retrieval.
version: 0.3.0
---

# OpenCite CLI Reference

OpenCite is a CLI tool and Python library for academic literature search and citation management. It aggregates results from Semantic Scholar, OpenAlex, PubMed, arXiv, and bioRxiv/medRxiv, deduplicates them, and outputs formatted results. It also supports PDF retrieval, PDF-to-markdown conversion (included by default), and batch operations.

## Installation

```bash
# Option 1: uv (recommended)
uv pip install opencite

# Option 2: pip
pip install opencite

# Option 3: uvx (no install needed, runs from cache)
uvx opencite --version
```

PDF conversion support (markitdown and markit-mistral) is included by default. If `MISTRAL_API_KEY` is set, markit-mistral is used for better handling of math, tables, and complex layouts. Otherwise, markitdown (free, local) is used as the fallback.

For development:
```bash
uv sync --extra dev        # install from source with dev tools
```

## Configuration

opencite supports TOML config, `.env` files, and environment variables.

```bash
uvx opencite config init   # creates ~/.opencite/config.toml template
uvx opencite config show   # display resolved config (keys masked)
uvx opencite config path   # show config file location
```

Config loading priority (later overrides earlier):
1. `~/.opencite/config.toml`
2. `~/.opencite/.env`
3. `.env` in working directory
4. Environment variables

### API Keys

- `SEMANTIC_SCHOLAR_API_KEY` - Semantic Scholar API
- `PUBMED_API_KEY` - NCBI/PubMed API
- `OPENALEX_API_KEY` - OpenAlex API (required since Feb 2026)
- `MISTRAL_API_KEY` - (optional) Mistral AI for enhanced PDF-to-markdown conversion

### Publisher Tokens (optional, for authenticated PDF access)

- `ELSEVIER_API_KEY` - Elsevier/ScienceDirect
- `WILEY_TDM_TOKEN` - Wiley TDM
- `SPRINGER_API_KEY` - Springer Nature

## Research Workflow

When the user asks for literature research, paper retrieval, or reading material on a topic, follow this end-to-end workflow.

### 1. Search for relevant papers

Choose the search strategy based on user needs:

- **Canonical/foundational papers**: `uvx opencite canonical "topic" --max 10`
- **Recent or specific papers**: `uvx opencite search "query" --max 20 --sort citations`
- **Citation graph exploration**: `uvx opencite cite "DOI" --direction both`
- Combine strategies when appropriate (e.g., canonical for background + search for recent work)

### 2. Evaluate and select papers

Review results considering citation count, relevance, recency, and open access availability. Present a summary to the user and confirm which papers to retrieve.

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

## Commands

### search - Find papers

```bash
uvx opencite search "query string" [options]
```

Options:
- `--max N` - Max results (default: 20)
- `--source all|openalex|s2|pubmed|arxiv|biorxiv` - Which API to query (default: all)
- `--year-from YYYY` - Published after year
- `--year-to YYYY` - Published before year
- `--oa-only` - Open access only
- `--sort relevance|citations|year` - Sort order (default: relevance)
- `-f, --format text|json|bibtex|csv` - Output format
- `-o, --output FILE` - Write to file
- `-v, --verbose` - Show abstracts

### lookup - Look up a paper

```bash
uvx opencite lookup IDENTIFIER [IDENTIFIER ...] [options]
```

Accepts DOI, `pmid:X`, `pmc:X`, `arxiv:X`, S2 ID, or OpenAlex ID. Auto-detects the type. Supports multiple IDs.

Options:
- `-f, --format text|json|bibtex`
- `-o, --output FILE`
- `--enrich` - Fetch from all APIs for richer data
- `--append-bib FILE` - Append BibTeX to a .bib file
- `-v, --verbose`

### cite - Citation graph

```bash
uvx opencite cite IDENTIFIER [options]
```

Options:
- `--direction citing|references|both` - Direction (default: citing)
- `--max N` - Max papers (default: 50)
- `--sort citations|year` - Sort order (default: citations)
- `--min-citations N` - Minimum citation count filter
- `-f, --format text|json|bibtex`
- `-o, --output FILE`
- `-v, --verbose`

### canonical - Most-cited papers

```bash
uvx opencite canonical "topic" [options]
```

Finds the most-cited, foundational papers for a topic.

Options:
- `--max N` - Number of papers (default: 10)
- `--year-from YYYY` - Published after year
- `--min-citations N` - Minimum citations (default: 100)
- `-f, --format text|json|bibtex`
- `-o, --output FILE`
- `-v, --verbose`

### pdf - Download PDF

```bash
uvx opencite pdf IDENTIFIER [options]
```

Tries multiple sources in priority order: publisher APIs (if tokens configured), OpenAlex/S2 PDF locations, PMC Open Access, direct arXiv/bioRxiv URL, DOI content negotiation.

Options:
- `-o, --output PATH` - Output file path (.pdf) or directory (default: .)
- `--filename NAME` - Custom filename
- `--convert` - Also convert downloaded PDF to markdown
- `--converter auto|markitdown|mistral` - Converter for markdown (default: auto)

### convert - PDF to markdown

```bash
uvx opencite convert FILE.pdf [options]
```

Auto mode uses markit-mistral when `MISTRAL_API_KEY` is set (better for math and complex layouts), otherwise falls back to markitdown (free, local). Both converters are included by default.

Options:
- `-o, --output FILE` - Output markdown path
- `--converter auto|markitdown|mistral` - Conversion method (default: auto)
- `--extract-images` - Extract images from PDF (mistral only)
- `--images-dir DIR` - Directory for extracted images

### ids - Convert identifiers

```bash
uvx opencite ids IDENTIFIER [IDENTIFIER ...] [options]
```

Converts between DOI, PMID, and PMCID using the NCBI ID Converter API.

Options:
- `-f, --format text|json`

### batch-fetch - Batch download PDFs

```bash
uvx opencite batch-fetch FILE [options]
uvx opencite batch-fetch --from-json FILE [options]
uvx opencite batch-fetch --from-stdin [options]
```

Downloads PDFs for multiple papers with controlled concurrency. When `--convert` is used, output is organized into subdirectories:

```
output-dir/
├── pdf/          # downloaded PDFs
└── markdown/     # converted markdown files
    └── img/      # per-paper image directories (mistral only)
```

Input sources (mutually exclusive):
- Positional `FILE` - Text file with IDs, one per line
- `--from-json FILE` - JSON file (array of DOIs or opencite search results)
- `--from-stdin` - Read IDs from stdin (pipe-friendly)

Options:
- `-o, --output-dir DIR` - Output directory (default: ./papers)
- `--convert` - Also convert each PDF to markdown
- `--converter auto|markitdown|mistral` - Converter (default: auto)
- `--concurrency N` - Max concurrent downloads (default: 3)
- `--summary FILE` - Write JSON summary report to file

### config - Manage configuration

```bash
uvx opencite config init   # create ~/.opencite/config.toml template
uvx opencite config show   # display resolved config (keys masked)
uvx opencite config path   # show config file location
```

## Common Workflows

### Literature review: search, filter, export
```bash
# Search broadly
uvx opencite search "motor cortex oscillations" --max 20 -f json -o results.json

# Export BibTeX for citation manager
uvx opencite search "motor cortex oscillations" --max 20 -f bibtex -o refs.bib
```

### Deep-dive on a paper's impact
```bash
# Look up the paper
uvx opencite lookup "10.1038/s41586-024-07487-w" -v

# Get papers that cite it
uvx opencite cite "10.1038/s41586-024-07487-w" --direction citing --max 20

# Get its references
uvx opencite cite "10.1038/s41586-024-07487-w" --direction references --max 20
```

### Full research pipeline: search, download, convert, read
```bash
# 1. Find canonical papers in the field
uvx opencite canonical "attention mechanism" --max 5 -f json -o results.json

# 2. Batch download and convert all found papers
uvx opencite batch-fetch --from-json results.json --convert -o ./papers --summary report.json

# 3. Papers are now organized in:
#    papers/pdf/       - PDF files
#    papers/markdown/  - Markdown files ready for reading
#    papers/markdown/img/<paper>/ - Extracted figures (mistral only)
```

### Cross-reference identifier conversion
```bash
# Single ID
uvx opencite ids "10.1001/jama.2024.12345"

# Multiple IDs with JSON output
uvx opencite ids "10.1001/jama.2024.12345" "PMC7654321" -f json
```

## Error Handling

- **Rate limits**: Semantic Scholar has aggressive rate limiting (1 req/sec). If you get rate limit errors, wait and retry.
- **Missing API keys**: Commands will warn about missing keys but still query available sources.
- **Timeouts**: API calls may time out; retry or try a different source with `--source`.
- **No results**: Try broader search terms or check identifier format.
- **PDF not found**: opencite reports which sources were tried and why each failed. Papers behind paywalls may need institutional access or publisher API tokens.

## Python API

For programmatic use:
```python
from opencite import Config, Paper, SearchResult
from opencite.search import SearchOrchestrator

config = Config.from_env()
async with SearchOrchestrator(config) as searcher:
    results = await searcher.search("query", max_results=10)
```
