---
name: ci-scaffolding
description: "This skill should be used when the user says \"set up CI\", \"create GitHub Actions\", \"scaffold CI pipeline\", \"add CI/CD\", \"configure continuous integration\", \"create test workflow\", \"create release workflow\", \"add pre-commit hooks\", \"set up linting pipeline\", \"configure ruff in CI\", \"configure biome in CI\", \"add typo checking\", or wants to add, update, or customize CI/CD pipelines for their project. For initial project setup including basic CI, see init-project. Use ci-scaffolding for adding or customizing CI/CD in existing projects."
version: 0.1.0
---

# CI/CD Scaffolding

Generate and configure CI/CD pipelines following project conventions. Supports Python (ruff + pytest + coverage) and TypeScript/JavaScript (biome + bun test) stacks, with templates for testing, documentation, and release workflows.

## When to Use

- Adding CI/CD to a new project
- Updating existing GitHub Actions workflows
- Setting up pre-commit hooks for linting
- Configuring coverage reporting
- Adding release automation (tag-based)

## Pipeline Templates

### Python Project Pipeline

Standard Python CI with three stages:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run ruff check --fix --unsafe-fixes .
      - run: uv run ruff format --check .
      - run: uv run pytest --cov --cov-report=xml
```

Key conventions:
- Use `astral-sh/setup-uv` (not pip)
- Ruff for both linting and formatting
- pytest with coverage (XML report for CI integration)
- No mocks in test configuration

### TypeScript/JavaScript Project Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun run biome check .
      - run: bun test
```

Key conventions:
- Use `oven-sh/setup-bun` (not npm/node)
- Biome for linting and formatting
- bun test for testing

### Release Workflow

Tag-based release automation:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
```

### Documentation Workflow

MkDocs deployment to GitHub Pages:

```yaml
# .github/workflows/docs.yml
name: Docs
on:
  push:
    branches: [main]
permissions:
  contents: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --group docs
      - run: uv run mkdocs gh-deploy --force
```

### Typo Checking

Add typo checking to any project:

```yaml
# In existing test.yml or standalone
- uses: crate-ci/typos@master
```

## Pre-commit Hook Setup

### Python (ruff)

```bash
#!/bin/sh
# .git/hooks/pre-commit
STAGED=$(git diff --cached --name-only --diff-filter=d -- '*.py')
[ -z "$STAGED" ] && exit 0
echo "$STAGED" | xargs uv run ruff check --fix --unsafe-fixes
echo "$STAGED" | xargs uv run ruff format
git add $STAGED
```

### TypeScript (biome)

```bash
#!/bin/sh
# .git/hooks/pre-commit
STAGED=$(git diff --cached --name-only --diff-filter=d -- '*.ts' '*.tsx' '*.js' '*.jsx')
[ -z "$STAGED" ] && exit 0
echo "$STAGED" | xargs bunx biome check --write
git add $STAGED
```

## Scaffolding Workflow

### Step 1: Detect project type

Scan for language markers (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`) and existing CI configuration.

### Step 2: Select pipelines

Based on detection:
- Always: test workflow
- If Python with docs: docs workflow
- If releases needed: release workflow
- If no pre-commit hook: install one

### Step 3: Generate files

Create `.github/workflows/` directory and write workflow files. Never overwrite existing workflows without asking.

### Step 4: Verify

Run `act` locally if available to validate workflows, or do a dry-run check of YAML syntax.

## Additional Resources

- Reference: [references/workflow-templates.md](references/workflow-templates.md) - Full workflow file templates with all options
- Reference: [references/ci-best-practices.md](references/ci-best-practices.md) - Caching, matrix builds, secrets management
