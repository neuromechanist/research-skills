# Rules Directory Guide

The `.rules/` directory contains detailed development standards as individual markdown files. Each file covers one domain. Include only the rules relevant to the project.

## Rule Files

### testing.md
**Always include.** The NO MOCK testing policy is a core principle. Covers real test structure, sample data directories, Docker for test databases, and framework recommendations (pytest for Python, vitest/jest for JS).

### git.md
**Always include.** Atomic commits, branch strategy, squash merging for features, rebase to update branches. References `gh issue develop` for branch creation.

### code_review.md
**Always include.** PR review process using pr-review-toolkit agents (code-reviewer, silent-failure-hunter, code-simplifier, comment-analyzer, pr-test-analyzer, type-design-analyzer). Checklist: compiles, tests pass, no debug code, error handling, resources cleaned up.

### python.md
**Include for Python projects.** UV for all package management, ruff for formatting and linting, ty for type checking. Line length 88, type hints for all public functions, pathlib.Path instead of os.path, context managers for resource management.

### documentation.md
**Include when the project has or plans documentation.** MkDocs with material theme. "Write for your future self" philosophy. Every README gets someone running in <5 minutes. Examples over explanations, progressive disclosure.

### ci_cd.md
**Include when using GitHub Actions.** Three workflow templates: test.yml, docs.yml, release.yml. Fail-fast pipeline: lint, type check, test, build, deploy. Matrix testing, cache management with setup-uv/setup-bun.

### self_improve.md
**Include for long-running projects.** Learning and rule evolution process. Extract patterns used 3+ times into rules. Mine failures from scratch_history.md. Mine successes from research.md.

### serena_mcp.md
**Include when Serena MCP is available.** Efficient code exploration with symbolic tools. `get_symbols_overview` -> `find_symbol` -> read bodies. Prefer symbolic editing over line-based edits.

## Customization Guidelines

After copying the rules directory:
1. Read each rule file and assess relevance to the project
2. Remove rules that do not apply (e.g., remove python.md for a pure JS project)
3. Keep testing.md, git.md, and code_review.md for all projects
4. Add project-specific rules as new .md files when needed
5. Update the AGENTS.md "[REFERENCE] Rules Directory" section to match the actual rules present
