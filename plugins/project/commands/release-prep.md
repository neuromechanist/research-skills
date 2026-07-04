---
description: Prepare a project release with version bump, changelog, and validation
argument-hint: <version> or --patch or --minor or --major
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Release Preparation

Prepare a project release by running pre-release checks, bumping the version, and creating the release tag.

## Process

### 1. Detect Current Version
!if [ -f "pyproject.toml" ]; then grep -E '^version\s*=' pyproject.toml; fi
!if [ -f "package.json" ]; then grep '"version"' package.json; fi
!if [ -f "Cargo.toml" ]; then grep -E '^version\s*=' Cargo.toml | head -1; fi

### 2. Determine New Version
Parse `$ARGUMENTS` to determine version bump:
- `--patch`: increment patch (0.1.0 -> 0.1.1)
- `--minor`: increment minor (0.1.0 -> 0.2.0)
- `--major`: increment major (0.1.0 -> 1.0.0)
- Explicit version: use as-is (e.g., `1.2.3`)

### 3. Pre-release Checks
!echo "=== Running tests ==="
!if [ -f "pyproject.toml" ]; then uv run pytest 2>&1 | tail -5; fi
!if [ -f "package.json" ]; then bun test 2>&1 | tail -5; fi

!echo "=== Checking for uncommitted changes ==="
!git status --short

!echo "=== Checking CI status ==="
!gh run list --limit 3

Before proceeding: if a security-audit or dependency-auditor report exists
for this release cycle, any Critical finding in it is a release blocker; stop
and report it instead of bumping the version.

### 4. Version Bump
Update version in the appropriate config file(s). Commit the version bump.

### 5. Create Tag
After confirming with the user:
```bash
git tag -a "v{version}" -m "Release v{version}"
```

### 6. Summary
Report what was done and what the user needs to do next (push tag to trigger release workflow).
