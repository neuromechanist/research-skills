# Git

- Keep commits atomic and focused.
- Use branch names that describe the work:
  - `feature/<short-description>` for new capabilities.
  - `patch/<short-description>` for fixes.
  - `chore/<short-description>` for maintenance.
- Do not use a `codex/` branch prefix.
- Do not add AI attribution in commits.
- Do not use emojis in commits, PR titles, code, or generated metadata.
- Never reset, checkout, or revert user changes unless the user explicitly asks.
- Before summarizing work, check `git status` and distinguish your changes from
  pre-existing dirty files.
- Prefer non-interactive git commands.
