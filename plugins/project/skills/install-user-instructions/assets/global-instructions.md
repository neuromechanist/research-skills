## General agent defaults

### Task strategy and model routing

- Keep requirements, architecture, difficult judgment, observation, supervision, load-bearing verification, and final synthesis on the strongest available model.
- On Claude Code, use Fable when available or Opus for lead reasoning, and Sonnet for implementation from an approved detailed plan.
- On OpenAI Codex, use Sol for lead reasoning, Terra for bounded phase-plan elaboration after architecture approval, and Luna for clear, repeatable implementation, focused tests, routine review, and validation.
- On Copilot, Cursor, or another system, preserve the same capability classes: strongest lead, intermediate elaborator, and cost-efficient worker.
- Give workers exact file scope, decided policies, acceptance criteria, named tests, and mechanical gates. Escalate unresolved architecture, repeated non-mechanical failures, data integrity, encryption, concurrency, authorization, and other high-risk invariants to the lead model.
- After incorporating an agent's final report, close or remove the agent unless it has a named recurring role and a concrete next task. Do not retain completed agents merely because they might be reused later.

### Instruction scope

- Keep reusable personal preferences in this user-level file.
- Keep repository facts, build commands, architecture, and team conventions in the repository's AGENTS.md.
- Keep tool-specific project files limited to tool-specific deltas. For Claude Code, import AGENTS.md from CLAUDE.md instead of copying the shared rules.

### Prose source and GitHub bodies

- Use semantic line breaks in Markdown, LaTeX, and other prose source: break at sentence boundaries and, when useful, at clause punctuation. Preserve blank lines for paragraph boundaries.
- GitHub issue and pull-request bodies are the exception. Keep each paragraph on one source line, separate paragraphs with blank lines, and do not insert sentence- or clause-level newlines inside a paragraph.

### Delivery discipline

- Make the smallest coherent change, preserve unrelated user work, and verify behavior with the project's real format, lint, type, and test gates.
- Surface unresolved decisions and failed checks explicitly. Do not weaken tests, hide diagnostics, or claim completion while required verification is failing.
