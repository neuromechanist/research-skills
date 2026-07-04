# Numerical and Scientific Debugging

For porting or matching a numerical reference implementation (Fortran/C/CUDA
to Python, one framework to another) and for any "the numbers do not match"
investigation. Distilled from a multi-day ICA-algorithm parity chase that
reached machine-precision agreement.

## 1. Teacher-forced trajectory comparison (build this harness first)

End-to-end metrics conflate three things: initialization differences,
trajectory divergence, and formula bugs. Separate them:

1. Seed BOTH implementations from an identical initialization (use one side's
   own save/load format to inject the other's init).
2. Verify the seeding is airtight before comparing anything else: initial
   transforms agree to near machine precision and iteration-0 objective values
   are identical. If seeding is not airtight, fix that first; every downstream
   comparison is noise until it is.
3. Diff per-iteration trajectories (objective value, parameter norms), not
   just final metrics. Same init + diverging trajectories = per-iteration
   formula or update-order bug. Same init + same trajectory + different final
   basin only happens with stochastic elements; pin them.

## 2. Know the noise floor before calling anything a bug

| Residual scale | Interpretation | Language you may use |
| --- | --- | --- |
| ~1e-16 to 1e-13 | Machine precision agreement | "bit-exact", "machine precision" |
| ~1e-13 to 1e-8 | Float accumulation/summation-order noise (scales with reduction depth) | "matches within float noise" |
| Above the estimated noise floor (e.g. 1e-3 when noise is 1e-8) | A real definitional difference; find the formula divergence | "real discrepancy" |

Estimate the floor for your problem size (accumulation depth, dtype) before
judging any residual. Always print the residual next to the claim. Never use
"bit-exact" for anything above ~1e-13.

## 3. Localization sequence

1. Single-variable toggles: disable optional steps (rescaling, matching,
   preprocessing) one at a time on both sides; record the residual per toggle
   state. This localizes which update carries the discrepancy.
2. Sufficient-statistic parity: compare intermediate quantities (denominators,
   gradients) at one iteration from identical state; a mismatch here names the
   exact formula.
3. Enumerate-and-test candidate formulas: when the reference's convention is
   ambiguous (transpose order, normalization side), implement each candidate
   and report the residual for each; accept the one at machine precision.
   Be exact about signs, factors of 1/2, logs, and which count divides which
   sum; these four account for most porting bugs.
4. After any partial fix, re-run the ORIGINAL end-to-end check. State
   "necessary but not sufficient" when a real bug's fix does not close the
   gap, and continue.

## 4. Is the metric itself well-posed?

Before concluding an unmet target (say, component correlation below 0.95) is a
code defect, run two controls:

- **Exactness control**: one update step from identical state is bit-exact, so
  the math is a faithful port.
- **Self-consistency control**: the implementation vs itself under a harmless
  perturbation (different block size, different thread count). If
  self-consistency also fails the metric, the algorithm has intrinsic
  sensitivity (multiple valid optima, permutation/partition ambiguity,
  basis-dependence) and the metric or its target must change; stop chasing a
  code bug that does not exist.
- Also audit the metric's implementation: correlating quantities in
  incompatible bases, or without permutation matching, is a measurement
  confound, not a finding.

## 5. Reporting and gates

- Tie the acceptance gate to a self-enforcing check where possible: a strict
  expected-failure test on the exact metric and threshold flips to passing
  (and forces its own removal) when parity is reached; prose checklists rot.
- Sample size follows decision weight: a result that flips a keep/kill gate
  must be re-measured at a defensible n before it enters a verdict table; a
  low-n boundary probe (does it OOM at length L?) is fine but must be labeled
  low-n.
- Commit expensive-to-reproduce results (benchmark outputs, sweeps) the moment
  they land, separately from code commits; anything that would take more than
  a few minutes of compute to re-derive should never sit only in a working
  tree.
- When handing off mid-chase, ship a validated re-runnable prototype plus an
  ordered findings doc, and verify the prototype reproduces its claimed
  numbers before calling it a handoff.
- Warn any downstream simplification or refactor pass, explicitly, that float
  operation order and summation order are part of the spec on
  numerically-validated code.
