---
name: debugging
description: "Use this skill when the user asks to \"debug\", \"find the root cause\", \"figure out why X fails\", \"investigate this bug\", \"this test is flaky\", \"the build broke\", \"production incident\", \"why is the output wrong\", or when any observed behavior contradicts expected behavior. Covers the reproduce-isolate-prove-fix-verify loop, anti-shortcut gates, and numerical/scientific debugging."
---

# Debugging

A disciplined root-cause loop. The goal is a stated causal mechanism with
proof, then a fix verified by the exact check that first exposed the problem.
Never fix by guessing, and never make a symptom disappear without knowing why.

## The loop

1. **Reproduce.** Run the failing thing yourself and capture the exact error,
   command, and environment. If you cannot reproduce, stop and gather the
   reporter's exact conditions; do not fix blind. Side observations found on
   the way get noted and set aside, not chased.
2. **Trace the intended path.** Before reading logs, read the code/docs to
   state what SHOULD happen, step by step. You cannot recognize the broken
   step without knowing the intended sequence.
3. **Check live state.** What is actually on disk, in the database, running as
   a process, deployed? A grep that finds no trace of a migration is not proof
   it never ran; completed one-off scripts are routinely deleted. Absence in
   code is not absence in reality.
4. **Find the smoking gun.** Logs, CI runs, git history. Cheapest checks
   first: installed version vs latest, the artifact's own declared type or
   config, the library's supported list. Only conclude "unsupported" or
   "impossible" after checking the declared capability directly.
5. **Prove the mechanism.** Confirm with a live probe, not log trust (example:
   the blob that returned 403 in the failing run returns 200 now, so it was a
   permission-timing issue, not missing data). A differential test beats an
   assumption: when two configurations should differ, run both and compare.
6. **Only now read source for the WHY**, and state the cause in one sentence
   with the evidence that proves it, plus what changes AND what deliberately
   does not change because it was not the cause.
7. **Fix**, minimally. Fix the upstream cause, not the symptom (a service that
   dies when the machine sleeps needs the sleep addressed, not a restart
   loop).
8. **Verify with the original failing check**, unchanged. Then run the wider
   gates (tests, lint, typecheck). Add a regression test that would have
   caught this bug. If recovery of live state was part of the fix, its success
   doubles as diagnosis confirmation.

## Isolation techniques (when the cause is entangled)

- **Single-variable toggles**: flip one factor at a time (feature flag, config
  bit, environment) and record the result per state. Never attempt a compound
  fix while two candidate causes are still entangled.
- **Necessary-but-not-sufficient check**: after any partial fix, re-run the
  original failing check. The first improving number is not proof of a
  complete fix; say "necessary but not sufficient" and keep going.
- **Ranked compounding causes**: many incidents have several contributing
  causes (stale binary + lost race + shared timeout). Enumerate and rank them;
  do not stop at the first plausible one.
- **Confound check**: before concluding "the fix did not work" or "the test is
  wrong", look for an independent confound (a second process racing the test,
  a hook rewriting the file). Re-run clean.
- **Instrumentation-first for weird results**: a flat or extreme result that
  fails to discriminate across conditions that should matter is an
  instrumentation bug until a targeted, isolated reproduction says otherwise.
  Do not report it as a finding, and do not let it block unrelated work while
  you wait to reproduce it.
- **Doc-vs-code conflicts**: when documentation (or an Architecture Decision
  Record) and code disagree, determine the actual source of truth
  empirically (test the code), then fix whichever artifact is wrong, making
  the fix more precise about where the invariant is enforced. Never silently
  pick a side.

## Anti-shortcut gates (hard rules)

- Never delete, skip, or loosen a failing test to make a suite pass. If a test
  is genuinely wrong, prove it (git history: did the tested thing move or
  disappear?) and say so explicitly.
- Never add a broad catch, silent fallback, or retry loop to make a symptom
  disappear. That converts a loud bug into a silent one.
- Never weaken a designated safety mechanism (rate limit, halt, permission
  gate) because it fired. When a guardrail fires during a bad outcome, the
  default hypothesis is that the new code is incompatible with a correct
  guardrail. Changing the guardrail requires separate, explicit user sign-off.
- Never read or print secrets (.env contents, tokens) while debugging
  credential or environment issues; test credentials differentially instead
  (call the API with each and compare behavior).
- Retry a flaky operation at most once under changed conditions. If it fails
  again under conditions you believe clean, stop retrying and surface a
  structural hypothesis instead.

## Verification is layered

An automated check passing covers only what that check was built to detect.
Before declaring a generated or visual artifact done, do one perceptual/manual
pass for defect classes the validator cannot see (label collisions,
off-canvas content, semantic errors). If the ideal verification is
structurally unavailable, run the nearest safe non-mutating substitute and
state exactly what it does and does not cover; never report "verified"
against a silently downgraded check.

## Numerical and scientific code

For parity work against a reference implementation, tolerance judgment, and
trajectory comparison, read `references/numerical-debugging.md` before
starting. Summary of its hard rules: compare from identical initialization,
know the float noise floor before calling a residual a bug, reserve
"bit-exact" for residuals at machine precision, and test whether the metric
itself is well-posed before chasing an unmet target.

## When to stop

- Root cause stated in one sentence, with cited evidence.
- Fix verified by the original failing check plus the standard gates.
- Regression test added (or an explicit reason why not).
- If the investigation dead-ends: document it (goal, issue, root cause if
  known, lesson, alternative) in the project's scratch/history notes and the
  issue tracker; a documented dead end is a valid outcome, a silent one is
  not.
- If you are deep in a long session and the remaining fix is risky, prefer a
  validated, independently re-runnable handoff artifact (script plus ordered
  notes, verified to run) over a rushed multi-file edit.
