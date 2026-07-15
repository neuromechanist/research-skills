---
name: codebase-onboarding
description: "Use this skill when the user asks to \"explore this codebase\", \"understand this repo\", \"map the architecture\", \"review our stack\", \"get up to speed\", \"break ground\" on an unfamiliar project or research field, \"what is the state of this project\", \"audit the architecture\", or before planning changes in a codebase you have not worked in. Produces a verified reconnaissance report before any design or edit."
---

# Codebase and Field Onboarding

Build a verified map of an unfamiliar codebase, project, or research area
before planning or editing anything. The output is a reconnaissance report
that separates verified facts from assumptions, ending in a one-paragraph
diagnosis.

## The bootstrap sequence (run in this order)

1. **Date and inventory.** Run `date`. List the tree (source dirs, configs,
   docs). Note the largest files with line counts; they are usually where the
   complexity lives.
2. **Intent docs before code.** Read `AGENTS.md`/`CLAUDE.md`, `README`,
   `.context/` (plan.md, research.md, decisions/), design docs. These say what
   the project is SUPPOSED to be.
3. **Code next.** Read entry points, the main loop or route table, and the one
   or two central types. Do not read everything; read what the intent docs
   point at.
4. **History.** `git log --oneline -20`, open issues and PRs
   (`gh issue list`, `gh pr list`). What was recently worked on, what is
   planned, what is stuck.
5. **What is ACTUALLY running.** Processes, containers (`docker ps -a`), data
   directories on disk, deployed endpoints, cron entries. This step
   distinguishes "designed" from "operated": if the design exists in code and
   issues but there is no runtime data on disk, the true next step is "turn it
   on and calibrate", not "design more".
6. **Verify the specific claim.** Whatever question triggered this onboarding
   ("does compaction work?", "is the migration done?"): grep the source and
   check live state for it directly. Absence of a script is not absence of
   work; completed one-off scripts get deleted.
7. **Probe third-party surfaces.** Before planning against any SDK or API, run
   one cheap introspection command against the INSTALLED version (import it,
   list the dataclass fields, hit the version endpoint). Treat your
   trained-in knowledge of library internals as a hypothesis.
8. **Diagnose in one paragraph.** State plainly what exists, what runs, what
   is broken or missing, and what that implies, before proposing any action.

## Delegating exploration (2+ independent areas)

Split "where is X" (mechanical mapping, delegate it) from "what does X
actually say" (judgment docs such as ADRs and strategy docs; read those
yourself). When the area is larger than one context can hold:

Use the worker/intermediate tier for bounded scouts (Codex Luna/Terra or
Claude Sonnet), but keep diagnosis, keystone verification, and synthesis on
the lead tier (Codex Sol or Claude Fable/Opus). Close/remove each one-off scout
after its report is incorporated. See `agent-fanout` for escalation rules.

- Partition by architectural domain (backend / CLI / web / data / infra) with
  disjoint file ownership, one read-only explorer per domain, all spawned in
  parallel. Agent count = number of genuinely independent domains, within the
  fan-out cap (see the agent-fanout skill).
- For a planned file decomposition: one explorer maps the target file's
  internal structure (symbol inventory with line ranges, module-level mutable
  state), a second maps external dependents (importers, test doubles, dynamic
  imports), and a third reads the merged precedent of a prior similar change,
  to mirror it.
- Every explorer prompt: numbered falsifiable questions naming the suspected
  files/symbols, an explicit READ-ONLY instruction, and the output contract
  "file:line references for load-bearing facts; conclusion-oriented; no file
  dumps". Template in `references/exploration-prompts.md`.
- **Re-verify the keystone fact yourself.** Before any explorer conclusion
  becomes a headline claim or a plan premise, spot-check the single most
  load-bearing fact directly (one grep or file read). Explorer reports are
  hypotheses with citations, not ground truth.

## Field / literature onboarding (research areas)

1. Run broad searches yourself first and save the raw corpus (queries and
   results) to files; then delegate one summarizer per topic family with a
   hard reading list, exact deliverable path, and a bounded return summary.
2. Prefer primary sources (specs, papers, official policy pages); use general
   web search only as a fallback when a primary source is unreachable.
3. Record per-family findings in `research/<family>.md`, synthesize into one
   survey doc, and record the resulting decision as an Architecture Decision
   Record (ADR) with a dated log line in `.context/research.md`
   ("Problem, To investigate, Decision (date), Rationale").
4. If the project's own docs name a preferred tool or skill for surveys and
   you choose differently, say so in one sentence at the point of choice.

## Output contract: the onboarding report

```markdown
## Diagnosis
[One blunt paragraph: what exists, what runs, what is missing/broken, what it implies.]

## Architecture map
[Components, how they connect, entry points; file:line for each claim.]

## Conventions observed
[Naming, testing, error handling, commit style; where the house rules live.]

## What actually runs
[Processes/containers/data found, or "nothing is operating" if so.]

## Verified facts vs assumptions
- Verified: [fact (file:line or command output)]
- Assumed (spot-check before relying): [assumption]

## Recommended next step
[One step, justified by the diagnosis.]
```

## Rules

- No edits during onboarding. This skill is read-only; if you find a bug,
  record it in the report or file an issue.
- On shared or remote machines, reconnaissance is read-only commands only
  (hostname, resource listings); never change drivers, caches, or system state
  on a box other people use, even to fix an obvious problem; report it
  instead.
- Do not stall on ambiguous or typo-heavy briefs: state your reading of the
  request in one sentence with an opt-out ("proceeding on that basis; correct
  me if you meant otherwise") and start the bootstrap sequence.
