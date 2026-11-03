---
name: project-preflight
description: "Use when starting work in an existing repository or before a review, planning, or GitHub operation to identify the repository, worktree, shell, terminal, GitHub CLI, credential inheritance, and native-agent surfaces."
version: 0.1.0
---

# Project Preflight

Run the bundled read-only preflight probe before relying on repository, shell,
terminal, GitHub, or native-agent state. It never spawns agents, changes files,
or prints credentials.

`<project-plugin-root>` is the project plugin directory that holds `skills/`, `scripts/`, and `templates/`:
the parent of the `skills/` directory that contains this skill, which is `../..` from this `SKILL.md`'s folder.
Confirm it with `test -x <project-plugin-root>/scripts/project-preflight`;
if that fails, report the path you resolved and stop.
Plugin helpers are not on `PATH`, so call them by absolute path.
When working from a checkout, the root is `plugins/project`.
Run:

```bash
<project-plugin-root>/scripts/project-preflight --format json
```

Use the JSON fields to distinguish repository-detection failures from optional
GitHub or native-agent capability failures. Required repository fields are
`repo_root`, `integration_branch`, and `current_branch`. Before a GitHub
operation, inspect `has_gh`, `gh_command_status`, `gh_network_status`,
`gh_auth_status`, `gh_token_status`, and `gh_child_credential_status`; before a
review panel, inspect `native_agent_status`, `native_agent_surface`,
`agent_model`, `agent_effort`, and `agent_max_reviewers`.

If the executable cannot be resolved, report that the project plugin is
partially installed instead of substituting a different detector or inferring
missing values.
