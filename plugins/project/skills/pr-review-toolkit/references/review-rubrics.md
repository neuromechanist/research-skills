# PR Review Rubrics

Use these lenses independently, then merge duplicate findings.
A finding that appears in multiple lenses is reported once, at the highest appropriate severity.
Lens content tracks Anthropic's upstream `pr-review-toolkit` agents (v1.0.1); see the Attribution section of `SKILL.md`.

## Severity Guide

- Critical: likely breakage, data loss, security exposure, privacy issue, corrupt state, or explicit project rule violation with serious impact.
- Important: user-visible bug, important missing test, reliability issue, API contract risk, or maintainability issue likely to cause defects.
- Moderate: real issue with bounded impact, useful but non-blocking test gap, or clarity issue in touched code.
- Suggestion: optional improvement. Include only when the user asks for broader polish.

## Confidence Filter

Score each candidate finding from 0 to 100 before reporting it:

- 0-25: likely false positive, or pre-existing and untouched by the change.
- 26-50: nitpick not backed by an explicit project rule.
- 51-75: valid but low impact.
- 76-90: important issue requiring attention.
- 91-100: confirmed bug or explicit project-rule violation.

Report only findings scored 80 or higher.
Critical findings normally score 90 or higher; Important findings 80 or higher.
Moderate and Suggestion items still need 80 confidence that the issue is real; the score measures certainty, not impact.
Skip style nits a configured linter or formatter already enforces.

## Code Lens

Review for:

- Correctness of changed behavior and edge cases, including null, undefined, and empty inputs
- API and data contract compatibility
- State management, concurrency, async ordering, race conditions, and lifecycle bugs
- Security, auth, permissions, secrets, privacy, and injection risks
- Resource and memory leaks, performance regressions, and unbounded work
- Explicit project rule violations (import patterns, framework conventions, naming, logging, error handling, testing practice, platform compatibility); cite the rule
- Missing or misleading validation at boundaries
- Duplication introduced by the change, missing critical error handling, and accessibility problems in user-facing UI

Filter aggressively.
Do not report generic preferences unless tied to a project rule or defect risk.
For each finding, give the rule or bug explanation and a concrete fix.

## Test Lens

Review for behavioral coverage rather than line coverage.

Flag:

- Changed behavior with no test exercising the new contract
- Error paths or negative cases that can regress silently
- Boundary conditions for parsers, validators, permissions, dates, money, IO, concurrency, async behavior, or migrations
- Tests that assert implementation details instead of observable behavior, or that would break under a reasonable refactor
- Tests that cannot fail for the bug they claim to cover
- Removed tests without equivalent coverage
- Integration points whose coverage no test owns

Before flagging a gap, check whether an existing unit or integration test already covers it.
Do not ask for tests of trivial getters, setters, or pass-through code without logic.
Prefer tests that read as descriptive and meaningful phrases (DAMP) over terse shared-setup tests when clarity is at stake.
For each gap, name the specific regression the missing test would catch and weigh its cost against that benefit.
Classify criticality from 1 to 10 when useful:

- 9-10: data loss, security, crash, corrupt state, or core workflow break
- 7-8: important user-visible behavior
- 5-6: meaningful edge case
- 1-4: optional completeness

## Error-Handling Lens

Locate every error-handling site in the change: try/catch or try/except blocks, Result or error returns, error callbacks and event handlers, error-state branches, fallbacks and defaults used on failure, log-and-continue sites, and optional chaining or null coalescing that may skip work.

Flag silent failure patterns:

- Empty catch blocks (never acceptable)
- Broad catches that swallow unrelated errors; list the unexpected error types each one could hide
- Errors caught locally that should propagate to a higher-level handler, or catches that skip cleanup or resource release
- Logging without user feedback when the user needs to act
- Logs without enough context (operation, identifiers, relevant state) to debug the failure months later, or without the project's error-tracking ID when the project defines one
- Returning null, undefined, empty data, or defaults on failure without surfacing the failure
- Fallbacks not requested by the user or documented in the spec, and hidden fallback chains that make behavior hard to explain
- Retry exhaustion without an actionable final error
- Production fallback to mock, fake, fixture, or stub data
- Failures "fixed" by disabling a test, bypassing a check, or suppressing the error

