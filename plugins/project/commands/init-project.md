---
description: Initialize a new project with cross-agent vibe-rules templates
argument-hint: <project-description>
allowed-tools: Bash, Read, Write, Edit
---

# Project Initialization with Vibe Rules

Initialize this project using bundled vibe-rules templates from the init-project plugin.

## Setup Process:

### 1. Analyze Current Project
!echo "Project description: $ARGUMENTS"
!pwd
!ls -la

### 2. Copy templates and set up project structure
!project-init-templates .

If the above command failed, report the exact error to the user and stop. Do not proceed with remaining steps.

### 3. Track agent files in git
AGENTS.md, CLAUDE.md, .rules/, and .context/ are tracked in git by default. Add to .gitignore only if explicitly requested by the user.

### 4. Optional default GitHub labels
If the repository has already been initialized, pushed to GitHub, and the user asks for default labels, run:

!project-init-labels .

This command is idempotent and creates or updates the standard type, priority, and workflow labels.

### 5. Customize AGENTS.md based on project context
Now analyze the project and customize the AGENTS.md file using the project description provided by the user: `$ARGUMENTS`
- Replace template placeholders: {{PROJECT_NAME}} with the project name, {{framework}} with the detected framework
- Use `$ARGUMENTS` as the project purpose in the "Project Context" section
- Add project-specific instructions based on detected language/framework
- Update .rules/ contents to match project needs; remove irrelevant rules
- Update .context/ files with project requirements; keep minimal instructions for unused files
- Put durable architecture decisions in `.context/decisions/` using the ADR template and `NNNN-short-title.md` naming convention
- Keep CLAUDE.md as `@AGENTS.md` followed only by Claude Code-specific plugin, skill, command, or MCP instructions
- Re-read AGENTS.md and CLAUDE.md to ensure only relevant context and rules are referenced

!if [ -f "package.json" ]; then echo "Detected: Node.js/JavaScript project"; fi
!if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then echo "Detected: Python project"; fi
!if [ -f "Cargo.toml" ]; then echo "Detected: Rust project"; fi
!if [ -f "go.mod" ]; then echo "Detected: Go project"; fi

### 6. Cursor setup (optional)
If the user also uses Cursor, offer to set up Cursor templates.
Use `project-templates-path` to locate the templates directory, then copy:
- .cursorrules from `<templates>/cursor/`
- core_rules/ .mdc files
- Planning workflow (default or advanced-taskmaster based on preference)

### 7. Verify initialization
!echo "\n=== Initialization Verification ===" && \
  for f in AGENTS.md CLAUDE.md .rules .context; do \
    if [ -e "$f" ]; then echo "[OK] $f exists"; else echo "[MISSING] $f was NOT created"; fi; \
  done

Now help customize the AGENTS.md file to document:
- Project-specific goals and instructions
- What's in the .context directory (plan, ideas, research, scratch_history)
- What rules are in .rules/ and which are relevant
- References to any existing planning documents

Keep CLAUDE.md as the Claude Code adapter: it should import AGENTS.md with `@AGENTS.md`, then append only Claude-specific plugin/skill/command instructions when needed.
