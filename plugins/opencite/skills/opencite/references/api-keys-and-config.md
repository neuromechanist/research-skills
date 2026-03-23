# API Keys and Configuration

Detailed configuration reference for opencite.

## Configuration Loading

opencite supports TOML config, `.env` files, and environment variables.

```bash
uvx opencite config init   # create ~/.opencite/config.toml template
uvx opencite config show   # display resolved config (keys masked)
uvx opencite config path   # show config file location
```

### Loading priority (later overrides earlier):

1. `~/.opencite/config.toml`
2. `~/.opencite/.env`
3. `.env` in working directory
4. Environment variables

## API Keys

| Variable | Service | Required |
|----------|---------|----------|
| `SEMANTIC_SCHOLAR_API_KEY` | Semantic Scholar API | Optional (rate-limited without) |
| `PUBMED_API_KEY` | NCBI/PubMed API | Optional |
| `OPENALEX_API_KEY` | OpenAlex API | Required since Feb 2026 |
| `MISTRAL_API_KEY` | Mistral AI (enhanced PDF-to-markdown) | Optional |

## Publisher Tokens (optional, for authenticated PDF access)

| Variable | Publisher |
|----------|-----------|
| `ELSEVIER_API_KEY` | Elsevier/ScienceDirect |
| `WILEY_TDM_TOKEN` | Wiley TDM |
| `SPRINGER_API_KEY` | Springer Nature |

Publisher tokens enable direct PDF downloads from journals that require authenticated access. Without these tokens, opencite falls back to open-access sources and content negotiation.

## PDF Conversion

Conversion uses markit-mistral when `MISTRAL_API_KEY` is set (better handling of math, tables, and complex layouts with image extraction). Otherwise, markitdown (free, local) is used as the fallback. Both converters are included by default.
