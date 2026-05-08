# Section Mapping: Template AGENTS.md vs User CLAUDE.md

Maps sections between the template (project-level) AGENTS.md and the typical user-level `~/.claude/CLAUDE.md` to enable intelligent comparison across levels.

## Template -> User Section Mapping

| Template Section | User Section | Comparison Notes |
|---|---|---|
| Project Context | Domain Context | Template has placeholders; user has personal specifics |
| Architecture Map | (none) | Project-only; skip for user level |
| Environment Setup | Tools | Both cover tool choices (UV, Bun, gh). Compare item-by-item |
| Development Workflow | Git Workflow | Template has 10-step; user has 7-step. Compare steps |
| [CRITICAL] Core Principles | (distributed) | User spreads across Testing, Linting & Type Checking, Code & Response Style |
| [NEVER DO THIS] | [NEVER DO THIS] | Direct match. Compare item-by-item for missing entries |
| Think Like a Senior Developer | Code & Response Style | Loosely related; template focuses on engineering mindset, user focuses on interaction style. Compare for non-overlapping best practices |
| Rules Directory | (none) | Project-only reference; skip for user level |
| Context Files | Project Documentation | User describes .context/ convention |
| Quick Commands | (none) | Project-specific; skip for user level |
| Project-Specific Guidelines | (none) | Project-only; skip for user level |

## Universal Sections

These template sections contain universally applicable best practices. When comparing at user level, check that the user file covers these topics:

- **[NEVER DO THIS]** -- compare item-by-item, suggest missing entries
- **Tool choices** (UV, Bun, ruff, ty, biome) -- verify consistency between template and user
- **Commit/PR standards** -- compare workflow steps, check for new best practices
- **Testing philosophy** (NO MOCKS) -- verify presence and completeness
- **Code review process** -- check PR review workflow is documented

## Project-Only Sections

These are only relevant at project level (skip when comparing user-level):

- Architecture Map (project structure)
- Rules Directory references (.rules/ file list)
- Context Files references (.context/ file list)
- Quick Commands (project-specific bash snippets)
- Project-Specific Guidelines (custom section)

## User-Only Sections

These exist in user CLAUDE.md but not in templates. Preserve completely during updates:

- Sprint/Feature Development Workflow (epic workflow with worktrees)
- PR Review Process (review-pr integration details)
- Writing Style (no em-dashes, abbreviation rules)
- Session Start (date command convention)
- Domain Context (personal research areas, tools, projects)
- Merge Strategy (regular merge vs squash)
- Linting & Type Checking (detailed tool config)

## Template Rules with Universal Applicability

These rule files from `templates/claude/rules/` contain best practices applicable at both levels. When updating user-level config, extract key principles from:

- `testing.md` -- NO MOCKS policy, real data requirements
- `git.md` -- commit messages, branch strategy, merge process
- `code_review.md` -- PR review checklist, no-tech-debt policy
- `self_improve.md` -- rule evolution, learning from projects

## Template Rules that are Project-Specific

These rules are primarily relevant to project-level updates:

- `python.md` -- language-specific (only if Python project)
- `ci_cd.md` -- CI/CD pipeline configuration
- `documentation.md` -- MkDocs setup
- `serena_mcp.md` -- code intelligence tools (only if Serena MCP available)
