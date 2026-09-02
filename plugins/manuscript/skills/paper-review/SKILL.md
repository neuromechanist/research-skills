---
name: paper-review
description: "Use this skill for \"review this paper\", \"review this manuscript\", \"peer review\", \"review my paper\", \"critique this manuscript\", \"review this submission\", \"give me feedback on my paper\", \"check my methods\", \"review my statistics\", \"review as a peer reviewer\", \"evaluate this manuscript\", \"review this PDF\", or mentions manuscript review, peer review, paper critique, or methodological review."
version: 0.1.1
---

# Academic Manuscript Review

Routes a manuscript to an **independent, fresh-context reviewer** that evaluates it for methodological soundness, statistical validity, logical consistency, and reproducibility, and returns a structured peer review. This skill is a thin dispatcher: it decides how to run the reviewer and in which mode. The review procedure, checklists, statistical and figure guides, principles, and output template all live in `references/` and are loaded by the reviewer, not duplicated here.

## When to use

Activate when the user wants peer-review feedback on a manuscript (journal article, conference paper, preprint).

## Why a fresh-context reviewer

Review validity depends on independence: a reviewer that shares the conversation that produced the manuscript is biased toward it. Run the reviewer in a separate context and pass only **framing** (manuscript path, target journal, manuscript type, revision status), never the authoring rationale. This is why the reviewer is a subagent on tools that support one, and an inline procedure where they do not.

## Modes (user decides each run)

- **Single (default):** one independent reviewer applies the full procedure end to end.
- **Panel (opt-in):** spawn independent reviewers in parallel on complementary lenses, then a synthesis pass. Trigger on "review panel", "multiple reviewers", or an explicit request. Lenses: **methods/design**, **statistics**, and **novelty/significance** (add **reproducibility** for methods-heavy or hardware papers). Each reviewer reads the whole manuscript but weights its lens and scores independently from `references/`; a final synthesis pass merges them into one Critical/Major/Minor review and surfaces genuine disagreement rather than averaging it away.

## Dispatch

Pick the branch for the current tool. In every branch the reviewer follows `references/review-procedure.md`.

- **Claude Code:** `Agent(subagent_type: "manuscript:paper-review", ...)` passing the manuscript path, target journal/type, and mode. For panel mode, issue one `Agent` call per lens in a single message so they run in parallel, then a final synthesis `Agent` call.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex reviewer, first copy `agents/templates/paper-review.toml` to `~/.codex/agents/` or `.codex/agents/`, then invoke that configured agent if the current Codex surface supports `/agent`. For panel mode, ensure `max_threads` covers the lens count. If no Codex subagent is configured or available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` reviewer in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents; use `/fleet` for panel mode when available. If running outside a plugin install, copy `agents/templates/paper-review.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback** (no subagent support, or the user wants an interactive in-thread review): first locate the rubric (`$CLAUDE_PLUGIN_ROOT/skills/paper-review/references`, else `find . -type d -path '*/skills/paper-review/references' | head -1`); if it cannot be found, stop and tell the user to install the manuscript plugin rather than reviewing from memory. Then follow `references/review-procedure.md` directly in this context.

## The brain (do not duplicate into dispatch or agent shells)

- `references/review-procedure.md` -- step-by-step procedure: intake, read, methodology, logic, literature, reproducibility, figures, writing, output.
- `references/methodology-checklist.md`, `references/statistical-review-guide.md`, `references/figure-review-guide.md` -- the assessment checklists and guides.
- `references/review-principles.md` -- review philosophy and severity calibration.
- `references/review-output-template.md` -- the Synopsis / Critical / Major / Minor / References / Editor Note format.
- `examples/sample-manuscript-review.md` -- worked review for calibration; `examples/sample-manuscript-excerpt.md` -- sample manuscript input for testing.
- Sister skill `manuscript:humanizer` (invoke with the Skill tool by that name) -- AI-writing patterns to flag in the prose-quality pass.
