---
description: Scaffold CI/CD pipeline for the current project
argument-hint: <python|typescript|auto>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# CI/CD Setup

Set up GitHub Actions workflows, pre-commit hooks, and CI configuration for this project. Load the `project:ci-scaffolding` skill for reference.

## Setup Process

### 1. Detect Project Type
!pwd
!ls -la
!if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then echo "DETECTED: Python"; fi
!if [ -f "package.json" ]; then echo "DETECTED: TypeScript/JavaScript"; fi
!if [ -f "Cargo.toml" ]; then echo "DETECTED: Rust"; fi
!if [ -f "go.mod" ]; then echo "DETECTED: Go"; fi

### 2. Check Existing CI
!ls -la .github/workflows/ 2>/dev/null || echo "No existing workflows"
!ls -la .git/hooks/pre-commit 2>/dev/null || echo "No pre-commit hook"

### 3. Generate Workflows

Based on detected project type and `$ARGUMENTS` (if provided), create:
- Test workflow (always)
- Release workflow (if tags are used)
- Documentation workflow (if mkdocs/docs detected)
- Typo checking (always)

Use templates from the `ci-scaffolding` skill. Write to `.github/workflows/`.

### 4. Install Pre-commit Hook

If no pre-commit hook exists, install one appropriate for the project type.

### 5. Verify
!ls -la .github/workflows/ 2>/dev/null
!echo "=== Pre-commit hook ==="
!ls -la .git/hooks/pre-commit 2>/dev/null || echo "No pre-commit hook"
