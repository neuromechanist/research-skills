# Code Review Standards

## PR Review Toolkit
When the `pr-review-toolkit` plugin is available, use it after creating PRs to catch issues before merge.

### Available Agents
- `code-reviewer` - Review for style, best practices, project guidelines
- `silent-failure-hunter` - Find inadequate error handling, silent failures
- `code-simplifier` - Simplify code while preserving functionality
- `comment-analyzer` - Check comment accuracy and maintainability
- `pr-test-analyzer` - Review test coverage quality
- `type-design-analyzer` - Analyze type design and invariants

### Workflow
**No technical debt carried forward.** Address all findings, not just critical ones.
1. Create PR with `gh pr create`
2. Run code review agents on the changes (all agents in parallel)
3. Address ALL findings: critical, important, suggestions, and nice-to-haves
4. Only skip genuine false positives or intentionally different design choices
5. Document skipped findings with clear reasoning (false positive / intended behavior)

## Manual Code Review Checklist

### Before Committing
- [ ] Code compiles/runs without warnings
- [ ] Tests pass (real tests, no mocks)
- [ ] No debug code left (print statements, TODO hacks)
- [ ] No sensitive data in code or logs

### Logic & Safety
- [ ] Error cases handled with specific exceptions
- [ ] No silent failures (empty catch blocks, bare except)
- [ ] Resource cleanup (files, connections, context managers)
- [ ] Input validation at system boundaries

### Code Quality
- [ ] Functions do one thing
- [ ] Clear naming (no abbreviations)
- [ ] No magic numbers (use constants)
- [ ] No premature abstraction (three uses before extracting)

### Never Do This
- [ ] No `except Exception: pass` or empty catch blocks
- [ ] No `# type: ignore` without explanation
- [ ] No commented-out code (delete it; git has history)
- [ ] No `TODO` without a linked issue
- [ ] No backward-compatibility shims; replace, don't deprecate

## Review Comments
When leaving review comments:
- Be specific about the issue
- Suggest a fix when possible
- Distinguish blocking vs. non-blocking issues
- Reference documentation or examples

---
*No technical debt carried forward. Review early, review often.*
