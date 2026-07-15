# Fan-Out Prompt Templates

Copy these verbatim and fill the brackets. Every template ends with a report
contract; do not remove it. Distilled from working frontier-model sessions.

## Shared CONTEXT block (paste into every prompt of a wave)

```
CONTEXT: [one-line project description]. Repo map: [packages/dirs and what
each is]. Largest files: [file, N lines; file, N lines]. House rules are in
[AGENTS.md / CLAUDE.md path] and apply strictly.
ALREADY HANDLED (do not re-report): [list of fixed/triaged items].
KNOWN GAPS (extend, do not rediscover): [issue refs].
```

## 1. Explorer / investigator (read-only)

```
You are a READ-ONLY investigator on [repo] (branch [branch]). Do NOT edit any
files. [Shared CONTEXT block]

Goal: [one sentence: what decision this report feeds].

Find and report, with file:line references and short excerpts:
1. [specific file/subsystem]: [specific falsifiable question]
2. [the flow]: how is [X] assembled? Where could [Y] be injected?
3. Whether [assumption] already exists anywhere.
4. Pain points: duplicated types, hardcoded values, TODOs, anything in
   [.context/plan.md] marked unfinished.

Report: a structured summary with file:line references for the load-bearing
facts. Be conclusion-oriented; no file dumps. Send the FULL report as your
final message text (do not write a report file).
```

Scope one explorer per independent subsystem. For a file-decomposition task,
always use at least two with disjoint scopes: one maps the target's internal
structure (symbol inventory with line ranges, module-level state), one maps
external dependents (every importer, test doubles, dynamic imports), and, when
a prior similar change exists, a third reads that merged precedent to mirror.

## 2. Implementer / builder (full lifecycle contract)

```
You are the builder for [issue #N: title] ([repo]). Read the issue first:
`gh issue view N`; it is the spec. [Shared CONTEXT block]

Worktree (work ONLY here, absolute paths):
git -C [/abs/repo] fetch origin [develop]
git -C [/abs/repo] worktree add ../[repo]-issue-N -b fix/issue-N-[slug] origin/[develop]

NEVER read or print .env or any secrets file.
Coordination: agent [name] is concurrently editing [files] on another branch;
do NOT touch those files. Keep your diff minimal and focused.
DECIDED POLICY (lead decision, note it in the PR body): [pre-resolved
ambiguity, exact wording].

Read first, in order: [AGENTS.md], [design doc / ADR], [the file to mirror:
an existing correct pattern for this kind of change].

Deliverables (exact values, no substitutions):
1. [requirement with exact constants/types/thresholds]
2. [requirement]. CRITICAL integration point: [the thing that silently breaks
   if missed]; add the test that proves it did not.

Tests: [named cases to add]. Gates: [format cmd], [lint cmd], [typecheck cmd]
(baseline has [N] pre-existing diagnostics; add ZERO new), [test cmd] green.

Commits: atomic, subject under 50 chars, no emojis, no AI attribution.
Push, open a PR against [base] with `gh pr create` ("Closes #N", what/why/how
tested). GitHub-body exception: keep each paragraph on one source line with
blank lines between paragraphs; do not apply sentence/clause semantic line
breaks inside a paragraph. Do NOT merge.

Report: PR URL, what you implemented, exact test commands and counts, and any
deviations from this brief with reasons. Send as final message text.
```

## 3. Reviewer (risk-class-specific; never a bare "review this PR")

```
Review PR #[P] on [repo]: `gh pr diff P`. Scope: ONLY [these commits/files];
[prior-reviewed parts] are out of scope. Do not modify code; post nothing to
GitHub; report to me only.

Project context: [stack, gates, where house rules live].

The exact risk class of this change: [name the failure mode this diff could
introduce, e.g. "a failure that used to hard-exit now depends on every step
returning FAIL and the sequencer checking every result" or "no transcript or
prompt content may reach logs; counts, durations, and paths only"]. Hunt
specifically for: [enumerated known failure modes of that class].

Report findings by severity (Critical / Important / Suggestion), each with
file:line and a one-line proposed fix. Only report issues you are confident
about; skip style nits the linter already enforces. Send the full report as
your final message text.
```

For security-relevant paths, brief a second reviewer specifically on input
variants (encodings, nesting, type confusion) that the first fix may have
missed. For simplification passes on numerically validated code, add:
"Do NOT suggest changes that alter float summation order, operation order, or
numerical results; parity is the spec."

## 4. Review synthesis and dispatch (to the same implementer, by name)

```
The [N]-agent review of PR #[P] is done: [one-line verdict]. Every finding
below gets addressed or explicitly rejected. Fix in your worktree, re-run all
gates (zero new diagnostics vs baseline), commit atomically, push. Do NOT
merge.

1. CRITICAL: [file:line]: [bug mechanism]. Fix: [exact fix].
2. IMPORTANT: ...
3. COMMENT FIX: [stale doc claim].
4. NO ACTION (logged): [finding]: belongs to #[M]; add one sentence to the
   PR body and a comment on #[M]. Keep every GitHub paragraph on one source
   line; use blank lines only between paragraphs.
EXPLICITLY REJECTED (rationale): [finding]: [one sentence why].

Reply with: commit hash, test counts, and anything you disagreed with and why
(argued disagreement is fine; "intentionally different by design" is an
accepted resolution).
```

After the fix-up commit, request a focused delta verification of just that
commit, not a full re-review.

## 5. Idle nudge (agent went idle without delivering)

```
You went idle but I never received your report. Send your complete
[deliverable] now via SendMessage to "[lead name]". Send the FULL content,
not a summary; split into consecutive messages if long. If your earlier
findings are gone from context, re-derive them from [the files/paths].
```

## 6. Correction broadcast (a claim you made earlier was wrong)

```
Important correction that affects your work; incorporate it now.
THE ERROR: I told you "[exact wrong claim]". That is WRONG. I re-verified
against [source, file:line]: [correct fact].
REWORK FOR YOU SPECIFICALLY: [exact, minimal instructions; state what does
NOT change].
Acknowledge and confirm what you changed.
```

## 7. Stand-down

```
[Task] is complete on my side: [specific commit/PR/merge state that
supersedes further work]. Nothing further needed; you can stand down. Thanks
for [something specific they did well].
```

If an incoming message is a duplicate of one already handled, reply
"Confirmed duplicate delivery; nothing further needed" instead of ignoring it
or redoing work.
