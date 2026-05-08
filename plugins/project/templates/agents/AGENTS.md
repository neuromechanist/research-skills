# {{PROJECT_NAME}} Instructions

## Project Context
**Purpose:** [Brief description of what you're building]
**Tech Stack:** [Languages, frameworks, key dependencies]
**Architecture:** [Key design decisions]

## Architecture Map
```
src/
├── core/          # [Purpose]
├── api/           # [Purpose]
├── models/        # [Purpose]
├── utils/         # [Purpose]
└── tests/         # Real tests only
```

## Environment Setup
```bash
# Python projects
uv sync          # Install dependencies
uv run pytest    # Run tests

# JS/TS projects
bun install      # Install dependencies
bun test         # Run tests
```

## Development Workflow
1. **Check context:** Review .context/plan.md for current tasks
2. **Understand deeply:** Check .context/ideas.md for design decisions
3. **Research if needed:** Update .context/research.md with findings
4. **Branch:** `gh issue develop <issue-number>`
5. **Code:** Follow patterns (see .rules/ for standards)
6. **Test:** Real data only (see .rules/testing.md)
7. **Document failures:** Log in .context/scratch_history.md immediately
8. **Commit:** Atomic, <50 chars, no emojis
9. **PR:** Reference context and issue
10. **Code review:** Run `/review-pr` after creating PR (see .rules/code_review.md)

## [CRITICAL] Core Principles - Never Compromise

### [FUNDAMENTAL] NO MOCKS - Test Reality Only
- Use real data or skip tests entirely
- Docker for test databases
- Ask user for sample data if needed
**Details:** .rules/testing.md

### Commits & Git
- Atomic commits, focused changes
- Messages <50 chars, no emojis, no AI attribution
- Feature branches for multi-step work
**Details:** .rules/git.md

### No Technical Debt Carried Forward
- Address ALL PR review findings
- Only skip genuine false positives or intended design choices
- Replace, don't deprecate
**Details:** .rules/code_review.md

### Documentation
- Examples > explanations
- README gets someone running in <5 minutes
**Details:** .rules/documentation.md

## [NEVER DO THIS]
- Never use mocks, stubs, or fake data in tests
- Never use `pip`, `conda`, or `virtualenv`; use UV for Python
- Never use `npm` or `npx`; use Bun for JS/TS
- Never commit secrets, .env files, or credentials
- Never leave empty catch blocks or silent failures
- Never add backward-compatibility shims; replace directly
- Never add TODO without a linked issue

## Think Like a Senior Developer
- Keep the big picture in mind
- Ask: "Will this prevent a 3am wake-up call?"
- Document learnings in .context/scratch_history.md
- Extract patterns (3+ uses) into rules
**See:** .rules/self_improve.md for learning process

## [REFERENCE] Rules Directory

### Core Standards
- `.rules/testing.md` - Complete NO MOCK policy
- `.rules/self_improve.md` - Learning from projects
- `.rules/documentation.md` - MkDocs setup
- `.rules/code_review.md` - PR review toolkit and checklist

### Language & Tools
- `.rules/python.md` - UV, ruff, ty
- `.rules/ci_cd.md` - GitHub Actions setup
- `.rules/{{framework}}.md` - Framework patterns

### MCP Tools (When Available)
- `.rules/serena_mcp.md` - Code intelligence with Serena MCP

## Context Files
- `.context/plan.md` - Current tasks and phases
- `.context/research.md` - Technical explorations
- `.context/ideas.md` - Design concepts
- `.context/scratch_history.md` - Failed attempts

## Quick Commands
```bash
# Python
uv run pytest tests/ --cov       # Run tests
uv run ruff check --fix . && uv run ruff format .  # Lint + format

# JS/TS
bun test                         # Run tests
bun run biome check --fix .      # Lint + format

# Docs
uv run mkdocs serve              # Build docs
```

## Project-Specific Guidelines
[Add custom requirements here]
[Team conventions]
[Special considerations]

---
Remember: You're building maintainable systems, not just writing code.
Check .rules/ for detailed guidance on any topic.
