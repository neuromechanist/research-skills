---
name: init-project
description: "Use this skill for \"initialize project\", \"set up project\", \"scaffold project\", \"create AGENTS.md\", \"create CLAUDE.md\", \"set up rules\", \"create context directory\", \"vibe rules\", \"project templates\", \"init new project\", \"set up development structure\", \"create .rules\", \"create .context\", \"create ADR\", \"architecture decision records\", \"set up GitHub labels\", \"default issue labels\", \"project scaffolding\", \"set up pre-commit hooks\", or when the user wants to initialize a new project with cross-agent development templates, structured documentation, and an optional default GitHub label set."
version: 0.2.0
---

# Project Initialization with Vibe Rules Templates

Initialize new projects with a structured development environment for Codex, Claude Code, Copilot, and optionally Cursor. The templates enforce consistent development practices: real testing (no mocks), atomic commits, documentation-driven development, and continuous rule improvement.

## When to Use

- Starting a new project from scratch
- Adding cross-agent structure to an existing project
- Setting up .rules/ and .context/ directories for a project that lacks them
- Migrating a project to vibe-rules conventions

Partial-init detection: if AGENTS.md or .rules/ already exists, this is not a
fresh init. Inventory what exists first; scaffold only the missing pieces
(never overwrite an existing AGENTS.md or customized rule), and use the
update-rules skill instead when the ask is to refresh existing files against
newer templates. For understanding an existing codebase before documenting
it, run codebase-onboarding first and reuse its report for the architecture
map in Step 4.

## Template Structure

The plugin bundles all templates under `templates/`:

```
templates/
  agents/           # Shared agent templates
    AGENTS.md       # Main cross-agent instructions file
  claude/           # Claude Code adapter templates
    CLAUDE.md       # Imports AGENTS.md, then holds Claude-only guidance
    rules/          # Detailed rule references
      testing.md      # NO MOCK testing policy
      git.md          # Version control standards
      python.md       # Python/UV standards
      code_review.md  # PR review toolkit
      documentation.md # MkDocs standards
      ci_cd.md        # GitHub Actions setup
      self_improve.md  # Rule evolution
      serena_mcp.md    # Code intelligence tools
  context/          # Documentation scaffolding
    plan.md           # Task tracking with phases
    ideas.md          # Design concepts
    research.md       # Technical explorations
    scratch_history.md # Failed attempts and lessons
    decisions/        # Architecture Decision Records
      README.md         # ADR convention (numbering, statuses, when to write one)
      0000-template.md  # Template for new ADRs (do not edit)
  config/           # Development configuration
    pre-commit        # Ruff pre-commit hook (Python)
    pyproject.toml    # Python project config
    pytest.ini        # Pytest config
    mkdocs.yml        # Documentation config
    gitignore-template # Common ignores
  github/           # CI/CD templates
    workflows/
      test.yml        # Test pipeline
      docs.yml        # Documentation deployment
      release.yml     # Release automation
  cursor/           # Cursor IDE templates (optional)
    .cursorrules      # Main cursor config
    core_rules/       # Modular .mdc rule files
    planning/
      default/        # Plan-based development workflow
      advanced-taskmaster/ # Complex project task management
```

## Initialization Workflow

### Step 1: Detect project type

Scan the current directory for language markers:
- `pyproject.toml`, `requirements.txt`, `setup.py` -> Python project
- `package.json` -> Node.js/JavaScript/TypeScript project
- `Cargo.toml` -> Rust project
- `go.mod` -> Go project

### Step 2: Copy core templates

Copy with safety checks (never overwrite existing files):
1. **AGENTS.md** from `templates/agents/AGENTS.md`
2. **CLAUDE.md** from `templates/claude/CLAUDE.md` (contains `@AGENTS.md`, then Claude-only guidance)
3. **.rules/** from `templates/claude/rules/` (all .md files)
4. **.context/** from `templates/context/` (plan, ideas, research, scratch_history)
5. **.context/decisions/** from `templates/context/decisions/` (ADR template and README). Created separately so existing projects that already have `.context/` still pick it up on re-run.

### Step 3: Language-specific setup

**Python projects:**
- Install pre-commit hook from `templates/config/pre-commit` (runs ruff on staged files)
- Reference `templates/config/pyproject.toml` and `templates/config/pytest.ini` for configuration examples

**All projects:**
- Offer GitHub Actions workflows from `templates/github/workflows/` if `.github/workflows/` does not exist

### Step 4: Customize AGENTS.md and keep CLAUDE.md as an adapter

Replace template placeholders with project-specific values:
- `{{PROJECT_NAME}}` in AGENTS.md - actual project name
- `{{framework}}` in AGENTS.md - detected framework (e.g., Django, FastAPI, Next.js)
- `{{TECH_STACK}}` in context/plan.md - detected languages and frameworks

Tailor the content:
- Remove rules that do not apply. Test: a rule applies if its language or tool
  appears in the repo's manifests or file extensions (python.md stays only if
  pyproject.toml or *.py exist; docker rules stay only if a Dockerfile or
  compose file exists).
- Add a project-specific architecture map: 3-8 bullet lines, one per
  component, each naming its directory and one-line responsibility, plus how
  they connect. Use the codebase-onboarding skill's report as the source when
  the repo is not trivial.
- Document existing conventions already in place: infer from the code, not
  from preference (test framework actually used, naming pattern of the three
  most recent modules, error-handling idiom of the main package)
- Ensure .context/ files have project-relevant instructions
- Keep shared project instructions in AGENTS.md
- Keep CLAUDE.md as `@AGENTS.md`, then append only Claude Code-specific plugin, skill, command, or MCP guidance below the import

### Step 5: Cursor setup (optional)

Only if the user requests it or uses Cursor:
- Copy `.cursorrules` from `templates/cursor/`
- Copy `core_rules/` .mdc files
- Offer planning workflow choice: default (plan-based) or advanced-taskmaster

### Step 6: GitHub labels (optional, post-push)

If (and only if) the project has been pushed to GitHub and the user opts in, install a default issue label set:

```bash
project-init-labels .
```

The script is idempotent (uses `gh label create --force`) and installs:
- **Type:** `feature`, `bug`, `chore`, `docs`, `refactor`
- **Priority:** `P0` (critical), `P1` (high), `P2` (medium), `P3` (low)
- **Workflow:** `epic`, `blocked`, `needs-triage`, `good first issue`, `help wanted`

Skip this step entirely if the project is not on GitHub yet, or if the user prefers to manage labels by hand. Do not run it without asking.

### Step 7: Verify and summarize

List created files and directories. Confirm the structure is correct before the user starts working.

## Core Principles Enforced by Templates

Read `references/core-principles.md` for the full rationale behind each principle.

1. **NO MOCKS** - Test with real data, real databases, real APIs. No mocks, stubs, or fake data.
2. **Atomic commits** - One logical change per commit, messages <50 chars, no emojis, no AI attribution.
3. **Documentation-driven** - Four .context/ files track plan, ideas, research, and failed attempts.
4. **No technical debt** - Address all PR review findings. Replace, do not deprecate.
5. **Tool consistency** - UV for Python, Bun for JS/TS, Ruff for linting, Ty for type checking.
6. **Rule evolution** - Extract patterns used 3+ times into rules. Mine failures into prevention rules.

## Rules Directory Reference

Read `references/rules-guide.md` for detailed descriptions of each rule file and when to include or exclude them.

## Context Directory Reference

Read `references/context-guide.md` for how to use each .context/ file effectively.
