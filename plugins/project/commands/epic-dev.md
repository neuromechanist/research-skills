---
description: Epic/sprint development workflow with git worktrees, GitHub issues, and phased delivery
argument-hint: "<epic description>" or --resume or --next-phase or --finalize
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, Task, AskUserQuestion, EnterPlanMode, ExitPlanMode, TodoWrite
---

# Epic Development Workflow

Orchestrate multi-phase feature development using git worktrees, GitHub issues with sub-issues, and phased PR delivery. Load the `project:workflow-reference` skill immediately for reference context.

## Core Principles

- **Full automation**: Execute all git, gh, and worktree commands automatically
- **Confirm only at strategic points**: epic plan, implementation plan, critical review findings, final merge
- **Use absolute paths**: Bash calls do not persist `cd`; always use full worktree paths
- **Track progress**: Use TodoWrite to track all phases and steps
- **No emojis**: Never use emojis in commits, PRs, or issues

---

## Phase 0: Repository Detection

**Goal**: Detect repo configuration and validate prerequisites.

**Actions**:
1. Run `project-detect-repo-config` and parse the output
2. **Validate all required values are present**: `INTEGRATION_BRANCH`, `REPO_ROOT`, `CURRENT_BRANCH` must be non-empty. If any are missing or if `ERROR` is set, report the error to the user and stop.
3. **Validate gh is functional**: If `HAS_GH=false` or `GH_ERROR` is set, tell the user what needs to be fixed and stop.
4. If `HAS_GH_SUBISSUE=false`, install it: `gh extension install agbiotech/gh-sub-issue`
5. Store detected values: `INTEGRATION_BRANCH`, `REPO_ROOT`, `HAS_EPIC_STATE`
6. Create initial todo list tracking all workflow phases

---

## Argument Parsing

Parse `$ARGUMENTS` to determine the mode:

| Argument | Mode | Action |
|----------|------|--------|
| `--resume` | Resume | Read `.claude/epic.local.md`, find current phase, continue |
| `--next-phase` | Next phase | Read state, find next pending phase, begin it |
| `--finalize` | Finalize | Skip to Phase 3 (final PR and cleanup) |
| Any other text | New epic | Use text as epic description |
| Empty | New epic | Ask user for epic description |

For `--resume`, `--next-phase`, and `--finalize`: read the state file at `{REPO_ROOT}/.claude/epic.local.md` and jump to the appropriate phase.

---

## Phase 1: Epic Setup

**Goal**: Create the epic issue, sub-issues, and worktree structure.

**Actions**:

1. **Gather information**:
   - If no description in `$ARGUMENTS`, ask the user what they want to build
   - Ask the user to describe the phases (or suggest a phase breakdown based on the description)

2. **Present epic plan for confirmation**:
   Display a summary:
   ```
   Epic: {title}
   Integration branch: {INTEGRATION_BRANCH}
   Epic branch: feature/issue-{N}-epic-{slug}

   Phases:
   1. {phase 1 title}
   2. {phase 2 title}
   ...

   Proceed?
   ```
   Wait for user confirmation.

3. **Execute setup** (automatic after confirmation):
   - Create epic issue: `gh issue create --title "Epic: {title}" --label "feature"`
   - For each phase:
     - Create sub-issue: `gh issue create --title "Phase {X}: {title}" --label "feature"`
     - Link: `gh sub-issue add {epic_issue} --sub-issue-number {phase_issue}`
   - Create epic worktree:
     ```bash
     PARENT=$(dirname "$REPO_ROOT")
     git worktree add "$PARENT/epic-{slug}" -b feature/issue-{N}-epic-{slug} {INTEGRATION_BRANCH}
     ```
   - Write state file to `{REPO_ROOT}/.claude/epic.local.md`
   - Ensure `.claude/*.local.md` is in `.gitignore`

4. **Single-phase shortcut**: If only one phase, skip epic worktree. Create feature branch directly from integration branch. No sub-issues needed.

---

## Phase 2: Sprint Execution

**Goal**: Implement each phase in its own worktree, PR, and merge cycle.

**For each phase** (starting from `current_phase` in state):

### Step 2.1: Setup phase worktree
```bash
PARENT=$(dirname "$REPO_ROOT")
EPIC_BRANCH=$(read from state)
git worktree add "$PARENT/{phase-slug}" -b feature/issue-{N}-phase{X}-{slug} {EPIC_BRANCH}
```
Update state: mark phase `in_progress`.

