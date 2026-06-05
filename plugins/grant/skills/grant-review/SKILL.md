---
name: grant-review
description: This skill should be used when the user asks to "review a grant", "review my proposal", "score this grant", "evaluate my specific aims", "critique my research strategy", "review as an NIH reviewer", "review as an NSF panelist", "give me reviewer feedback", "check my grant proposal", "review my R01", "review my K99", "evaluate my CAREER proposal", "run a mock study section", "review my resubmission", "review this PDF", "check my proposal PDF", "analyze my grant layout", or mentions grant review, proposal critique, NIH scoring, NSF panel review, study section feedback, or proposal PDF review.
version: 0.1.2
---

# Grant Proposal Review

Routes a grant proposal to an **independent, fresh-context reviewer** that scores it against the official NIH or NSF criteria and returns a structured review. This skill is a thin dispatcher: it decides how to run the reviewer and in which mode. The review procedure, criteria, scoring rubrics, and output templates all live in `references/` and are loaded by the reviewer, not duplicated here.

## When to use

Activate when the user wants feedback on a grant proposal (specific aims, research strategy, project description) evaluated against NIH or NSF review criteria.

## Why a fresh-context reviewer

Review validity depends on independence: a reviewer that shares the conversation that produced the proposal is biased toward it. Run the reviewer in a separate context and pass only **framing** (proposal path, mechanism/agency, resubmission status, target program), never the authoring rationale. This is also why the reviewer is a subagent on tools that support one, and an inline procedure where they do not.

## Modes (user decides each run)

- **Single (default):** one independent reviewer applies the full procedure end to end.
- **Panel (opt-in):** spawn N independent reviewers in parallel, then a synthesis pass. Trigger on "mock study section", "panel review", or an explicit request for multiple reviewers. NIH: 3 reviewers; NSF: 2-3 panelists. Each reviewer scores independently from `references/`; a final chair pass reconciles them into one output. Surface genuine disagreement rather than blindly averaging scores.

## Dispatch

Pick the branch for the current tool. In every branch the reviewer follows `references/review-procedure.md`.

- **Claude Code:** `Task(subagent_type: "grant-review", ...)` passing the proposal path, mechanism, and mode. For panel mode, launch one `Task` per reviewer role in parallel, then a final synthesis `Task`.
- **Codex CLI:** install `agents/templates/grant-review.toml` to `~/.codex/agents/` (or project `.codex/agents/`), then run the `grant-review` subagent (`/agent`). For panel mode, ensure `max_threads` covers the reviewer count.
- **Copilot CLI:** install `agents/templates/grant-review.agent.md` to `.github/agents/` (or `~/.copilot/agents/`), then run the `grant-review` agent; use `/fleet` for panel mode.
- **Fallback** (no subagent support, or the user wants an interactive in-thread review): run the procedure directly in this context by following `references/review-procedure.md`.

## The brain (do not duplicate into dispatch or agent shells)

- `references/review-procedure.md` -- step-by-step procedure: mechanism ID, ingest, score, synthesize, output.
- `references/nih-review-criteria.md`, `references/nih-career-training-criteria.md`, `references/nsf-review-criteria.md` -- criteria and scoring.
- `references/review-best-practices.md` -- calibration and common reviewer comments.
- `references/review-output-templates.md` -- NIH and NSF output format.
- `examples/sample-nih-r01-review.md` -- worked review; `examples/sample-r01-aims.md` -- sample proposal input for testing.
- Sister skill `manuscript:humanizer` -- AI-writing patterns to flag in grant prose.
