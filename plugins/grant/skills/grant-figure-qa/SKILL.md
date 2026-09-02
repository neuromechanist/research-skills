---
name: grant-figure-qa
description: Use this skill to review grant proposal figures for compliance, resolution, accessibility, and quality. Triggers on "check grant figures", "review proposal figures", "figure QA for grant", "NIH figure requirements", or when preparing a grant for submission.
version: 0.1.0
---

# Grant Figure QA

Routes a grant proposal's figures to an **independent, fresh-context QA reviewer** that checks every figure for NIH/NSF compliance (resolution, dimensions, fonts, color accessibility, content, captions) and returns a structured report. This skill is a thin dispatcher: the full checklist and report format live in `references/figure-qa-procedure.md`.

## When to use

Activate when preparing a grant for submission and the figures need a compliance and accessibility pass, or when the user asks to check proposal figures.

## Why a fresh-context reviewer

A compliance pass is more trustworthy from a reviewer that did not author the figures. Run it in a separate context and pass only the proposal directory and target agency. On tools without subagents, run the procedure inline.

## Dispatch

In every branch the reviewer follows `references/figure-qa-procedure.md`.

- **Claude Code:** `Agent(subagent_type: "grant:grant-figure-qa", ...)` passing the proposal directory and agency (NIH/NSF). Honor a `no-qa` opt-out by returning immediately.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex reviewer, first copy `agents/templates/grant-figure-qa.toml` to `~/.codex/agents/` or `.codex/agents/`, then invoke that configured agent if the current Codex surface supports `/agent`. If no Codex subagent is configured or available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` reviewer in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents. If running outside a plugin install, copy `agents/templates/grant-figure-qa.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback** (no subagent support, or an interactive in-thread check): first locate the procedure (`$CLAUDE_PLUGIN_ROOT/skills/grant-figure-qa/references`, else `find . -type d -path '*/skills/grant-figure-qa/references' | head -1`); if it cannot be found, stop and tell the user to install the grant plugin rather than guessing requirements. Then follow `references/figure-qa-procedure.md` directly.

## The brain (do not duplicate into dispatch or agent shells)

- `references/figure-qa-procedure.md` -- locate figures, resolution/dimensions, fonts, color accessibility, content, captions, and the report format, with the NIH/NSF requirement thresholds.
