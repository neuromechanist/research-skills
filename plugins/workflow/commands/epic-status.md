---
description: Show current epic/sprint workflow state
allowed-tools: ["Bash", "Read", "Glob"]
---

# Epic Status

Display the current state of the active epic workflow.

## Actions

1. Find the state file at `.claude/epic.local.md` in the current repo root (use `git rev-parse --show-toplevel` to find it)
2. If no state file exists, report: "No active epic found in this repository."
3. If state file exists, read it and parse the YAML frontmatter
4. Display a formatted summary:

```
Epic: #{epic_issue} - {epic_title}
Integration branch: {integration_branch}
Epic branch: {epic_branch}
Current phase: {current_phase} of {total_phases}

Phases:
  [x] Phase 1: {title} (#{issue}, PR #{pr})
  [ ] Phase 2: {title} (#{issue}) <- current
  [ ] Phase 3: {title} (#{issue})
```

5. Check active worktrees with `git worktree list` and show which ones belong to this epic
6. For the current phase, show its branch and whether a PR exists yet
7. Show GitHub links: `https://github.com/{owner}/{repo}/issues/{epic_issue}`
