# Common Workflows

Worked examples for typical opencite usage patterns.

## Literature review: search, filter, export

```bash
# Search broadly
uvx opencite search "motor cortex oscillations" --max 20 -f json -o results.json

# Export BibTeX for citation manager
uvx opencite search "motor cortex oscillations" --max 20 -f bibtex -o refs.bib
```

## Deep-dive on a paper's impact

```bash
# Look up the paper
uvx opencite lookup "10.1038/s41586-024-07487-w" -v

# Get papers that cite it
uvx opencite cite "10.1038/s41586-024-07487-w" --direction citing --max 20

# Get its references
uvx opencite cite "10.1038/s41586-024-07487-w" --direction references --max 20
```

## Full research pipeline: search, download, convert, read

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

## Cross-reference identifier conversion

```bash
# Single ID
uvx opencite ids "10.1001/jama.2024.12345"

# Multiple IDs with JSON output
uvx opencite ids "10.1001/jama.2024.12345" "PMC7654321" -f json
```

## Search and export BibTeX

```bash
uvx opencite search "neural oscillations" -f bibtex -o refs.bib
```

## Citation graph exploration

```bash
uvx opencite cite "10.1038/s41586-024-07487-w" --direction both
```

## Batch download with conversion

```bash
uvx opencite search "tDCS" -f json -o results.json
uvx opencite batch-fetch --from-json results.json --convert -o ./papers --summary report.json
```
