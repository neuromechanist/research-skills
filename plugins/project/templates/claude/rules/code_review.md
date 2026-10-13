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

### Workflow (at most two rounds, then merge)
**No technical debt carried forward, and no review loops.** Full procedure: the `project:pr-review-toolkit` skill's `references/review-convergence.md`.
1. Create PR with `gh pr create`; start review while CI runs
2. Round 1: one review panel on the whole diff
3. Give every finding one outcome: fix (including suggestions), reject with a one-line reason, or follow-up issue for code the PR did not touch
4. Commit fixes on the PR branch and push once. A large fix (>150 non-test lines, public contract change, or new approach) goes in a fix PR whose base is the PR branch
5. Round 2 only if round 1 was substantial (accepted Critical, large fix, or auth/crypto/data-integrity/concurrency change): one reviewer, fix diff only
6. Fix round-2 findings directly; no third round. Merge when CI is green

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
*No technical debt carried forward. Two review rounds at most, then merge.*
