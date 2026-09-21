---
name: project-preflight
description: "Use when starting work in an existing repository or before a review, planning, or GitHub operation to identify the repository, worktree, shell, terminal, GitHub CLI, credential inheritance, and native-agent surfaces."
version: 0.1.0
---

# Project Preflight

Run the bundled read-only preflight probe before relying on repository, shell,
terminal, GitHub, or native-agent state. It never spawns agents, changes files,
or prints credentials.

Resolve the executable from the project plugin installation that contains this
skill, using its sibling `bin/project-preflight` path. When working from a
checkout, that path is `plugins/project/bin/project-preflight`. Invoke the
executable by its absolute path rather than assuming that the plugin's `bin/`
directory is on `PATH`:

```bash
<project-plugin-root>/bin/project-preflight --format json
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
