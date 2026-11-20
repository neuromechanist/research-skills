---
name: security-audit
description: "This skill should be used when the user says \"security audit\", \"check for vulnerabilities\", \"security review\", \"harden project\", \"dependency audit\", \"credential scan\", \"check for secrets\", \"scan for secrets\", \"OWASP review\", \"security checklist\", \"audit dependencies\", \"find vulnerabilities\", or wants to review their project for security issues, exposed credentials, or vulnerable dependencies."
version: 0.2.0
---

# Security Audit

Routes a security review to an **independent, fresh-context auditor** covering credential exposure, code vulnerability patterns, authentication, configuration, Docker, and continuous integration and delivery (CI/CD), with dependency scanning handled by the `dependency-auditor` agent in parallel. This skill is a thin dispatcher; the checklist, severity rubric, and output format live in `references/audit-procedure.md`.

## When to Use

- Before a release or deployment
- After adding new dependencies
- When onboarding to a new codebase
- Periodic security reviews
- After receiving a vulnerability report

## Why a fresh-context auditor

The session that wrote the code knows why each risky-looking pattern was meant to be safe, and that knowledge is exactly what an attacker does not share. A separate auditor reads only the tree, history, and configuration. Pass **framing** only: repository root or paths, deployment context (internet-facing service, internal tool, library, research scripts), and release target if any; never the implementation rationale. Dependency scanning is mechanical, so it stays with the `dependency-auditor` agent rather than the judgment-based auditor.

## Modes (caller decides each run)

- **Full (default):** the auditor runs the whole checklist while `dependency-auditor` scans packages, outdated versions, and licenses in parallel; merge both into one report by the shared severity rubric.
- **Scoped:** the caller names checklist sections (for example secrets only, or CI/CD only) or paths; run only those, and skip `dependency-auditor` unless dependencies are in scope.
- **Dependencies only:** "audit dependencies" or a lockfile change; run `dependency-auditor` alone.

## Dispatch

Pick the branch for the current tool. In every branch the auditor follows `references/audit-procedure.md`.

- **Claude Code:** in a single message, `Agent(subagent_type: "project:security-audit", ...)` with the root, scope, and deployment context, and `Agent(subagent_type: "project:dependency-auditor", ...)` with the root, so both run in parallel. Merge the two reports: one Critical/High/Medium/Low list, dependency findings tagged `[DEP]`, duplicates removed, and every Critical surfaced as a release blocker.
- **Codex CLI:** plugin installation exposes this skill, not a Codex subagent. To use a fresh-context Codex auditor, copy `agents/templates/security-audit.toml` to `~/.codex/agents/` or `.codex/agents/` and invoke that configured agent if the current Codex surface supports `/agent`; run the dependency section of the procedure in this session. If no Codex subagent is available, use the fallback branch.
- **Copilot CLI:** plugin installation exposes this skill and, through `.github/plugin/plugin.json`, the `.agent.md` auditor in `agents/templates/`. Invoke that configured agent when the current Copilot surface supports custom agents, and run the dependency section in this session. If running outside a plugin install, copy `agents/templates/security-audit.agent.md` to `.github/agents/` or `~/.copilot/agents/`. If no custom agent is available, use the fallback branch.
- **Fallback** (no subagent support, or the user wants an interactive in-thread audit): locate the references (`$CLAUDE_PLUGIN_ROOT/skills/security-audit/references`, else `find . -type d -path '*/skills/security-audit/references' | head -1`); if they cannot be found, stop and tell the user to install the project plugin rather than auditing from memory. Then follow `references/audit-procedure.md` in full, including the dependency scan.

## The brain (do not duplicate into dispatch or agent shells)

- `references/audit-procedure.md` -- scope and independence rules, the seven-section checklist, the severity rubric shared with `dependency-auditor`, and the output format.
- `references/owasp-top-10.md` -- Open Worldwide Application Security Project (OWASP) Top 10 checklist with project-specific examples.
- `references/secret-management.md` -- how to manage secrets across environments.
