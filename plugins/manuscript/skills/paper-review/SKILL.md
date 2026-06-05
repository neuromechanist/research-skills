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

- **Claude Code:** `Task(subagent_type: "paper-review", ...)` passing the manuscript path, target journal/type, and mode. For panel mode, launch one `Task` per lens in parallel, then a final synthesis `Task`.
- **Codex CLI:** install `agents/templates/paper-review.toml` to `~/.codex/agents/` (or project `.codex/agents/`), then run the `paper-review` subagent (`/agent`). For panel mode, ensure `max_threads` covers the lens count.
- **Copilot CLI:** install `agents/templates/paper-review.agent.md` to `.github/agents/` (or `~/.copilot/agents/`), then run the `paper-review` agent; use `/fleet` for panel mode.
- **Fallback** (no subagent support, or the user wants an interactive in-thread review): first locate the rubric (`$CLAUDE_PLUGIN_ROOT/skills/paper-review/references`, else `find . -type d -path '*/paper-review/references' | head -1`); if it cannot be found, stop and tell the user to install the manuscript plugin rather than reviewing from memory. Then follow `references/review-procedure.md` directly in this context.

## The brain (do not duplicate into dispatch or agent shells)

- `references/review-procedure.md` -- step-by-step procedure: intake, read, methodology, logic, literature, reproducibility, figures, writing, output.
- `references/methodology-checklist.md`, `references/statistical-review-guide.md`, `references/figure-review-guide.md` -- the assessment checklists and guides.
- `references/review-principles.md` -- review philosophy and severity calibration.
- `references/review-output-template.md` -- the Synopsis / Critical / Major / Minor / Editor Note format.
- `examples/sample-manuscript-excerpt.md` -- sample manuscript input for testing.
- Sister skill `manuscript:humanizer` -- AI-writing patterns to flag in the prose-quality pass.
