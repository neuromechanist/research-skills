# Card <ID>: <title>

Status: ready
Tier: worker
Timebox: <size and duration, e.g. M, 1 day; escalate at 2 days or two failed approaches>
Needs: <capabilities, e.g. browser; or none>
Depends: <step IDs, or none>
Branch: feature/issue-<n>-<slug>
Worktree: <absolute path>
Plan: <plan path and section>

## Goal

<One sentence: the observable outcome when this card is done.>

## Context

<What to read first, with paths. Facts the worker cannot derive. Live facts are added by the manager at dispatch.>

## Scope

<Files and directories this card may change. Everything else is out of scope.>

## Decided design

Settled: <every design decision the lead made, with exact values>.
The implementer may choose: <the only freedoms left>.

## Acceptance

<Literal commands and thresholds, each in backticks, e.g. `uv run pytest tests/test_store.py -q` passes with the two new tests.>

## Gates

<The project's mechanical gates, e.g. `uv run ruff check . && uv run ty check && uv run pytest -q`, with zero new diagnostics against the measured baseline.>

## Stop conditions

<When to stop and report instead of continuing, e.g. a registered design looks wrong, a gate fails twice for a non-mechanical reason, the change needs a file outside Scope.>

## Report

Your final message is the report, at most 25 lines: PR number and head SHA; gates run with their quoted last lines; evidence paths; a revert check per fix; deviations from this card; questions for the lead; patch notes for other owners.
