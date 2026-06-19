# Rule Evolution

- Add or update rules when a pattern appears repeatedly, a review finding should
  become a prevention rule, or a tool/platform behavior changes.
- Keep `AGENTS.md` concise. Put detailed operating rules in `.rules/*.md` and
  link to them from AGENTS.
- Rules should be actionable, specific, and grounded in this repo's real
  workflows.
- Do not overwrite local project conventions with generic templates. Merge only
  the parts that improve this repository.
- When changing marketplace or plugin behavior, update the relevant docs and
  tests so future agents can verify the rule mechanically.
