# Code Review

- Review against local rules first: `AGENTS.md`, `.rules/`, plugin manifests,
  and the relevant skill or agent procedure.
- Lead with findings ordered by severity. Include concrete file and line
  references.
- Prioritize behavioral bugs, broken install surfaces, schema mismatches,
  version drift, data loss, security risks, and missing verification.
- Avoid cosmetic findings unless they violate an explicit project rule or make a
  change materially harder to maintain.
- For review and QA skills, verify the thin-dispatch contract:
  - The skill owns triggers.
  - Shared `references/` are the source of truth.
  - Agent shells stay fresh-context and load those references.
  - Codex and Copilot behavior is described accurately for their current
    install surfaces.
- If no actionable findings exist, say so clearly and name residual risks or
  checks not run.
