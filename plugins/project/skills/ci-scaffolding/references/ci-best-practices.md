# CI/CD Best Practices

## Caching

### Python (uv)
```yaml
- uses: astral-sh/setup-uv@v5
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
- uses: actions/setup-go@v5
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
- uses: actions/checkout@v4
# Use:
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
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
  - uses: actions/checkout@v4
    with:
      ref: ${{ github.event.pull_request.head.sha }}  # Runs untrusted code with write access
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
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: |
      coverage.xml
      test-results/
    retention-days: 7
```
