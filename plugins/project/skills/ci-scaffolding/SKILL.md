---
name: ci-scaffolding
description: "This skill should be used when the user says \"set up CI\", \"create GitHub Actions\", \"scaffold CI pipeline\", \"add CI/CD\", \"configure continuous integration\", \"create test workflow\", \"create release workflow\", \"add pre-commit hooks\", \"set up linting pipeline\", \"configure ruff in CI\", \"configure biome in CI\", \"add typo checking\", or wants to add, update, or customize CI/CD pipelines for their project. For initial project setup including basic CI, see init-project. Use ci-scaffolding for adding or customizing CI/CD in existing projects."
version: 0.1.1
---

# CI/CD Scaffolding

Generate and configure CI/CD pipelines following project conventions. Supports Python (ruff + pytest + coverage) and TypeScript/JavaScript (biome + bun test) stacks, with templates for testing, documentation, and release workflows.

## When to Use

- Adding CI/CD to a new project
- Updating existing GitHub Actions workflows
- Setting up pre-commit hooks for linting
- Configuring coverage reporting
- Adding release automation (tag-based)

## Triggers and scope (every workflow)

CI runs only when files it checks change, once per push.

1. Trigger on `pull_request` for any base (fix PRs and epic phase PRs need CI too) plus `push` to the integration branches. Never `on: [push, pull_request]`; it runs twice for every PR push.
2. Add `concurrency` that cancels superseded PR runs.
3. Scope each workflow to the files it reads: `paths` for docs and deploy workflows, `paths-ignore` for code workflows. Ignore only paths no job reads; if CI builds or lints the docs, keep them in that job's scope.
4. A workflow skipped by a path filter or `[skip ci]` leaves its required check pending and blocks merge. For a required check, use the always-running gate job in `references/ci-best-practices.md`, give that workflow no trigger-level `paths` or `paths-ignore`, and require only the gate.
5. Give every job `timeout-minutes` (default 20) and tests a per-test timeout; a hung job otherwise runs for 6 hours.
6. Required checks never call live external services; put those in a scheduled or non-required job.
7. One workflow per concern; never two workflows running the same tests.
8. Prefer no post-merge bot commit: bump versions inside the PR or at release. If a bot must commit after merge (version bump, file sync), push it with `[skip ci]`, alone in its push, only to the integration branch, never to a PR head. GitHub also reads the marker from a PR's head commit, so if the integration branch later heads a release PR (for example `develop` to `main`), its required checks never report; in that setup skip inside the workflow instead: a gate job detects the bot's commit and skips its steps, so the required checks still pass. A bot push needs a PAT or App token to trigger anything; `GITHUB_TOKEN` pushes trigger no workflows. A tag on a `[skip ci]` commit also skips tag-triggered workflows, so create releases with `gh release create` or a dispatch.
9. One merge deploys and publishes once per environment, from the final commit. When a bot bumps after merge, the same workflow deploys: a `bump` job, then a `deploy` job with `needs: bump` that checks out the bumped SHA. No separate push-triggered deploy runs for that branch.

```yaml
on:
  pull_request:
    paths-ignore: ['**.md', 'docs/**', '.context/**', '.memory/**']
  push:
    branches: [main, develop]
    paths-ignore: ['**.md', 'docs/**', '.context/**', '.memory/**']
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

### `[skip ci]` commits

- Add `[skip ci]` to the subject of a commit that changes only files no CI job reads (notes, `.context/`, `.memory/`, prose docs CI does not build). Exception: bot bump and sync commits per rule 8.
- GitHub reads only the head commit of a push. Never push a `[skip ci]` commit on top of untested code commits.
- GitHub matches the token anywhere in that message, body included. Never quote it in a commit message you want tested; write "skip-ci marker" instead.
- On a PR branch, use it only when `gh pr checks N --required` lists no required checks; otherwise rely on the gate job's `changes` filter.

## Pipeline Templates

### Python Project Pipeline

Standard Python CI pipeline:

```yaml
# .github/workflows/test.yml
name: Tests
# on + concurrency: copy the block from "Triggers and scope"
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run ruff check .
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
# on + concurrency: copy the block from "Triggers and scope"
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
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
    timeout-minutes: 20
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
    paths: ['docs/**', 'mkdocs.yml']
permissions:
  contents: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --group docs
      - run: uv run mkdocs gh-deploy --force
```

### Typo Checking

Add typo checking to any project:

```yaml
# In its own workflow without path filters (it reads docs)
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
Confirm every workflow has scoped triggers and `concurrency`, and that a docs-only change starts no code workflow.

## Additional Resources

- Reference: [references/workflow-templates.md](references/workflow-templates.md) - Full workflow file templates with all options
- Reference: [references/ci-best-practices.md](references/ci-best-practices.md) - Caching, matrix builds, secrets management
