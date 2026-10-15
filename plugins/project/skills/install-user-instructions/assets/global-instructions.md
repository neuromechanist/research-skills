## General agent defaults

### Task strategy and model routing

- Keep requirements, architecture, difficult judgment, observation, supervision, load-bearing verification, and final synthesis on the strongest available model, directly or by delegation from a Sonnet or Luna driver.
- On Claude Code, use Fable when available or Opus for lead reasoning, and Sonnet for implementation from an approved detailed plan.
- On OpenAI Codex, use Sol for lead reasoning, Terra for bounded phase-plan elaboration after architecture approval, and Luna for clear, repeatable implementation, focused tests, routine review, and validation.
- When the session itself runs on Sonnet or Luna, act as a mechanical driver: delegate routine work to Sonnet (`xhigh`) or Luna (`max`), and architecture, high-risk invariants, and contested findings to Opus or Sol (`xhigh`).
- On Copilot, Cursor, or another system, preserve the same capability classes: strongest lead, intermediate elaborator, and cost-efficient worker.
- Give workers exact file scope, decided policies, acceptance criteria, named tests, and mechanical gates. Escalate unresolved architecture, repeated non-mechanical failures, data integrity, encryption, concurrency, authorization, and other high-risk invariants to the lead model.
- After incorporating an agent's final report, close or remove the agent unless it has a named recurring role and a concrete next task. Do not retain completed agents merely because they might be reused later.

### Instruction scope

- Keep reusable personal preferences in this user-level file.
- Keep repository facts, build commands, architecture, and team conventions in the repository's AGENTS.md.
- Keep tool-specific project files limited to tool-specific deltas. For Claude Code, import AGENTS.md from CLAUDE.md instead of copying the shared rules.

### Prose source and GitHub text

- Use semantic line breaks in Markdown, LaTeX, and other prose source: break at sentence boundaries and, when useful, at clause punctuation. Preserve blank lines for paragraph boundaries.
- Text posted to GitHub (issue and pull-request bodies, comments, reviews, and discussions) is the exception, because GitHub renders every single newline there as a line break. Keep each paragraph and list item on one source line, separate paragraphs with blank lines, and do not insert sentence- or clause-level newlines inside a paragraph.

### Pull requests and CI

- Review each PR at most twice: one full review, then one review of the fix commits only if the findings or fixes were substantial. Never a third round.
- Fix review findings with commits on the same PR branch, pushed once per round. Use a separate fix PR, targeting the PR's head branch, only for a large fix or when that branch blocks direct pushes (one fix PR per round). Never merge before the review returns.
- Give every finding one outcome: fixed, rejected with a reason, or filed as an issue (only for code the PR did not touch). Resolve accepted findings before merging; never defer them to a follow-up PR or the next release.
- Scope CI: trigger on pull requests and pushes to integration branches, path-filter by what each workflow checks, cancel superseded runs, and set job timeouts. Add `[skip ci]` to commits that touch only files no CI job reads. Bump versions inside the PR or at release; a post-merge bot bump carries `[skip ci]`, alone in its push to the integration branch (unless that branch heads a release PR, where the marker silences required checks; then skip inside a gate job), and the same workflow deploys once from the bumped commit. One merge deploys once per environment.
- Every wait has a limit and a next action. Do not re-ask, re-review, or restart a step to get unstuck.

### Delivery discipline

- Make the smallest coherent change, preserve unrelated user work, and verify behavior with the project's real format, lint, type, and test gates.
- Surface unresolved decisions and failed checks explicitly. Do not weaken tests, hide diagnostics, or claim completion while required verification is failing.