### Step 2.2: Implementation planning
- Enter plan mode using `EnterPlanMode` tool
- The plan should focus on this specific phase's scope
- Wait for user to approve the plan (this is handled by ExitPlanMode)
- After plan approval, proceed to implementation

### Step 2.3: Implementation
- Work in the phase worktree using absolute paths: `$PARENT/{phase-slug}/`
- Follow the approved plan
- Write tests (unit + integration)
- Run tests and verify they pass
- Make atomic commits with concise messages

### Step 2.4: PR and review
- Create PR targeting the epic branch:
  ```bash
  cd "$PARENT/{phase-slug}" && gh pr create --base {epic_branch} --title "Phase {X}: {title}" --body "$(cat <<'PREOF'
  ## Summary
  {brief description of what this phase implements}

  Closes #{phase_issue}
  Part of epic #{epic_issue}

  ## Test plan
  {test plan}
  PREOF
  )"
  ```
- Push branch: `git -C "$PARENT/{phase-slug}" push -u origin {phase_branch}`
- Run `/review-pr` (invoke the `pr-review-toolkit:review-pr` skill)
- If critical issues found: present them and ask user how to proceed
- If no critical issues: summarize findings briefly and proceed

### Step 2.5: Merge and cleanup
- Squash merge: run from phase worktree `gh pr merge --squash --delete-branch`
- Update state: mark phase `complete`, record PR number
- Remove worktree: `git worktree remove "$PARENT/{phase-slug}"`
- Delete local branch if still present

### Step 2.6: Next phase
- Increment `current_phase` in state
- If more phases remain, loop back to Step 2.1
- If all phases complete, proceed to Phase 3

---

## Phase 3: Epic Finalization

**Goal**: Merge the epic branch to the integration branch.

**Actions**:

1. Create final PR:
   ```bash
   cd "$PARENT/epic-{slug}" && gh pr create --base {INTEGRATION_BRANCH} --title "{epic_title}" --body "$(cat <<'PREOF'
   ## Summary
   {description of the full epic}

   Closes #{epic_issue}

   ## Phases completed
   {numbered list of phases with PR links}

   ## Test plan
   - All phase PRs individually reviewed and tested
   - Integration tests passing on epic branch
   PREOF
   )"
   ```

2. Push epic branch: `git -C "$PARENT/epic-{slug}" push -u origin {epic_branch}`

3. Run `/review-pr` on the full epic PR

4. **Confirm**: Present review summary and ask user to approve final merge

5. Squash merge: `gh pr merge --squash --delete-branch`

6. Close epic issue if not auto-closed: `gh issue close {epic_issue}`

7. Clean up epic worktree: `git worktree remove "$PARENT/epic-{slug}"`

8. Archive or delete state file

---

## Phase 4: Summary

**Goal**: Report what was accomplished.

**Actions**:
1. Mark all todos complete
2. Present summary:
   - Epic issue link
   - All phase PRs (with links)
   - Final PR link
   - Files modified across all phases
   - Total issues created and closed
3. Suggest next steps if any

---

## Error Handling

- **Detection script failure**: If `project-detect-repo-config` fails or returns `ERROR`, report the exact error and stop. Do not proceed with empty configuration values.
- **Git conflicts**: Stop and present the conflict. Ask user to resolve manually, then continue.
- **Test failures**: Present test output. Ask user whether to fix and retry or skip.
- **PR check failures**: Wait for CI, present results. If failing, ask user how to proceed.
- **GitHub API failures**: If `gh issue create` or `gh pr create` fails, report the exact error, show which issues/PRs were already created, and ask the user whether to retry or abort. Never proceed with empty issue/PR numbers.
- **Missing gh sub-issue**: Install automatically: `gh extension install agbiotech/gh-sub-issue`
- **Merge failures**: If `gh pr merge` fails for any reason (CI, review, conflicts), do NOT proceed to worktree cleanup or state update. Report the error and wait for user resolution. The state file should remain at `in_progress` for the current phase.
- **Worktree already exists**: Detect and reuse existing worktree instead of creating new one.
- **Worktree cleanup failures**: If `git worktree remove` fails (dirty tree, locked), warn the user and suggest `git worktree remove --force` only after confirming no uncommitted work.
- **State file missing on resume**: Report error, ask user to start fresh or provide details.
- **State file corruption**: After reading `.claude/epic.local.md`, validate that required fields (`epic_issue`, `epic_branch`, `integration_branch`, `phases`, `current_phase`) are present and have valid values. If validation fails, show what was read and ask the user to fix or start fresh.
