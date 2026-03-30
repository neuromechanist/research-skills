---
name: workflow-reference
description: This skill should be used when executing the epic-dev workflow, creating epic branches, managing sprint phases, working with git worktrees for phased feature development, or when the user mentions "epic workflow", "sprint phases", "phased development", or "git worktree workflow".
version: 0.1.0
---

# Epic/Sprint Development Workflow Reference

Procedural reference for multi-phase feature development using git worktrees, GitHub issues with sub-issues, and phased PR delivery.

## Branch Strategy Decision Tree

Determine the integration branch and branching model:

1. **Integration branch detection:**
   - If `develop` branch exists (local or remote): integration branch = `develop`
   - Otherwise: integration branch = default branch (`main` or `master`)

2. **Epic branch:**
   - Named: `feature/issue-{N}-epic-{short-name}`
   - Created from: integration branch
   - Purpose: collects all phase PRs before final merge to integration

3. **Phase branches:**
   - Named: `feature/issue-{N}-phase{X}-{short-name}`
   - Created from: epic branch
   - Merged to: epic branch (squash merge)

4. **Single-phase shortcut:**
   - If only one phase, skip the epic branch layer
   - Create feature branch directly from integration branch
   - Merge directly to integration branch

## State File Format

Persistent state stored in `.claude/epic.local.md` (gitignored via `.claude/*.local.md`):

```yaml
---
epic_issue: 132
epic_title: "Feature: Community Dashboard"
integration_branch: develop
epic_branch: feature/issue-132-epic-dashboard
worktree_base: "../epic-dashboard"
phases:
  - number: 1
    title: "Backend metrics collection"
    issue: 133
    branch: "feature/issue-133-phase1-metrics"
    status: complete       # pending | in_progress | complete
    pr: 135
  - number: 2
    title: "Dashboard frontend"
    issue: 134
    branch: "feature/issue-134-phase2-frontend"
    status: pending
    pr: null
current_phase: 2
created_at: "2026-02-02T12:00:00Z"
---

## Notes
Running notes about the epic, decisions made, blockers encountered.
```

Status transitions: `pending` -> `in_progress` -> `complete`

## Git Worktree Operations

All worktree paths use absolute paths (Bash calls do not persist `cd`).

**Create epic worktree:**
```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
PARENT=$(dirname "$REPO_ROOT")
git worktree add "$PARENT/epic-{short-name}" -b feature/issue-{N}-epic-{short-name} {integration_branch}
```

**Create phase worktree from epic branch:**
```bash
git worktree add "$PARENT/{short-name}-phase{X}" -b feature/issue-{N}-phase{X}-{short-name} feature/issue-{EPIC}-epic-{epic-name}
```

**Clean up worktree after merge:**
```bash
git worktree remove "$PARENT/{worktree-name}"
git branch -d feature/issue-{N}-phase{X}-{short-name}
```

**Handle existing worktree:** Before creating, check:
```bash
git worktree list | grep -q "{branch-name}" && echo "EXISTS" || echo "NEW"
```

## GitHub Operations

**Create epic issue:**
```bash
gh issue create --title "Epic: {description}" --label "feature" --body "{body with phase breakdown}"
```

**Create phase sub-issue and link:**
```bash
PHASE_ISSUE=$(gh issue create --title "Phase {X}: {title}" --label "feature" --body "Part of #{epic_issue}" | grep -o '[0-9]*$')
gh sub-issue add {epic_issue} --sub-issue-number $PHASE_ISSUE
```

**Create PR to epic branch:**
```bash
gh pr create --base {epic_branch} --title "Phase {X}: {title}" --body "Closes #{phase_issue}\n\nPart of epic #{epic_issue}"
```

**Squash merge:**
```bash
gh pr merge --squash --delete-branch
```

**Create final PR (epic to integration):**
```bash
gh pr create --base {integration_branch} --title "{epic_title}" --body "Closes #{epic_issue}\n\n## Phases completed\n{list}"
```

## Confirmation Points

**Confirm (pause and ask):**
- Epic plan: before creating issues and branches, present the full plan
- Implementation plan: after `/plan` mode produces the plan, wait for approval
- Critical review findings: if `/review-pr` finds critical issues, present them
- Final epic merge: before merging epic branch to integration

**Auto-proceed (no confirmation):**
- Repository detection
- Branch and worktree creation (after plan confirmed)
- Issue and sub-issue creation (after plan confirmed)
- State file updates
- Running tests
- Non-critical review findings (just summarize)
- Worktree cleanup after merge
- PR creation

## Variation Handling

### No develop branch
Auto-detected. Use `main` (or `master`) as integration branch. All other workflow steps are identical.

### Single-phase feature
When the user describes only one phase or says "just one phase":
- Skip epic worktree creation
- Create feature branch directly from integration branch: `feature/issue-{N}-{short-name}`
- Create single issue (no sub-issues needed)
- PR targets integration branch directly

### Resume interrupted epic
When invoked with `--resume`:
- Read `.claude/epic.local.md`
- Find the first phase with status != `complete`
- Check if its worktree exists; if so, switch to it
- If worktree does not exist, create it
- Continue from where the phase left off

### Next phase
When invoked with `--next-phase`:
- Read state, find next `pending` phase
- Mark it `in_progress`, create worktree, begin execution

### Finalize
When invoked with `--finalize`:
- Skip to Phase 3 (final PR from epic branch to integration)

## Integration with Other Skills/Commands

- **`/plan`** or **EnterPlanMode**: Invoke at the start of each phase for implementation planning
- **`/review-pr`** or **`/pr-review-toolkit:review-pr`**: Invoke before merging each phase PR and the final epic PR
- **`/feature-dev`**: Optionally invoke within a phase for complex implementation (user decides)
- **TodoWrite**: Track all phases and steps throughout

## Naming Conventions

Keep names short and lowercase with hyphens:
- Epic: `epic-{2-3 word slug}` (e.g., `epic-dashboard-metrics`)
- Phase: `phase{N}-{2-3 word slug}` (e.g., `phase1-backend-metrics`)
- Worktree dirs: same as branch slug without `feature/issue-N-` prefix
