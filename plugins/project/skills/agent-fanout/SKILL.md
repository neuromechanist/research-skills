---
name: agent-fanout
description: "Use this skill when the user asks to \"fan out agents\", \"spawn agents\", \"use an agent team\", \"parallel agents\", \"delegate to subagents\", \"act as team lead\", \"orchestrate implementation\", \"fan out teammates\", or when a task decomposes into 2+ independent work items (parallel exploration, one implementer per issue, a multi-lens PR review panel). Covers the basic mechanics of spawning, briefing, supervising, and synthesizing subagents and teammates, plus the hard cap on fleet size."
---

# Agent Fan-Out and Teams

Orchestrate multiple subagents or teammates to explore, implement, review, and
validate in parallel. This skill makes every judgment call explicit: when to fan
out, how many agents, which model, what to put in each prompt, how to supervise,
and how to combine results.

## When to fan out (decision table)

| Situation | Action |
| --- | --- |
| Single bounded question ("where is X defined?") | No fan-out. Search directly or use one read-only explorer. |
| Open-ended audit/review of a system with 2+ independent subsystems | One read-only explorer per subsystem, in parallel. |
| Multiple root-caused issues, each fixable independently | One implementer per issue, each in its own git worktree. |
| One pull request (PR) ready for review | One review panel (2-5 reviewers, see Review panels below). |
| Sequential work where step N needs step N-1's output | Do NOT parallelize. Run one agent at a time or do it inline. |
| Task needs secrets, deploy rights, or user-only credentials | Do NOT delegate. Keep it in the main session (mark the task "owner: lead"). |

Do not fan out for work you can finish inline in a few minutes; a subagent costs
setup, supervision, and synthesis time.

## Hard limits (compute BEFORE launching)

1. Before any fan-out, compute the worst case: `finders x max findings per
   finder x verifiers per finding + implementers + reviewers`. Write the number
   down in your plan.
2. **Budget: 10-20 agents per run for routine work; hard cap 40.** If the
   math exceeds the routine budget, say so and justify it; if it exceeds 40,
   cut scope before launching: fewer lenses, findings capped per agent
   (`maxItems`-style limits in the prompt), one verification vote instead of
   three. Going past 40 requires explicit user approval in the same
   conversation. If the user's own configuration states a stricter cap, the
   stricter number wins.
3. Prefer waves of 10 or fewer concurrent agents. Finish and synthesize a wave
   before launching the next.
