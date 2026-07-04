---
name: epic-dev
description: Execute the project epic development workflow for Codex. Use when the user asks for "epic dev", "epic-dev", "/epic-dev", "run the epic workflow", "create an epic", "resume the epic", "--resume", "--next-phase", "--finalize", phased feature delivery, sprint phases, GitHub sub-issues, or git worktrees for multi-phase implementation.
---

# Epic Development Workflow

Codex entrypoint for the same phased epic workflow exposed to Claude Code as
`/epic-dev`. Use `workflow-reference` for command snippets, state shape, and
variation details, then follow this procedure as the execution contract.

## Operating Rules

- Execute repository detection, GitHub lookups, worktree setup, tests, commits, PR creation, and cleanup directly when prerequisites are valid.
- Ask before strategic points only: epic plan approval, per-phase implementation plan approval, critical review decisions, and final epic merge.
- Use absolute paths in shell commands. Do not rely on a previous `cd`.
- Track progress with the active planning tool when available.
- Do not use `codex/` branch prefixes. Prefer `feature/issue-{N}-...`, `patch/...`, or `chore/...` per project rules.
- Do not use emojis in issues, PRs, commits, or generated state.

## Phase 0: Repository Detection

1. Run `project-detect-repo-config` from the target repository.
2. Validate required values before continuing:
   - `INTEGRATION_BRANCH`
   - `REPO_ROOT`
   - `CURRENT_BRANCH`
3. Stop and report the exact error if `ERROR` is set or required values are empty.
4. Validate GitHub CLI access. If `HAS_GH=false` or `GH_ERROR` is set, tell the user what to fix and stop.
5. If `HAS_GH_SUBISSUE=false`, install `gh-sub-issue` with `gh extension install agbiotech/gh-sub-issue` after normal approval rules for networked commands.
6. Read existing state from `.claude/epic.local.md` if present. New Codex runs may continue using that file for compatibility with the Claude command.

## Mode Parsing

Interpret the user request:

| Input | Mode | Action |
| --- | --- | --- |
| `--resume` | Resume | Read state, find the current incomplete phase, and continue. |
| `--next-phase` | Next phase | Read state, find the next pending phase, and start it. |
| `--finalize` | Finalize | Skip to the final epic PR and cleanup. |
| Any other text | New epic | Treat the text as the epic description. |
| Empty request | New epic | Ask for the epic description. |

For resume modes, validate state fields before acting: `epic_issue`,
`epic_branch`, `integration_branch`, `phases`, and `current_phase`.

## Phase 1: Epic Setup

1. Gather the epic description and phase breakdown. Suggest phases when the user has not provided them, using the sizing rule in `workflow-reference` (one phase = one independently reviewable and testable PR, roughly one subsystem or up to ~500 net changed lines; if two candidate phases can only be tested together, they are one phase). If the description contains only one such unit, use the single-phase shortcut.
2. Present the plan for confirmation:

   ```text
   Epic: {title}
   Integration branch: {INTEGRATION_BRANCH}
   Epic branch: feature/issue-{N}-epic-{slug}

   Phases:
   1. {phase 1 title}
   2. {phase 2 title}

   Proceed?
   ```

3. After confirmation, create the epic issue, phase sub-issues, and links:
   - `gh issue create --title "Epic: {title}" --label "feature"`
   - `gh issue create --title "Phase {X}: {title}" --label "feature"`
   - `gh sub-issue add {epic_issue} --sub-issue-number {phase_issue}`
4. Create the epic worktree from the integration branch unless this is a single-phase feature.
5. Write `.claude/epic.local.md` using the format in `workflow-reference`.
6. Ensure `.claude/*.local.md` is ignored without overwriting existing `.gitignore` customizations.

For a single-phase feature, skip the epic worktree and sub-issues. Create one
feature branch from the integration branch and target the integration branch
directly.

## Phase 2: Sprint Execution

For each phase, starting from the current state:

1. Create or reuse the phase worktree from the epic branch.
2. Mark the phase `in_progress`.
3. Build an implementation plan scoped only to this phase and ask for approval.
4. Implement in the phase worktree using absolute paths.
5. Add focused tests for changed behavior and run the relevant verification.
6. Commit atomic changes with concise messages.
7. Push and create a PR targeting the epic branch:

   ```bash
   git -C "{phase_worktree}" push -u origin {phase_branch}
   gh pr create --base {epic_branch} --title "Phase {X}: {title}" --body "{body}"
   ```

8. Invoke `pr-review-toolkit` for the phase PR. Fix critical issues before merging unless the user explicitly chooses otherwise.
9. Squash merge the phase PR only after checks and critical review issues are resolved.
10. Update state, remove the phase worktree, and continue to the next phase.

## Phase 3: Epic Finalization

1. Create the final PR from the epic branch to the integration branch.
2. Run project tests or the best available integration verification from the epic worktree.
3. Invoke `pr-review-toolkit` on the final PR.
4. Present the final review summary and ask for merge approval.
5. Merge the final PR with a regular merge (`--merge`) to preserve per-phase history; only squash if the user explicitly asks.
6. Close the epic issue if GitHub did not close it automatically.
7. Remove the epic worktree.
8. Archive or delete the local state file after confirming the workflow is complete.

## Error Handling

- Detection failure: stop with the exact `project-detect-repo-config` error.
- Git conflict: stop, show conflicted files, and ask the user to resolve or direct the strategy.
- Test failure: report the failing command and failure summary; fix and rerun unless the user directs otherwise.
- GitHub API failure: show what was already created and ask whether to retry or abort.
- Merge failure: do not update state or clean up worktrees. Leave the phase marked `in_progress`.
- Dirty worktree cleanup: do not force-remove without explicit user approval.
- Corrupt state: show the invalid fields and ask whether to repair state or start a new epic.

## References

- `workflow-reference` skill: branch strategy, state file format, worktree commands, GitHub commands, and variation handling.
- `pr-review-toolkit` skill: phase and final PR review before merge.
