---
name: figure-qa
description: Use this skill to QA a scientific figure for journal compliance, alignment, palette correctness, and text legibility. Triggers on "QA this figure", "check this figure", "review my figure", "is this figure paper-ready", "validate figure", "check the text in this figure", or when invoked after a figures skill produces output (unless the caller passes no-qa). Dispatches on input type (SVG, raster PNG/JPG/TIFF, Python plot script, or composed-figure directory), runs the programmatic checks including OCR of expected strings and palette compliance against the project theme, adds a vision rubric pass, and returns a report with a machine-readable JSON verdict that drives the generate, QA, fix loop.
version: 0.2.0
---

# Figure QA

Routes a scientific figure to an independent, fresh-context QA reviewer that detects the input type, runs the deterministic checks (fonts, palette, geometry, alpha, resolution, rendered text) with the helper scripts, and adds a vision-language model (VLM) rubric judgment for the aesthetic dimensions.
This skill is a thin dispatcher: the detection logic, exit-code contract, VLM rubric, report shape, and the iterate loop all live in `references/`, and the deterministic engine lives in the figures plugin's `agents/figure-qa-scripts/`.

## When to use

Activate when a figure needs a journal-submission QA pass, or after a figures skill (`figures:scientific-figure`, `figures:svg-figure`, `figures:svg-primitives`, `figures:transparent-icons`, `figures:ai-full-figure`, `figures:plot-styling`) produces output, unless the caller passes `no-qa`.

## What to pass to the reviewer

Every dispatch carries the same briefing, so the right checks run:

- the figure path and, when known, the input type
- the target journal (`nature`, `science`, `cell`, `pnas`, `poster`, `slide`, or `generic`)
- the theme path (`figures/theme.json`) so palette compliance is judged against the project bible rather than a fixed allow-list
- every verbatim string the figure was asked to render (titles, panel letters, labels); without this list the raster text check is silently off
- the physical width in millimetres for raster inputs, so text height converts to points

## Why a fresh-context reviewer

A QA pass is more trustworthy from a reviewer that did not just author the figure.
Run it in a separate context and pass only the briefing above.
On tools without subagents, run the procedure inline.
For several candidates, issue one dispatch per candidate in a single message so they run in parallel on the Sonnet tier.

## Dispatch

In every branch the reviewer follows `references/figure-qa-procedure.md` (strict separation: scripts own ground-truth measurements, the VLM owns aesthetic judgment).

- **Claude Code:** `Agent(subagent_type: "figures:figure-qa", ...)` with the briefing above. Honor a `no-qa` opt-out by returning immediately.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex reviewer, first copy `${CLAUDE_PLUGIN_ROOT}/agents/templates/figure-qa.toml` (the plugin's `agents/templates/` directory) to `~/.codex/agents/` or `.codex/agents/`, then invoke that configured agent if the current Codex surface supports `/agent`. If no Codex subagent is configured or available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` reviewer in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents. If running outside a plugin install, copy `agents/templates/figure-qa.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback** (no subagent support, or an interactive in-thread check): first locate the procedure (`$CLAUDE_PLUGIN_ROOT/skills/figure-qa/references`, else `find . -type d -path '*/skills/figure-qa/references' | head -1`); if it cannot be found, stop and tell the user to install the figures plugin rather than guessing checks. Then follow `references/figure-qa-procedure.md` directly.

## The report and the loop

The report keeps its markdown sections and ends with one fenced JSON block: `status` (`ship`, `revise`, `block`), `findings[]` each with `check`, `severity`, `message`, `action` (`regenerate`, `edit`, `overlay`, `rescale`, `recolor`, `none`) and a `hint`, plus `measurements` and the five VLM scores.
Generation skills branch on that block.
`references/iterate-loop.md` defines the generate, QA, fix, regenerate loop (N candidates in parallel, one targeted change per iteration, stop at `ship` or after three iterations) that `figures:ai-full-figure` follows.

## The brain (do not duplicate into dispatch or agent shells)

- `references/figure-qa-procedure.md`: no-qa opt-out, script location, type detection, per-branch checks including the raster text check and theme palette compliance, exit-code contract, VLM rubric, the exact report shape, and the finding-to-action table.
- `references/iterate-loop.md`: the candidate, QA, fix loop with its worker briefing and stopping conditions.
- `agents/figure-qa-scripts/check_{svg,raster,plot_script}.py` (in the figures plugin): the deterministic engine, kept in place so other skills can call it directly. `check_raster.py --json --expect-text "..." --palette figures/theme.json --width-mm 89 --journal nature` is the text and palette check; `check_svg.py --json --palette figures/theme.json` covers SVG geometry, fonts, and palette.