4. Every phase plan states its own agent budget up front (for example "Sonnet
   implementer + Sonnet reviewer, ~3 agents total").
5. If you hit a rate limit: stop spawning, schedule one backoff wait, resume
   staggered. Narrate as a status update, not a question.

Evidence for the cap: an uncapped review-verify fan-out in a real session
reached ~130 agents, rate-limited the account, and disrupted the live product
under review. Compute the count first.

## Roles and model routing

The economics of fan-out: every ecosystem has a cheaper, fast worker tier
below its frontier model (Sonnet below Opus/Fable for Claude; the equivalent
smaller tier for GPT or Gemini). Worker-tier agents perform at near-lead
quality when, and only when, three compensating controls are present: a
detailed brief (the full lifecycle contract below, with exact values and
named tests), mechanical gates they must pass (lint, typecheck, tests, zero
new diagnostics), and lead verification of the result (review panel plus the
lead spot-checking headline claims). Route work to the worker tier by
default and spend the strong model where judgment concentrates: planning,
architecture, and synthesis. This saves both time and cost.

| Role | Agent type | Model | Notes |
| --- | --- | --- | --- |
| Explorer/scout | read-only explorer | small/fast (e.g. Sonnet) | One-shot for bounded questions; named and reusable for recurring investigations. |
| Planner/architect | plan agent | inherit session model (do NOT downgrade) | The one role where the strongest available model matters most. |
| Implementer | general-purpose | small/fast by default; strongest model when the change touches data integrity, encryption, or concurrency | One per issue, one per worktree, named. |
| Reviewer | review agent | small/fast | One panel per PR; fresh agents each PR (never reuse reviewers across PRs). |
| Validator | general-purpose | small/fast | Live/end-to-end checks; classify first what needs human hardware. |
| Integration reviewer | review agent | small/fast | One, at the end; told explicitly to skip re-reviewing what per-PR panels covered. |

Review panels shrink as the code stabilizes: 4-5 lenses while new types and
invariants are being invented, 2-3 once they settle, 1 integration-scoped
reviewer for the final merge.

## Mechanics (the plumbing)

Read `references/fanout-mechanics.md` for tool-by-tool instructions: spawning
(agent tool parameters, naming, model selection, background execution),
messaging (follow-ups, corrections, stand-downs), task boards, worktree
commands, and what to do on platforms without subagent support (run the same
role prompts sequentially in fresh contexts). If you have never spawned an
agent in the current tool, read that file first.

## Briefing rules (what goes in every prompt)

Read `references/fanout-prompts.md` for the full templates. Non-negotiable
elements for every delegated prompt:

1. **Shared CONTEXT block**, authored once, pasted into every prompt of the
   wave: one-line project description, repo/package map, largest files with
   line counts, and a negative list (already-fixed items not to re-report,
   known gaps to extend rather than rediscover).
2. **Scope boundary**: exact worktree/branch (literal commands), files owned by
   concurrent siblings ("agent X is editing files A and B; do not touch them"),
   and read-only vs edit rights.
3. **DECIDED POLICY lines**: pre-resolve every foreseeable ambiguity at spawn
   time so parallel agents cannot diverge ("DECIDED POLICY (lead decision,
   note it in the PR body): ...").
4. **Numbered deliverables** with exact values (constants, thresholds, type
   signatures), never "reasonable defaults".
5. **Gates**: the exact verification commands to run and the numeric bar
   ("zero new lint/type diagnostics vs the measured baseline", "all tests
   green").
6. **How-far boundary**: commit / push / PR / merge, and an explicit DO NOT
   beyond it (usually "Do NOT merge").
7. **Report contract**: a closing "Report:" line dictating the final message's
   exact contents, and the instruction to send the full report as message text
   (report files may be blocked for subagents; idle does not mean delivered).
8. **Secrets rule**: "NEVER read or print .env or any secrets file."
9. **No perfect agent type available?** Reuse the closest adjacent one and
   override its default framing explicitly in the prompt: state what this
   task is and is NOT ("this is a technical disclosure, NOT a journal
   manuscript; do not score on journal criteria; instead assess ..."), so
   the agent does not fall back to its default domain.

## Supervision protocol

- **Canary first**: before launching N parallel instances of an unvalidated
  action, run one and watch it complete.
- **Staleness threshold**: pick a number when you spawn (default 30-60 min for
  implementers). If an agent shows no commits, file writes, or messages within
  it, check filesystem evidence (file mtimes, expected deliverable paths). Do
  not treat "no report yet" as "still working".
- **Escalation ladder**: (1) nudge with the exact expected deliverable, (2)
  narrow the ask ("send what you have now, quote line numbers"), (3) state the
  consequence ("if you do not reply shortly I will take over"), (4) stop the
  agent and finish the work in the main session.
- **Idle without report**: send the standard nudge (template in references).
  If an idle ping arrives after the report already landed, acknowledge and do
  not double-nudge.
- **Zombies**: track which agents are stood down or superseded; if one
  resurfaces, discard its late output explicitly instead of acting on it.
- **Agent hard-fails** (API error, crash): say so, and proceed on the coverage
  that completed. Never silently drop a failed lane and never block everything
  on it. If the dead agent left partial output on disk, brief the replacement
  with an inventory of those files; do not re-run the original prompt blind.
- **Lead keeps its hands off the code**: once delegation is underway, direct
  edits to project source by the lead are a smell. Prefer widening an
  existing agent's mandate or spawning a new one; it keeps every change
  reviewable under a scoped brief and preserves the lead's context for
  coordination. The exception is taking over from a stalled or stopped
  agent.
- **Upstream changes**: after merging anything into a shared branch, message
  every in-flight worker naming exactly what changed and 1-2 acceptable
  reconciliation strategies, before they open PRs.
- **Correction broadcast**: if a claim you gave earlier turns out wrong and
  reached in-flight agents, send each one a named correction quoting the wrong
  claim, the disproving evidence, and their specific rework. Leave a marker in
  project docs where the wrong path was taken.

## Synthesis rules (after a wave returns)

1. Merge N reports into ONE consolidated, prioritized list, bucketed by
   severity (Critical / Important / Moderate / Suggestion).
2. Every finding is either accepted (dispatched with an exact fix) or rejected
   with a one-sentence rationale recorded in an "EXPLICITLY REJECTED" section.
   No silent drops.
3. When two agents disagree on a fact, reproduce it yourself with a minimal
   check (grep, script, source read). Never average or pick by confidence.
4. Reproduce any headline numeric claim that gates a merge yourself before
   standing the worker down; state your number next to theirs.
5. Treat a subagent's causal explanation as a hypothesis: spot-check the most
   load-bearing fact against the evidence its own report cites before relaying
   it or acting on it.
6. "PR open" and "PR reviewed with findings addressed" are two separately
   verified states. A task completes on its own stated criterion (usually
   merge), not on the nearest milestone.

## Done

The fan-out is complete when: every spawned agent is completed, stood down, or
stopped with its output accounted for; every finding is dispatched or rejected
with a reason; every claimed result you relied on has been independently
spot-checked; worktrees and other artifacts created for the wave are cleaned
up; and the state file / task board reflects final status.
