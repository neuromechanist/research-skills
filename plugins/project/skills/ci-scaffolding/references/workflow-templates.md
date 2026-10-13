# CI/CD Workflow Templates

Complete workflow file templates with all configuration options.

## Python Test Workflow (Full)
```yaml
name: Tests
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
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    needs: lint
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --dev
      - run: uv run pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          file: coverage.xml
```

## TypeScript Test Workflow (Full)
```yaml
name: Tests
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
    runs-on: ubuntu-latest
    timeout-minutes: 20
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun test
```

## Release Workflow (Full)
```yaml
name: Release
on:
  push:
    tags: ['v*']

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          draft: false
          prerelease: ${{ contains(github.ref, '-rc') || contains(github.ref, '-beta') }}
```

## Documentation Workflow (Full)
```yaml
name: Documentation
on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'src/**'

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --group docs
      - run: uv run mkdocs gh-deploy --force
```

## Go Test Workflow
```yaml
name: Tests
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
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go vet ./...
      - run: go test -race -coverprofile=coverage.out ./...
```

## Typos Workflow (unfiltered)

Typos reads docs, so it runs in its own workflow without path filters.

```yaml
name: Typos
on:
  pull_request:
  push:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  typos:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: crate-ci/typos@v1
```
