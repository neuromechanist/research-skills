---
name: grant-review
description: This skill should be used when the user asks to "review a grant", "review my proposal", "score this grant", "evaluate my specific aims", "critique my research strategy", "review as an NIH reviewer", "review as an NSF panelist", "give me reviewer feedback", "check my grant proposal", "review my R01", "review my K99", "review my SBIR", "review my STTR", "review my Phase I application", "review my Phase II application", "review my commercialization plan", "evaluate my CAREER proposal", "run a mock study section", "run a grant readability review", "check my clear sentences", "review my resubmission", "review this PDF", "check my proposal PDF", "analyze my grant layout", or mentions grant review, proposal critique, NIH scoring, NSF panel review, small business grant review, study section feedback, or proposal PDF review.
version: 0.2.0
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
- **Readability (run BEFORE the panel):** one fresh-context reviewer restricted to clarity, with no merit scoring. Follow `references/readability-procedure.md`; a panel can run clean while the first page still contains prose the PI cannot follow on first read. The default pass reports line-anchored, length-neutral rewrites for long chained sentences, ambiguous pronouns, premature terms or abbreviations, rhetorical inversions, and gratuitous self-undermining while preserving substantive limitations. If requested, the same reviewer can add the optional conciseness hunt as a second pass; do not fan out a second agent unless the caller asks for it. Conciseness rewrites must be strictly shorter while preserving every number, citation, qualification, and required element.

## Dispatch

Pick the branch for the current tool. Single and panel reviews follow `references/review-procedure.md`; readability reviews follow `references/readability-procedure.md` and never score merit.

- **Claude Code:** `Agent(subagent_type: "grant:grant-review", ...)` passing the proposal path, mechanism, and mode. The agent selects the readability procedure when `mode=readability`; for panel mode, issue one `Agent` call per reviewer role in a single message so they run in parallel, then a final synthesis `Agent` call.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex reviewer, first copy `agents/templates/grant-review.toml` to `~/.codex/agents/` or `.codex/agents/`, then invoke that configured agent if the current Codex surface supports `/agent`. Pass `mode=readability` for the non-scoring pass. For panel mode, ensure `max_threads` covers the reviewer count. If no Codex subagent is configured or available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` reviewer in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents; pass `mode=readability` for the non-scoring pass and use `/fleet` for panel mode when available. If running outside a plugin install, copy `agents/templates/grant-review.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback** (no subagent support, or the user wants an interactive in-thread review): first locate the rubric (`$CLAUDE_PLUGIN_ROOT/skills/grant-review/references`, else `find . -type d -path '*/skills/grant-review/references' | head -1`); if it cannot be found, stop and tell the user to install the grant plugin rather than reviewing from memory. Then follow `references/readability-procedure.md` for `mode=readability`, or `references/review-procedure.md` for other modes.

## The brain (do not duplicate into dispatch or agent shells)

- `references/review-procedure.md` -- step-by-step procedure: mechanism ID, ingest, score, synthesize, output.
- `references/readability-procedure.md` -- non-scoring first-read clarity pass with anchored, page-neutral rewrites and an optional concise-writing hunt.
- `references/nih-review-criteria.md`, `references/nih-career-training-criteria.md`, `references/nsf-review-criteria.md` -- criteria and scoring.
- `references/sbir-sttr-review-criteria.md` -- SBIR/STTR (R41, R42, R43, R44) criteria. These are **not** reviewed under the RPG Simplified Review Framework; they keep the five classic scored criteria plus commercial-potential questions, Commercialization Plan assessment, Phase I milestones, Phase I progress, and Fast-Track acceptability.
- `references/review-best-practices.md` -- calibration and common reviewer comments.
- `references/review-output-templates.md` -- NIH and NSF output format.
- `examples/sample-nih-r01-review.md` -- worked review; `examples/sample-r01-aims.md` -- sample proposal input for testing.
- Sister skill `manuscript:humanizer` (invoke through the host's skill-invocation mechanism) -- AI-writing patterns to flag in grant prose.
