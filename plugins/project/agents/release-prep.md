---
name: release-prep
description: "Use this agent to autonomously prepare a project release by running pre-release checks, validating CI, checking test coverage, and verifying changelog. Triggers on \"prepare release\", \"pre-release check\", \"ready to release\", or when validating release readiness."
version: 0.2.0
model: sonnet
tools: Bash, Read, Glob, Grep
color: green
---

# Release Preparation Agent

Autonomously validate that a project is ready for release by running a comprehensive checklist.

## Procedure

### 1. Identify Version and Project Type

Read version from config files (`pyproject.toml`, `package.json`, `Cargo.toml`). Identify the project stack.

### 2. Run Pre-release Checklist

#### Tests
```bash
# Python
uv run pytest --tb=short 2>&1 | tail -20

# JavaScript
bun test 2>&1 | tail -20
```

#### Lint
```bash
# Python
uv run ruff check . 2>&1 | tail -10

# JavaScript
bunx biome check . 2>&1 | tail -10
```

#### Coverage
```bash
# Python
uv run pytest --cov --cov-report=term-missing 2>&1 | tail -20
```

#### Uncommitted Changes
```bash
git status --short
git diff --stat
```

#### CI Status
```bash
gh run list --limit 5
```

#### Changelog/Release Notes
Check if CHANGELOG.md exists and has an entry for the upcoming version.

#### License
Check LICENSE file exists.

### 3. Generate Report

```
## Release Readiness Report

Version: X.Y.Z
Branch: main
Last CI run: passing/failing

### Checklist
- [x] All tests passing (N tests)
- [x] Lint clean
- [x] Coverage: XX%
- [ ] CHANGELOG.md updated for vX.Y.Z
- [x] No uncommitted changes
- [x] CI green on latest commit
- [x] LICENSE file present

### Blockers
1. CHANGELOG.md missing entry for vX.Y.Z

### Ready to Release: NO (1 blocker)
```
