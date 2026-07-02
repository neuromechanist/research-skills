# Documentation

- Keep docs and README content aligned with the source of truth in manifests,
  skills, agents, and `.rules/`.
- When changing plugin registration, update:
  - `README.md` for user-facing install and capability notes.
  - `AGENTS.md` for concise repo guidance.
  - `docs/cross-agent-compatibility.md` for researched platform behavior and
    source links.
  - `.rules/cross-agent-compatibility.md` when the policy itself changes.
- Attribute adapted external ideas in README or docs when requested or when the
  implementation is intentionally based on upstream work.
- Prefer links to source files, official docs, and issue references over
  duplicating long procedures.
- Keep examples executable and platform-specific instructions explicit.
- Do not let generated docs drift from the actual manifests or install paths.
