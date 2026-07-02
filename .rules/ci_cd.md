# CI/CD

- Use CI as a fast quality gate: lint, type check when configured, test, then
  build or package validation.
- Python CI should use `astral-sh/setup-uv` and run commands through `uv`.
- JavaScript and TypeScript CI should use `oven-sh/setup-bun` and run commands
  through Bun.
- Keep CI checks aligned with local commands documented in `AGENTS.md` and
  `.rules/`.
- Do not add workflows that depend on unavailable secrets or services without
  documenting the required setup.
- Prefer focused validation jobs for this marketplace:
  - JSON manifest parsing.
  - TOML template parsing.
  - Skill validation for new or changed skills.
  - Marketplace integrity tests.
