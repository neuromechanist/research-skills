# PR Review Procedure

Use this procedure for PRs, branch diffs, staged changes, unstaged changes, and
targeted file reviews.

## 1. Establish Scope

Prefer the narrowest scope that matches the user request.

- Explicit PR: inspect `gh pr view` and `gh pr diff`.
- Current branch PR: try `gh pr view`; if absent, compare against the detected integration branch.
- Staged review: use `git diff --cached`.
- Unstaged review: use `git diff`.
- Recent local work: inspect `git status --short`, then both staged and unstaged diffs.
- Explicit files: inspect only those files and the relevant diff hunks.

If scope is ambiguous and choosing wrong could waste time or cause false
findings, ask a short clarification. Otherwise review the current branch changes.

## 2. Load Project Rules

Read the nearest available rule sources before making style claims:

- `AGENTS.md`
- `CLAUDE.md`
- `.rules/*.md`
- framework-specific docs already present in the repo
- package scripts and test commands when verification matters

Separate explicit rule violations from optional style suggestions.

## 3. Select Lenses

Apply user-requested lenses first. If the user requests `all` or does not specify
lenses, apply:

- `code` always
- `tests` when behavior changed, tests changed, or test coverage is requested
- `errors` when error handling, fallbacks, IO, network, parsing, auth, persistence, or async paths changed
- `comments` when comments, docs, docstrings, READMEs, generated docs, or public API docs changed
- `types` when public types, schemas, models, enums, validation boundaries, or state machines changed
- `simplify` when code works but is complex, or the user asks to refine/simplify

## 4. Inspect Diffs Before Whole Files

Start from changed hunks, then open surrounding code only as needed. Prefer
high-signal commands:

```bash
git status --short
git diff --stat
git diff --check
git diff --cached --stat
git diff --cached --check
```

Use `rg` for dependency and call-site checks. Do not review the whole repository
unless the user requests it or the changed contract requires call-site analysis.

## 5. Calibrate Findings

Report only actionable issues:

- Bugs and behavioral regressions
- Data loss, security, privacy, or reliability risks
- API contract breaks
- Missing tests for changed behavior
- Explicit project rule violations
- Misleading comments or docs
- Silent failures or hidden fallbacks
- Type designs that permit invalid states in important code paths

Avoid low-signal nits, cosmetic preferences, and broad refactors unless they
materially reduce risk.

## 6. Verification

Run relevant checks when the request includes implementation, when findings
depend on test behavior, or when the project has a cheap targeted command. If a
command cannot run, report why.

For advisory review only, do not edit files. For simplify or fix mode, patch the
minimal scope and verify with the closest available test.

## 7. Output Format

Lead with findings, ordered by severity.

Each finding must include:

- Severity
- File and line
- What is wrong
- Why it matters
- Concrete fix direction

Use this shape:

```markdown
**Findings**
- Critical: [file:line] Description. Impact. Fix.
- Important: [file:line] Description. Impact. Fix.
- Moderate: [file:line] Description. Impact. Fix.

**Questions**
- Only include questions that change the review outcome.

**Residual Risk**
- Mention skipped checks, unrun tests, or areas outside scope.
```

If there are no actionable findings, say that clearly and still include any
remaining test gaps or verification limits.
