# Core Development Principles

These principles are enforced by the vibe-rules templates. They apply to all projects initialized with init-project.

## NO MOCKS - Test Reality Only

Real bugs hide at integration points, not in unit logic. Mocks test your assumptions, not your code.

**Rules:**
- Never use mocks, stubs, or fake data in tests
- Use real databases (Docker for test databases)
- Use actual API connections (or skip the test)
- Use real file systems with test fixtures
- If real testing is impossible, ask the user for sample data or environment access
- Better to skip a test entirely than write a misleading mock-based test

**Rationale:** A passing mock test gives false confidence. When mocked tests pass but production fails, the cost is much higher than not having the test at all.

## Atomic Commits

Each commit should contain exactly one logical change that can be understood in isolation.

**Rules:**
- Messages must be <50 characters, no emojis, no AI attribution
- Types: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Feature branches: `feature/short-description`
- Never force-push to shared branches
- Squash merge for features, rebase to update branches

## Documentation-Driven Development

All projects use a standardized `.context/` directory with four files that track the project's evolving state.

**Files:**
- `plan.md` - Task tracking with phases (pending, in progress, complete)
- `research.md` - Technical solutions, approaches, and references discovered
- `ideas.md` - High-level concepts, design decisions, architectural ideas
- `scratch_history.md` - Failed attempts, lessons learned, anti-patterns to avoid

## No Technical Debt Carried Forward

Address ALL PR review findings, not just critical ones. Only skip findings that are genuine false positives or intentionally different by design.

**Rules:**
- Replace, do not deprecate
- No `TODO` without a linked issue
- No commented-out code (git has history)
- No `# type: ignore` without explanation
- No empty catch blocks or silent failures

## Tool Consistency

Standardize on specific tools across all projects to avoid configuration drift.

| Domain | Tool | Never use |
|--------|------|-----------|
| Python packages | UV | pip, conda, virtualenv |
| Python linting | Ruff | pylint, flake8, black |
| Python types | Ty | mypy |
| JS/TS packages | Bun | npm, npx |
| JS/TS linting | Biome | eslint, prettier |

## Rule Evolution

Rules are living documents. Extract patterns into rules when used 3+ times. Mine failures from scratch_history.md into prevention rules. Mine successes from research.md into best practices.
