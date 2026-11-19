---
name: pr-review-toolkit
description: "Review pull requests and recent code changes across specialized lenses: general code quality, tests, error handling and silent failures, comments and docs, type design, simplification, and seam (integration) review. Use when the user asks to review a PR, review recent changes, check tests, check error handling, check comments, analyze types, simplify/refine an implementation, run \"review-pr\", before merging phase PRs in the epic-dev workflow, or for a seam or integration review: before merging a finished epic branch, before promoting dev to main, checking that an epic's goals are met, checking the changelog against what landed, or asking whether anything fell between the seams."
---

# PR Review Toolkit

Portable PR review skill adapted for the project plugin.
The review lenses track Anthropic's upstream `pr-review-toolkit` plugin (see Attribution);
this implementation keeps the procedure and rubrics in `references/` so Codex, Claude Code, and Copilot use the same source of truth.

## Review Lenses

- `code`: project rules, bugs, contracts, maintainability, security, and performance.
- `tests`: behavioral coverage, edge cases, negative paths, and brittle tests.
- `errors`: silent failures, broad catches, hidden fallbacks, and unhelpful user-facing errors.
- `comments`: comment accuracy, stale documentation, redundant comments, and missing rationale.
- `types`: invariants, validation boundaries, encapsulation, and illegal states.
- `simplify`: clarity and refactoring opportunities while preserving behavior.
- `seam`: integration review across already-reviewed PRs, for an epic branch before it merges or a `dev` to `main` promotion: goals met end to end, changelog and version truth, and work that fell between PRs. Procedure in `references/seam-review.md`.
- `all`: all applicable per-PR lenses (everything except `seam`). This is the default.

## Dispatch

Prefer a fresh-context reviewer when the current tool supports subagents. The
reviewer must read `references/review-procedure.md` and
`references/review-rubrics.md` before producing findings.

For Codex, use `references/review-panel-protocol.md` to select the bounded
native-subagent panel before falling back. The default panel is three Luna/max
reviewers grouped by risk; it is not a six-agent lens swarm.

A `seam` review never uses the panel on any surface: dispatch one integration-scoped reviewer (the same agent, with lens `seam` and the seam inputs) that also reads `references/seam-review.md`.

- **Claude Code:** run `Agent(subagent_type: "project:pr-review-toolkit", ...)` if the bundled agent is available; otherwise follow the fallback branch.
- **Codex CLI:** invoke the `project-preflight` skill's bundled `<project-plugin-root>/scripts/project-preflight --format json` executable by absolute path first (`<project-plugin-root>` is the parent of the `skills/` directory that contains this skill); plugin helpers are not on `PATH`. When the scope is `all` (default) or the caller requests a pre-merge review, `native_agent_status=available`, and no `single`/`inline` opt-out is present, dispatch the bounded panel in `references/review-panel-protocol.md` through the current native subagent surface. Use `gpt-6-luna` at `max` effort by default, cap the panel at three reviewers, require structured accounting, synthesize and verify findings, and close completed agents. If native subagents are unavailable, or the caller selects a single/inline review, use the existing inline procedure. The copied `agents/templates/pr-review-toolkit.toml` remains an opt-in configured-agent path when the current Codex surface lacks direct native dispatch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` reviewer in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents. If running outside a plugin install, copy `agents/templates/pr-review-toolkit.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback:** run the review inline in the current context after reading both reference files. This is the portable default path when preflight reports no native subagents or the caller opts out.

## Inputs To Collect

- Scope: PR number, branch range, staged changes, unstaged changes, or explicit files.
- Lens selection: one or more of `code`, `tests`, `errors`, `comments`, `types`, `simplify`, `seam`, or `all`.
- Seam inputs (lens `seam` only): mode `epic` (epic issue number and epic branch) or `promotion` (base and head refs, such as `main` and `dev`, plus the last promotion tag when one exists); for a round-2 seam `delta`, pass the round-1 report, each finding's outcome, and the round-1 head commit; see `references/seam-review.md`.
- Mode: advisory review by default; `pre-merge` selects the bounded panel when available; `delta` is the round-2 review of fix commits only (one reviewer); `single` and `inline` opt out; edit mode is allowed only when the user explicitly asks to simplify/refine or implement review fixes.
- Round: a review that gates a merge is round 1 (full) or round 2 (delta). There is no round 3 unless the user asks.
- Overrides: user-supplied model, effort, panel size, lens grouping, or fallback choice always wins over defaults.

## Required Workflow

1. Read `references/review-procedure.md`.
2. Read `references/review-rubrics.md`.
3. For lens `seam`, read `references/seam-review.md`; its scope discovery replaces step 7.
4. For Codex automatic dispatch, read `references/review-panel-protocol.md` and run the preflight gate before choosing panel versus fallback.
5. When the review gates a merge, read `references/review-convergence.md`: it decides whether round 2 runs, where fixes go, and when to merge.
6. Inspect the local project rules before generic preferences: nearest `AGENTS.md`, `CLAUDE.md`, `.rules/`, and relevant framework guidance.
7. Determine the diff scope with `git status`, `git diff`, `git diff --cached`, `gh pr view`, or `gh pr diff` as appropriate. For `delta`, the scope is the fix diff only.
8. Select applicable lenses. Use `code` for every review unless the user explicitly excludes it.
9. If a panel ran, account for every reviewer and synthesize/deduplicate findings; independently verify load-bearing claims and close completed one-off agents.
10. Report findings first, ordered by severity, with concrete file and line references.
11. If no actionable findings exist, say so clearly and list any residual test gaps or verification limits.

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

**Strengths** (optional)
- ...
```

Report only findings that pass the confidence filter in `references/review-rubrics.md`.
A `seam` review adds the verdict and goal traceability sections from `references/seam-review.md`.

For `simplify` in edit mode, make the smallest behavior-preserving patch, run the
relevant tests or checks, and summarize what changed.

## Attribution

Lens content is adapted from Anthropic's `pr-review-toolkit` plugin, version 1.0.1, in `anthropics/claude-plugins-official/plugins/pr-review-toolkit` (last upstream change 2026-10-26, synced 2026-11-19), which is licensed under the Apache License 2.0.
Its six agents (`code-reviewer`, `pr-test-analyzer`, `silent-failure-hunter`, `comment-analyzer`, `type-design-analyzer`, `code-simplifier`) map to the `code`, `tests`, `errors`, `comments`, `types`, and `simplify` lenses in `references/review-rubrics.md`.
This project skill paraphrases and reorganizes that guidance for cross-agent use rather than copying it verbatim; the `seam` lens, the Codex panel, and the convergence rules are original to this project.
When resyncing, diff the upstream agent files against the rubrics and update the version and date here.
