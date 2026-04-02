# Documentation Standards (MkDocs)

## Core Philosophy: Write for Your Future Self
**Good docs** answer questions before they're asked.
**Think:** What would confuse me in 6 months?
**Goal:** New developers productive in <1 hour.

## Setup
```bash
# Python projects (UV)
uv add --dev mkdocs mkdocs-material "mkdocstrings[python]"

# JS/TS projects
bun add -D typedoc
```

## Minimal mkdocs.yml
```yaml
site_name: {{PROJECT_NAME}}
site_url: https://example.com
repo_url: https://github.com/user/repo

theme:
  name: material
  features: [navigation.tabs, search.suggest]

nav:
  - Home: index.md
  - API: api/
  - Guides: guides/

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_root_heading: yes
            members_order: source

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
  - toc
```

## Structure
```
docs/
  index.md           # Home page
  guides/
    getting_started.md
    advanced.md
  api/               # Auto-generated from docstrings
    module_a.md      # Contains ::: my_project.module_a
```

## API Documentation
```markdown
# Module A
::: my_project.module_a
    handler: python
    options:
      show_source: no
```

## Commands
```bash
# Python (MkDocs)
uv run mkdocs serve    # Live preview at localhost:8000
uv run mkdocs build    # Generate site/
uv run mkdocs gh-deploy # Deploy to GitHub Pages

# JS/TS (TypeDoc)
bun run typedoc
```

## Writing Tips (Think Like a Teacher)
- **Start with why:** Context before details
- **Show, don't tell:** Examples > explanations
- **Use admonitions:** `!!! warning "Common mistake"`
- **Code blocks:** Include full context, not fragments
- **Progressive disclosure:** Simple first, then advanced

**Ask yourself:**
- Would a new developer understand this?
- Did I explain the "why" not just the "how"?
- Are there examples for each concept?

## CI/CD Integration
See `ci_cd.md` for auto-deployment workflow

## Documentation Mindset
**You're not just documenting** - you're teaching.
**Every README** should get someone running in minutes.
**Every guide** should prevent a support question.
**Think:** "What would I want to know?"

---
*Great docs make great developers. Write with empathy.*
