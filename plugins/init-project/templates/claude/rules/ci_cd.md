# CI/CD Workflow Standards

## Purpose: Automated Quality Gates
**Why CI/CD?** Catch issues before users do.
**Think:** Every pipeline failure is a production bug prevented.
**Goal:** Fast feedback, high confidence, zero surprises.

## Essential Workflows

### 1. Testing (`test.yml`)
**Triggers:** `on: [push, pull_request]` to main branches
**Jobs (in order):**
- **Lint:** `ruff check` / `biome check` (fails fast)
- **Type Check:** `ty` / `tsc --noEmit`
- **Test:** Real tests only, matrix for versions
- **Build:** Verify compilation if applicable
- **Coverage:** Optional reporting to Codecov

### 2. Documentation (`docs.yml`)
**Triggers:** `on: push: branches: [main]`
**Jobs:** Build with MkDocs -> Deploy to GitHub Pages

### 3. Release (`release.yml`)
**Triggers:** Tag creation or manual
**Jobs:** Build -> Create release -> Publish packages

## Python Example (UV)
```yaml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - run: uv sync --dev
    - run: uv run ruff check .
    - run: uv run ruff format --check .

  test:
    needs: lint
    runs-on: ubuntu-latest
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
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: oven-sh/setup-bun@v2
    - run: bun install
    - run: bun run biome check .

  test:
    needs: lint
    runs-on: ubuntu-latest
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
