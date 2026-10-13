# CI/CD Workflow Standards

## Purpose: Automated Quality Gates
**Why CI/CD?** Catch issues before users do.
**Think:** Every pipeline failure is a production bug prevented.
**Goal:** Fast feedback, high confidence, zero surprises.

## Triggers and Scope (avoid wasted runs)
- **Trigger:** `pull_request` (any base) plus `push` to `main`/`develop` only. Never `on: [push, pull_request]` (double runs on every PR push).
- **Concurrency:** cancel superseded PR runs (`group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}`).
- **Scope:** `paths-ignore` docs and notes for code workflows; `paths` for docs and deploy workflows.
- **Required checks:** a skipped workflow leaves a required check pending; use an unfiltered workflow with a gate job (see the ci-scaffolding skill).
- **`[skip ci]`:** in the subject of commits that touch only files no CI job reads (see git rules).
- **Timeouts:** every job sets `timeout-minutes` (default 20); a hung job otherwise runs 6 hours.
- **No live services in required checks; one workflow per concern; bot version-bump commits carry `[skip ci]`.**

## Essential Workflows

### 1. Testing (`test.yml`)
**Triggers:** `pull_request` and `push` to main branches, docs paths ignored
**Jobs (in order):**
- **Lint:** `ruff check` / `biome check` (fails fast)
- **Type Check:** `ty` / `tsc --noEmit`
- **Test:** Real tests only, matrix for versions
- **Build:** Verify compilation if applicable
- **Coverage:** Optional reporting to Codecov

### 2. Documentation (`docs.yml`)
**Triggers:** `push` to `main` with `paths: [docs/**, mkdocs.yml]`
**Jobs:** Build with MkDocs -> Deploy to GitHub Pages

### 3. Release (`release.yml`)
**Triggers:** Tag creation or manual
**Jobs:** Build -> Create release -> Publish packages

## Python Example (UV)
```yaml
name: CI
on:
  pull_request:
    paths-ignore: ['**.md', 'docs/**', '.context/**', '.memory/**']
  push:
    branches: [main, develop]
    paths-ignore: ['**.md', 'docs/**', '.context/**', '.memory/**']
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv sync --dev
    - run: uv run ruff check .
    - run: uv run ruff format --check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 20
    strategy:
      matrix: { python-version: ['3.11', '3.12', '3.13'] }
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
      with: { python-version: '${{ matrix.python-version }}' }
    - run: uv sync --dev
    - run: uv run pytest --cov=src
```

## JavaScript/TypeScript Example (Bun)
```yaml
name: CI
on:
  pull_request:
    paths-ignore: ['**.md', 'docs/**', '.context/**', '.memory/**']
  push:
    branches: [main, develop]
    paths-ignore: ['**.md', 'docs/**', '.context/**', '.memory/**']
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
    - uses: actions/checkout@v4
    - uses: oven-sh/setup-bun@v2
    - run: bun install
    - run: bun run biome check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
    - uses: actions/checkout@v4
    - uses: oven-sh/setup-bun@v2
    - run: bun install
    - run: bun test
```

## Key Practices (Think About Pipeline Flow)
- **Pin versions:** `actions/checkout@v4` (reproducibility)
- **Cache deps:** UV and Bun both have built-in caching; use `setup-uv` and `setup-bun` actions
- **Fail fast:** Lint -> Type Check -> Test -> Build -> Deploy (catch cheap failures first)
- **Matrix testing:** Test all supported versions
- **Secrets:** Never commit credentials; use GitHub Secrets
- **Conditional:** Deploy only from protected branches

## Pipeline Philosophy
**Fast feedback:** Developers should know in <5 min
**Clear failures:** Error messages should guide fixes
**No surprises:** If it passes CI, it works in production

**Ask yourself:**
- Will this catch real issues?
- Is the feedback loop fast enough?
- Are we testing what actually matters?
