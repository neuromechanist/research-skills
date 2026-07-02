---
name: pr-review-toolkit
description: "Review pull requests and recent code changes across specialized lenses: general code quality, tests, error handling and silent failures, comments and docs, type design, and simplification. Use when the user asks to review a PR, review recent changes, check tests, check error handling, check comments, analyze types, simplify/refine an implementation, run \"review-pr\", or before merging phase PRs in the epic-dev workflow."
---

# PR Review Toolkit

Portable PR review skill adapted for the project plugin. The upstream Anthropic
`pr-review-toolkit` inspired the review lenses; this implementation keeps the
procedure and rubrics in `references/` so Codex, Claude Code, and Copilot can use
the same source of truth.

## Review Lenses

- `code`: project rules, bugs, contracts, maintainability, security, and performance.
- `tests`: behavioral coverage, edge cases, negative paths, and brittle tests.
- `errors`: silent failures, broad catches, hidden fallbacks, and unhelpful user-facing errors.
- `comments`: comment accuracy, stale documentation, redundant comments, and missing rationale.
- `types`: invariants, validation boundaries, encapsulation, and illegal states.
- `simplify`: clarity and refactoring opportunities while preserving behavior.
- `all`: all applicable lenses. This is the default.

## Dispatch

Prefer a fresh-context reviewer when the current tool supports subagents. The
reviewer must read `references/review-procedure.md` and
`references/review-rubrics.md` before producing findings.

- **Claude Code:** run `Task(subagent_type: "pr-review-toolkit", ...)` if the bundled agent is available; otherwise follow the fallback branch.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex reviewer, first copy `agents/templates/pr-review-toolkit.toml` to `~/.codex/agents/` or `.codex/agents/`, then invoke that configured agent if the current Codex surface supports `/agent`. If no Codex subagent is configured or available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` reviewer in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents. If running outside a plugin install, copy `agents/templates/pr-review-toolkit.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback:** run the review inline in the current context after reading both reference files. This is the portable default path.

## Inputs To Collect

- Scope: PR number, branch range, staged changes, unstaged changes, or explicit files.
- Lens selection: one or more of `code`, `tests`, `errors`, `comments`, `types`, `simplify`, or `all`.
- Mode: advisory review by default; edit mode only when the user explicitly asks to simplify/refine or implement review fixes.

## Required Workflow

1. Read `references/review-procedure.md`.
2. Read `references/review-rubrics.md`.
3. Inspect the local project rules before generic preferences: nearest `AGENTS.md`, `CLAUDE.md`, `.rules/`, and relevant framework guidance.
4. Determine the diff scope with `git status`, `git diff`, `git diff --cached`, `gh pr view`, or `gh pr diff` as appropriate.
5. Select applicable lenses. Use `code` for every review unless the user explicitly excludes it.
6. Report findings first, ordered by severity, with concrete file and line references.
7. If no actionable findings exist, say so clearly and list any residual test gaps or verification limits.

## Output Shape

Use this structure unless the user asks for a different format:

```markdown
**Findings**
- Critical: ...
- Important: ...
- Moderate: ...

**Questions**
- ...

**Residual Risk**
- ...
```

For `simplify` in edit mode, make the smallest behavior-preserving patch, run the
relevant tests or checks, and summarize what changed.

## Attribution

Inspired by Anthropic's `pr-review-toolkit` plugin in
`anthropics/claude-code/plugins/pr-review-toolkit`. The upstream plugin README
identifies the plugin license as MIT; this project implementation is written as
an original project skill with attribution rather than a verbatim copy.
