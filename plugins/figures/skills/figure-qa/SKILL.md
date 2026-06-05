---
name: figure-qa
description: Use this skill to QA a scientific figure for journal compliance, alignment, palette correctness, and label legibility. Triggers on "QA this figure", "check this figure", "review my figure", "is this figure paper-ready", "validate figure", or when invoked proactively after a figure-generation skill produces output (unless the caller passes no-qa). Dispatches on input type (SVG, raster PNG/JPG/TIFF, Python plot script, or composed-figure directory) and runs the right programmatic checks plus a VLM rubric judgment pass.
version: 0.1.0
---

# Figure QA

Routes a scientific figure to an **independent, fresh-context QA reviewer** that detects the input type, runs the deterministic checks (fonts, palette, geometry, alpha, DPI) via helper scripts, and adds a VLM rubric judgment for the aesthetic dimensions. This skill is a thin dispatcher: the detection logic, exit-code contract, VLM rubric, and report format all live in `references/figure-qa-procedure.md`, and the deterministic engine lives in the figures plugin's `agents/figure-qa-scripts/`.

## When to use

Activate when a figure needs a journal-submission QA pass, or proactively after a figure-generation skill (scientific-figure, svg-figure, svg-primitives, transparent-icons, ai-full-figure, plot-styling) produces output, unless the caller passes `no-qa`.

## Why a fresh-context reviewer

A QA pass is more trustworthy from a reviewer that did not just author the figure. Run it in a separate context and pass only the figure path, input type (if known), and target journal. On tools without subagents, run the procedure inline.

## Dispatch

In every branch the reviewer follows `references/figure-qa-procedure.md` (strict separation: scripts own ground-truth measurements, VLM owns aesthetic judgment).

- **Claude Code:** `Task(subagent_type: "figure-qa", ...)` passing the figure path and target journal. Honor a `no-qa` opt-out by returning immediately.
- **Codex CLI:** install `agents/templates/figure-qa.toml` to `~/.codex/agents/` (or project `.codex/agents/`), then run the `figure-qa` subagent (`/agent`).
- **Copilot CLI:** install `agents/templates/figure-qa.agent.md` to `.github/agents/` (or `~/.copilot/agents/`), then run the `figure-qa` agent.
- **Fallback** (no subagent support, or an interactive in-thread check): first locate the procedure (`$CLAUDE_PLUGIN_ROOT/skills/figure-qa/references`, else `find . -type d -path '*/skills/figure-qa/references' | head -1`); if it cannot be found, stop and tell the user to install the figures plugin rather than guessing checks. Then follow `references/figure-qa-procedure.md` directly.

## The brain (do not duplicate into dispatch or agent shells)

- `references/figure-qa-procedure.md` -- no-qa opt-out, script location, type detection, per-branch checks, exit-code contract, VLM rubric, and the exact report shape.
- `agents/figure-qa-scripts/check_{svg,raster,plot_script}.py` (in the figures plugin) -- the deterministic engine, kept in place so other skills (e.g. svg-primitives) can call it directly.
