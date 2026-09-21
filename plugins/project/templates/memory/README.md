# Project Memory

This directory is the project's durable, agent-agnostic memory. Track it in
version control so any agent, model, machine, or human can read and review the
same operational observations.

## One fact per file

Create one Markdown file per observation, using a short kebab-case filename and
YAML frontmatter like this:

```markdown
---
name: descriptive-short-name
description: One-line hook for the index
type: observation
recorded: 2026-09-20
revalidate_after: 2026-10-20
---

What was observed, how it was verified, and what would make it stale.
```

Use an ISO date for `recorded` and set `revalidate_after` whenever the fact
depends on a file, flag, workflow, dependency, service, or other changing
surface. Add the entry to `INDEX.md` with a one-line hook. Correct or delete a
memory as soon as it becomes false; a stale memory is actively harmful.

Memory is an observation, not authority. It must not silently become a rule.
If the entry starts to say what future work must do, promote the underlying
choice to an Architecture Decision Record (ADR) instead.

## The three-way boundary

Keep these stores distinct:

| Store | Meaning | Authority | Lifecycle |
| --- | --- | --- | --- |
| `.context/decisions/` | A ruling and its alternatives | Binding; an ADR wins when sources disagree | Never delete; supersede with a later ADR |
| `.context/` | Analysis, plans, maps, and evidence | Informational | Rewrite freely; mark historical when complete |
| `.memory/` | An operational observation that saves the next person time | Non-binding; never cite it as a decision | Correct or delete when false |

Before writing, ask two questions. Could someone reasonably have decided the
other way? If yes, record the alternatives and costs in an ADR. Does the note
bind anyone? If yes, it is an ADR, not a memory. A memory can be promoted to an
ADR when it reveals a choice; analysis can be compressed into an ADR when it
settles. An ADR does not decay into a memory.

## Safety boundary

Never commit secrets, tokens, API keys, credentials, private transcripts,
customer data, personal data, or information about a named individual here.
Do not copy agent-private memory wholesale. Record only the smallest
project-relevant observation that is safe to review and publish with the
repository. Link to a public issue, commit, or document when useful, after
checking that the link itself does not disclose sensitive information.
