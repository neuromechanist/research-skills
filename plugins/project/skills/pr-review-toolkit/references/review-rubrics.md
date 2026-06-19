# PR Review Rubrics

Use these lenses independently, then merge duplicate findings. A finding that
appears in multiple lenses should be reported once at the highest appropriate
severity.

## Severity Guide

- Critical: likely breakage, data loss, security exposure, privacy issue, corrupt state, or explicit project rule violation with serious impact.
- Important: user-visible bug, important missing test, reliability issue, API contract risk, or maintainability issue likely to cause defects.
- Moderate: real issue with bounded impact, useful but non-blocking test gap, or clarity issue in touched code.
- Suggestion: optional improvement. Include only when the user asks for broader polish.

## Code Lens

Review for:

- Correctness of changed behavior and edge cases
- API and data contract compatibility
- State management, concurrency, async ordering, and lifecycle bugs
- Security, auth, permissions, secrets, privacy, and injection risks
- Resource leaks, performance regressions, and unbounded work
- Explicit project rule violations
- Missing or misleading validation at boundaries

Filter aggressively. Do not report generic preferences unless tied to a project
rule or defect risk.

## Test Lens

Review for behavioral coverage rather than line coverage.

Flag:

- Changed behavior with no test exercising the new contract
- Error paths or negative cases that can regress silently
- Boundary conditions for parsers, validators, permissions, dates, money, IO, concurrency, or migrations
- Tests that assert implementation details instead of observable behavior
- Tests that cannot fail for the bug they claim to cover
- Removed tests without equivalent coverage

For each gap, explain the specific regression the missing test would catch.
Classify criticality from 1 to 10 when useful:

- 9-10: data loss, security, crash, corrupt state, or core workflow break
- 7-8: important user-visible behavior
- 5-6: meaningful edge case
- 1-4: optional completeness

## Error-Handling Lens

Look for silent failure patterns:

- Empty catch blocks
- Broad catches that swallow unrelated errors
- Logging without user feedback when the user needs to act
- Returning null, undefined, empty data, or defaults on failure without surfacing the failure
- Hidden fallback chains that make behavior hard to explain
- Retry exhaustion without an actionable final error
- Production fallback to mock, fake, fixture, or stub data
- Optional chaining or null coalescing that skips required work

For each issue, state what errors could be hidden, user impact, and the preferred
propagation or feedback path.

## Comment And Documentation Lens

Review changed comments, docstrings, markdown, examples, and public API docs.

Flag:

- Comments that contradict the code
- Parameter, return, type, or error documentation that is stale
- Examples that no longer compile or no longer match behavior
- Comments that restate obvious code while missing the reason for non-obvious choices
- TODO/FIXME notes that are already resolved or too vague to be actionable
- Generated docs updated without the source of truth, when the repo has one

Prefer comments that explain why, constraints, invariants, cross-system contracts,
or non-obvious tradeoffs.

## Type-Design Lens

Use for static types, schemas, models, database shapes, validation objects, config,
protocol messages, and state machines.

Assess:

- Encapsulation: can callers violate internal invariants?
- Invariant expression: are valid states clear from the type shape?
- Invariant usefulness: do the constraints prevent real bugs?
- Enforcement: are construction and mutation boundaries validated?
- Evolution: will the type tolerate expected future fields or states?
- API ergonomics: does the type make correct use easier than incorrect use?

Flag anemic types only when behavior or invariants are important and currently
left to scattered caller discipline. Prefer simple types when extra abstraction
would not reduce real risk.

## Simplification Lens

Use in advisory mode unless the user explicitly asks for edits.

Look for:

- Unnecessary nesting or branching
- Duplicate logic introduced in the change
- Clever expressions that obscure control flow
- Abstractions created before there is meaningful duplication or ownership clarity
- Long functions where extracting a local helper would make the contract clearer
- Names that hide important domain distinctions
- Comments made necessary by unnecessarily complex code

Preserve behavior. Do not reduce clarity just to reduce line count. In edit mode,
make the smallest patch that improves comprehension and run targeted checks.
