---
description: Academic literature search and citation management
allowed-tools: Bash, Read, Write, Glob, Grep
argument-hint: <search|lookup|cite|canonical|pdf|convert|ids|batch-fetch|config> [args...]
---

# OpenCite CLI

Run opencite commands for academic literature search and citation management.

## Setup Check

Verify opencite is installed:

```bash
uvx opencite --version
```

If not installed, run `uv pip install opencite`.

## Routing

Based on the request, determine which subcommand to run:

| Command | When to use |
|---------|-------------|
| `search` | Find papers matching a query |
| `lookup` | Look up a paper by DOI, PMID, PMCID, or other identifier |
| `cite` | Explore citing/cited-by papers (citation graph) |
| `canonical` | Find most-cited, foundational papers in a field |
| `pdf` | Download a PDF by identifier |
| `convert` | Convert a local PDF to markdown |
| `ids` | Convert between identifier types (DOI, PMID, PMCID) |
| `batch-fetch` | Download and optionally convert PDFs for multiple papers |
| `config` | Manage configuration (init, show, path) |

All search/lookup/cite/canonical commands support `-f text|json|bibtex|csv` and `-o FILE`.

## Execution

For detailed workflows, option listings, and configuration, consult the opencite skill (`SKILL.md` and files under `references/`).

If the intent is ambiguous, ask which subcommand is needed before proceeding.
