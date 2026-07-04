---
name: engineering-loop
description: "Use this skill when the user asks to \"implement this change\", \"fix this issue\", \"add this feature\", \"make this change properly\", \"ship this\", or for any ordinary single-PR development task: one issue, one branch, one pull request. For multi-phase features use epic-dev; for unfamiliar code run codebase-onboarding first; for failing behavior use the debugging skill."
---

# Engineering Loop (single change, one PR)

The standard loop for one ordinary change: spec to merged PR with review and
verification. Lightweight counterpart to the epic-dev workflow.

## Scale check (before starting)

| Signal | Route |
| --- | --- |
| One reviewable unit: one subsystem, roughly a day or less | This skill. |
| 2+ independently reviewable/testable units, or multiple subsystems | epic-dev (phased epic with worktrees). |
| You have not worked in this code before | codebase-onboarding first, then return here. |
| Behavior is wrong and cause unknown | debugging skill first; the fix then follows this loop. |
| No issue exists yet | Create one (except trivial fixes); it is the durable spec. |

## The loop

1. **Read the spec.** `gh issue view N`. If the request is a one-line or
   ambiguous instruction, restate your interpretation in one sentence with an
   opt-out ("proceeding on that basis; tell me if you meant X") and continue;
   do not stall.
2. **Explore just enough, then find the pattern to mirror.** Read the target
   area and locate an existing correct implementation of the same shape
   (a similar route, a similar test, the sibling module). New code mirrors
   the house pattern; do not invent a new one for an ordinary change. If the
   change builds on a third-party API you have not used in this repo, probe
   the installed version first (import and inspect; do not trust memory).
3. **Branch.** `gh issue develop N --checkout` (or
   `git checkout -b feature/issue-N-<slug>` per repo convention). Never work
   on the default branch.
4. **Pin test first (refactors only).** If the change claims to preserve
   behavior, commit #1 is a characterization test captured against the
   ORIGINAL code (route inventory, golden output). A pin test written after
   the move proves nothing.
5. **Implement the smallest coherent diff.** Match surrounding style. Discard
   incidental churn before committing (lockfiles, formatting of untouched
   lines). No backward-compatibility shims when the user confirms zero
   consumers; remove outright and preserve the substantive invariant instead.
   For every new guard or error path, decide fail-open vs fail-closed
   explicitly and say why in the code or PR.
6. **Gate every commit.** Format, lint, typecheck, test; the bar is zero NEW
   diagnostics against the MEASURED baseline (measure it; do not trust a
   documented number, and note discrepancies). Python: `uv run ruff format
   && uv run ruff check --fix && uv run ty check && uv run pytest`.
   JS/TS: `bun run biome check --write && bun test` (or the project's
   configured commands). Commit atomically: subject under 50 characters, no
   emojis, no AI attribution.
7. **Long-running steps** (benchmarks, big builds, batch jobs over ~10
   minutes): detach them per `references/background-jobs.md`; never leave
   them as session-tracked shells. Commit expensive-to-reproduce results the
   moment they land, separately from code.
8. **Push and open the PR.** Body: what changed, why (link "Closes #N"), and
   what was tested with commands and counts. No emojis, no AI attribution.
9. **Review.** Run the pr-review-toolkit skill (or repo review command) on
   the PR. Address ALL findings: fix, or reject with a one-sentence reason
   posted to the PR ("false positive" / "intentionally different by design").
   No silent drops; a deleted test that held the only coverage of a scenario
   is a blocking gap, not a nit.
10. **CI, then merge.** Wait for checks (background watch:
    `gh pr checks N --watch`); merge only when green, using the repo's merge
    convention (regular merge unless the repo says squash; when a local
    skill/command convention conflicts with the user's standing preference,
    surface it once BEFORE the first merge, not after). Confirm any
    irreversible cleanup (deleting remote branches beyond the PR's own,
    force-removing dirty worktrees) with the user instead of folding it into
    a broad "proceed".
11. **Close out.** Close the issue with a substantive comment (evidence, not
    "done"), update project state/memory files with anything reusable
    learned, and clean up artifacts you created.

## Definition of done

Done = merged (or PR open and green, if instructed not to merge), findings
addressed or rejected with reasons, issue closed with evidence. "Code
written" is not done; failing tests are never done (report the failure
output instead). If verification is structurally unavailable (no local
emulator, needs user hardware), run the nearest safe non-mutating substitute,
say exactly what it does and does not cover, and hand the remaining step to
the user as a copy-pasteable command.

## Authorization boundary

Setting up infrastructure that serves no traffic yet (a new database, branch,
draft PR) is yours to do. Any action that changes what a live, external
consumer receives right now (production deploy, publishing a package,
pushing to a live endpoint) is handed to the user as an exact command, even
when you hold the credentials.
