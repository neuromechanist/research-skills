---
name: implementation-planning
description: "Use this skill when the user asks to \"plan this feature\", \"write an implementation plan\", \"design before coding\", \"think through the approach\", \"review this plan\", or before any multi-file change, architectural decision, experiment with a go/no-go outcome, or strategic pivot. Produces a verifiable plan with pre-registered decision gates and an explicit list of open judgment calls."
---

# Implementation Planning

Plans that a different (or weaker) model could execute without re-deriving
your reasoning, with success criteria fixed before any result is seen.

## Pick the register (by stakes, not size)

| Situation | Register |
| --- | --- |
| Hard to reverse after shipping; touches privacy, auth, what data leaves the device, or public contracts; strategic pivot | **Heavyweight**: full plan document, user approval gate before executing (plan mode where available). |
| Known engineering backlog; the work is clear, there is just a lot of it | **Lightweight**: tracked issues carrying the full spec (template below); no separate plan document. |
| Single ordinary change | No formal plan; the engineering-loop skill's step order is the plan. |

The dividing line is reversibility and blast radius, not effort. A large
backlog of clear fixes needs no plan document; a small change to what an
external partner receives does.

## Heavyweight plan: required sections

```markdown
# Plan: <title> (issue #N)
## Context
[The evidence forcing this work, with numbers. What the previous phase or
investigation proved.]
## What already exists to reuse (do not rebuild)
[Named files/functions. Every plan must check this before proposing new code.]
## Approach
[The design, and one paragraph on why this and not the leading alternative.]
## Files
[New and modified, explicit paths.]
## Decision gate (set BEFORE looking at results)
[Crisp pass/fail: "X ships as default if metric A >= threshold on every
case AND metric B does not regress; if it fails, honest conclusion + named
fallback. No adoption of a non-passing candidate."]
## Prerequisites (user actions)
[Only the human can do these: account registrations, credentials, hardware.]
## Agent budget
[How many subagents this plan will spawn, worst case; see agent-fanout cap.]
## Open judgment calls
[Every ambiguity you resolved unilaterally, as a flagged list the reviewer
can veto. Silence on ambiguity is a defect.]
## Verification
[How each deliverable is proven: commands, thresholds, who runs them.]
```

## Lightweight register: the issue IS the plan

```markdown
## Symptom
[User-visible behavior, verbatim if reported.]
## Root cause
[file:line, what is wrong, the fixture/test/commit that proves it.]
## Fix
[Concrete, scoped change. DECIDED POLICY lines for any foreseeable ambiguity.]
Refs: #A, #B.
```

An implementer (human or agent) executes from the issue alone; that is the
test of whether it is written well enough.

## Non-negotiable planning rules

1. **Verify load-bearing claims.** Before presenting any plan, list the 3-5
   facts that would break it if wrong, and re-check each one directly against
   source or live state, even when a trusted subagent supplied them.
2. **Pre-register gates.** Success/failure thresholds are written before the
   experiment or implementation runs. Re-running with adjusted parameters
   without disclosing that the original gate failed is prohibited.
3. **Check sibling documents.** Open issues, ADRs, and plan files in the same
   tracker may carry constraints on your deliverable that your source
   document does not restate. Surface contradictions before code starts.
4. **Reuse before rebuild.** The "already exists" section is mandatory;
   check the codebase and past research before proposing new modules.
5. **Separate decisions from details.** Batch every decision that needs the
   user (hard to reverse, quoted to third parties, spends real money or
   days of compute) into ONE structured question with 2-4 labeled options,
   one marked "(Recommended)", each with a one-line evidence-based rationale.
   Decide internal implementation details yourself and state them as facts.
   If a question times out unanswered, proceed with the recommended option
   and disclose that at the next checkpoint the user will read ("approving
   this plan also approves X").
6. **Persist the plan-of-record outside chat.** GitHub epic/issue plus a
   Definition of Done with measurable criteria; make gates self-enforcing
   where possible (a strict expected-failure test on the exact metric beats
   a prose checklist). Conversation history will be compacted; the tracker
   survives.
7. **New information reorders work.** When new input contradicts or gates a
   decision already acted on, stop downstream work, resolve the upstream
   decision first, state why the order flipped, then resume.
8. **Plans from subagents get verified, not trusted.** A planning agent must
   be read-only, cite file:line for its claims, and end with its own open
   judgment calls; you then re-verify its load-bearing claims (rule 1)
   before adopting the plan. Planning agents run on the session's own model,
   not the cheap worker tier.
9. **Kill cleanly.** When a gate fails, execute the named fallback: revert
   prototype code (with authorization), record the dead end (what was tried,
   what it cost, why it failed) in the tracker and scratch notes, and mark
   deferred ideas explicitly as deferred, never silently dropped.

## Phase sizing (feeds epic-dev)

One phase = one independently reviewable and testable PR: roughly one
subsystem, one migration, or up to ~500 net lines of non-generated change.
If the description contains two or more such units, it is an epic (use
epic-dev); if not, it is a single feature (engineering-loop). Name phases
with 2-3 word kebab-case slugs: drop stopwords, keep the object noun first
("backend-metrics", "sync-engine", not "implement-the-new-backend-metrics").
