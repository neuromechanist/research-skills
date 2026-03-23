# OpenCite CLI Reference

Complete option listings for all opencite subcommands.

## search - Find papers

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

## lookup - Look up a paper

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

## cite - Citation graph

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

## canonical - Most-cited papers

```bash
uvx opencite canonical "topic" [options]
```

Find the most-cited, foundational papers for a topic.

Options:
- `--max N` - Number of papers (default: 10)
- `--year-from YYYY` - Published after year
- `--min-citations N` - Minimum citations (default: 100)
- `-f, --format text|json|bibtex`
- `-o, --output FILE`
- `-v, --verbose`

## pdf - Download PDF

```bash
uvx opencite pdf IDENTIFIER [options]
```

Tries multiple sources in priority order: publisher APIs (if tokens configured), OpenAlex/S2 PDF locations, PMC Open Access, direct arXiv/bioRxiv URL, DOI content negotiation.

Options:
- `-o, --output PATH` - Output file path (.pdf) or directory (default: .)
- `--filename NAME` - Custom filename
- `--convert` - Also convert downloaded PDF to markdown
- `--converter auto|markitdown|mistral` - Converter for markdown (default: auto)

## convert - PDF to markdown

```bash
uvx opencite convert FILE.pdf [options]
```

Auto mode uses markit-mistral when `MISTRAL_API_KEY` is set (better for math and complex layouts), otherwise falls back to markitdown (free, local). Both converters are included by default.

Options:
- `-o, --output FILE` - Output markdown path
- `--converter auto|markitdown|mistral` - Conversion method (default: auto)
- `--extract-images` - Extract images from PDF (mistral only)
- `--images-dir DIR` - Directory for extracted images

## ids - Convert identifiers

```bash
uvx opencite ids IDENTIFIER [IDENTIFIER ...] [options]
```

Convert between DOI, PMID, and PMCID using the NCBI ID Converter API.

Options:
- `-f, --format text|json`

## batch-fetch - Batch download PDFs

```bash
uvx opencite batch-fetch FILE [options]
uvx opencite batch-fetch --from-json FILE [options]
uvx opencite batch-fetch --from-stdin [options]
```

Download PDFs for multiple papers with controlled concurrency. When `--convert` is used, output is organized into subdirectories:

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

## config - Manage configuration

```bash
uvx opencite config init   # create ~/.opencite/config.toml template
uvx opencite config show   # display resolved config (keys masked)
uvx opencite config path   # show config file location
```

## Python API

For programmatic use:

```python
from opencite import Config, Paper, SearchResult
from opencite.search import SearchOrchestrator

config = Config.from_env()
async with SearchOrchestrator(config) as searcher:
    results = await searcher.search("query", max_results=10)
```
