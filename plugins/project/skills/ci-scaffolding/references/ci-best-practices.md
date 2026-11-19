# CI/CD Best Practices

## Caching

### Python (uv)
```yaml
- uses: astral-sh/setup-uv@v10.3.2
  with:
    enable-cache: true
```

### Bun
```yaml
- uses: oven-sh/setup-bun@v2
  with:
    bun-version: latest
# Bun caches automatically in ~/.bun/install/cache
```

### Go
```yaml
- uses: actions/setup-go@v7
  with:
    go-version: '1.22'
    cache: true
```

## Matrix Builds

Use matrix strategy for multi-version testing:

```yaml
strategy:
  fail-fast: false  # Don't cancel other jobs if one fails
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.11", "3.12"]
```

Only run expensive operations (coverage upload, artifact creation) on one matrix combination:
```yaml
- if: matrix.python-version == '3.12' && matrix.os == 'ubuntu-latest'
  run: upload-coverage
```

## Secrets Management

- Store secrets in GitHub Settings > Secrets and Variables > Actions
- Reference as `${{ secrets.SECRET_NAME }}`
- Never echo secrets or use in `if` conditions that could leak values
- Use `GITHUB_TOKEN` for repository operations (auto-provided)

## Security Hardening

### Pin third-party actions to SHA
```yaml
# Instead of:
- uses: actions/checkout@v7
# Use:
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
```

### Minimal permissions
```yaml
permissions:
  contents: read
  # Only add write permissions when needed
```

### Avoid pull_request_target with checkout
```yaml
# DANGEROUS - don't do this:
on: pull_request_target
steps:
  - uses: actions/checkout@v7
    with:
      ref: ${{ github.event.pull_request.head.sha }}  # Runs untrusted code with write access
```

## Scoped required checks (gate job)

Branch protection waits forever on a required check whose workflow was skipped by `paths`, `paths-ignore`, or `[skip ci]`.
A job skipped by `if:` reports success instead.
So for required checks, always run the workflow, skip expensive jobs by condition, and require only the gate:

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    outputs:
      code: ${{ steps.filter.outputs.code }}
    steps:
      - uses: actions/checkout@v7
      - uses: dorny/paths-filter@v4
        id: filter
        with:
          filters: |
            code: ['src/**', 'tests/**', 'pyproject.toml', 'package.json', '.github/workflows/**']
  test:
    needs: changes
    if: needs.changes.outputs.code == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v7
      # lint, typecheck, test
  gate:
    needs: [changes, test]
    if: always()
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - run: |
          [[ "${{ contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled') }}" == "false" ]]
```

## Conditional Jobs

```yaml
jobs:
  docs:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    # Only deploy docs on push to main
```

## Artifact Upload

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: test-results
    path: |
      coverage.xml
      test-results/
    retention-days: 7
```