For user-facing error messages, check that each one says what went wrong in terms the reader understands, gives an actionable next step, is specific enough to tell it apart from similar errors, and names the relevant file or operation.

For each issue, state the hidden errors, the user and debugging impact, and the preferred propagation or feedback path, with a short corrected example when it helps.

## Comment And Documentation Lens

Review changed comments, docstrings, Markdown, examples, and public API docs.
Read each one as a maintainer arriving months later without the authoring context.
This lens is advisory: report and suggest; do not edit unless edit mode was granted.

Flag:

- Comments that contradict the code: signatures, parameters, return types, referenced symbols, described behavior, handled edge cases, or complexity claims
- Parameter, return, type, or error documentation that is stale
- Examples that no longer compile or no longer match behavior
- Missing context the reader needs: critical assumptions or preconditions, non-obvious side effects, important error conditions, the approach of a complex algorithm, or the rationale for non-obvious business logic
- Comments that restate obvious code; recommend removal with a one-line rationale
- Comments tied to temporary states or transitional implementations that will rot
- Ambiguous wording that admits more than one reading
- TODO/FIXME notes that are already resolved or too vague to be actionable
- Generated docs updated without the source of truth, when the repo has one

Prefer comments that explain why, constraints, invariants, cross-system contracts, or non-obvious tradeoffs.
Group findings as inaccurate (Critical or Important), improvement opportunities, and recommended removals.

## Type-Design Lens

Use for static types, schemas, models, database shapes, validation objects, config, protocol messages, and state machines.

First list each type's invariants: data consistency requirements, valid state transitions, relationships between fields, encoded business rules, and pre- and postconditions.
Then rate each new or substantially changed type from 1 to 10 on:

- Encapsulation: are internals hidden, and can callers violate invariants from outside?
- Invariant expression: are valid states clear from the type shape, enforced at compile time where feasible?
- Invariant usefulness: do the constraints prevent real bugs without being too restrictive or too permissive?
- Enforcement: are invariants checked at construction, and is every mutation point guarded?

Also consider evolution (will the type tolerate expected future fields or states?) and ergonomics (does it make correct use easier than incorrect use?).

Flag these anti-patterns:

- Exposed mutable internals
- Invariants enforced only by documentation or by external caller discipline
- Missing validation at construction boundaries
- Inconsistent enforcement across mutation methods
- Types with too many responsibilities
- Anemic types, only when behavior or invariants are important and currently scattered across callers

Prefer making illegal states unrepresentable, compile-time guarantees over runtime checks, and immutability where it simplifies invariants.
Weigh each suggestion's complexity, breaking-change, and performance cost against the risk it removes; prefer simple types when extra abstraction would not reduce real risk.

## Simplification Lens

Use in advisory mode unless the user explicitly asks for edits.
Scope is the code the change touched, unless the user asks for broader scope.

Look for:

- Unnecessary nesting or branching
- Nested ternary operators; prefer `if`/`else` chains or a `switch`/`match`
- Duplicate logic introduced in the change, and redundant code or abstractions
- Clever expressions or dense one-liners that obscure control flow
- Abstractions created before there is meaningful duplication or ownership clarity
- Long functions where extracting a local helper would make the contract clearer
- Names that hide important domain distinctions
- Comments that restate obvious code, or that complex code made necessary

Guard against over-simplification: do not merge separate concerns into one function, remove abstractions that aid organization, or trade readability for fewer lines.
Preserve behavior exactly; explicit code beats compact code.
In edit mode, apply the project's own standards, make the smallest patch that improves comprehension, run targeted checks, and summarize only changes that affect understanding.

## Seam Lens

Use for integration reviews: an epic branch after its phase PRs merged, or a `dev` to `main` (integration to release) promotion.
The full procedure, inputs, checklist, and verdict live in `seam-review.md`; read it whenever this lens is selected.
The seam lens does not repeat per-PR line-level review; it reviews goals, cross-PR interfaces, and documentation truth across the whole integrated range.
