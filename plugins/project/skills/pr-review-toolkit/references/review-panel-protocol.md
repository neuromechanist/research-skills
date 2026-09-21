# Bounded Review Panel Protocol

This protocol defines the automatic Codex path for `project:pr-review-toolkit`.
It is a bounded dispatch policy, not a second review rubric. Every reviewer
still loads `review-procedure.md` and `review-rubrics.md`.

## Dispatch gate

Before dispatching, run the read-only startup probe:

```bash
<project-plugin-root>/bin/project-preflight --format json
```

Use the panel only when all of these are true:

1. the scope is `all` (the default) or the caller explicitly requests a
   pre-merge review;
2. `native_agent_status` is `available`;
3. the caller has not selected `single`, `inline`, or another opt-out; and
4. the requested work is not an advisory review of one named lens.

If any condition is false, run the single inline procedure or the explicitly
configured single reviewer. Optional capability failure is a fallback reason,
not a review error.

## Default panel

The default panel is at most three fresh reviewers. Do not exceed the configured
`agent_max_reviewers` budget from preflight or a caller-supplied lower cap.
Group the six lenses into risk-focused briefs:

| Reviewer | Lenses | Brief |
|---|---|---|
| `contract` | `code`, `types` | Find behavioral, API, security, and invariant breaks introduced by the diff. |
| `verification` | `tests`, `errors` | Find missing behavioral coverage, silent failures, bad fallbacks, and unverified negative paths. |
| `maintainability` | `comments`, `simplify` | Find stale public documentation, misleading rationale, and complexity that can cause defects. |

Use **Codex `gpt-5.6-luna` at `max` effort** for these reviewers by default.
On Claude surfaces use **Sonnet at `xhigh`** by default. A user-supplied model,
effort, panel size, lens, or single/inline choice always overrides this policy.
Do not route routine reviews to Sol, Terra, or Astra.

Each brief must include the changed range, project rules, the assigned lenses,
the specific risk class, a confidence filter, and a request for no more than
five findings. Reviewers are read-only and must not create commits, messages,
PRs, or merges.

## Report contract

Each reviewer returns one structured report:

```json
{
  "reviewer_id": "contract",
  "status": "completed",
  "lenses": ["code", "types"],
  "findings": [
    {
      "severity": "Important",
      "file": "path/to/file.py",
      "line": 42,
      "problem": "...",
      "impact": "...",
      "fix": "...",
      "confidence": "high"
    }
  ],
  "checks": ["..."],
  "residual_risk": "..."
}
```

An unavailable or timed-out reviewer returns `status: "unavailable"` with an
error summary. The orchestrator must account for every dispatched reviewer
rather than silently drawing conclusions from a partial panel.

## Synthesis and cleanup

The lead deduplicates findings by normalized file, line range, and failure
claim. It independently verifies every finding that could block a merge, then
marks each finding `accepted` or `rejected` with a one-sentence reason. The
final toolkit report retains the existing findings-first shape and includes:

- dispatched reviewer IDs, lens groups, and statuses;
- accepted findings ordered by severity;
- rejected duplicates or false positives with reasons;
- checks run and residual risk;
- cleanup confirmation for every completed one-off reviewer.

The orchestrator must account for every finding and close completed agents.
Never silently drop a reviewer, a finding, or a failed capability probe.
