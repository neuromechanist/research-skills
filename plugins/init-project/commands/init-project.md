---
description: Initialize a new project with vibe-rules templates for Claude
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

### 2. Validate Plugin Root and Locate Templates
!if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] || [ ! -d "${CLAUDE_PLUGIN_ROOT}/templates" ]; then echo "ERROR: CLAUDE_PLUGIN_ROOT is not set or templates directory not found. This command must be run as a Claude Code plugin." && exit 1; fi
!echo "Using templates from: ${CLAUDE_PLUGIN_ROOT}/templates" && ls "${CLAUDE_PLUGIN_ROOT}/templates"

### 3. Copy Claude Templates (with safety checks)

#### CLAUDE.md (if doesn't exist)
!if [ ! -f "CLAUDE.md" ]; then cp "${CLAUDE_PLUGIN_ROOT}/templates/claude/CLAUDE.md" ./CLAUDE.md && echo "Created CLAUDE.md"; else echo "CLAUDE.md already exists, skipping"; fi

#### .rules directory (if doesn't exist)
!if [ ! -d ".rules" ]; then mkdir -p .rules && cp "${CLAUDE_PLUGIN_ROOT}/templates/claude/rules/"*.md ./.rules/ && echo "Created .rules directory with $(ls .rules/*.md 2>/dev/null | wc -l | tr -d ' ') rule files"; else echo ".rules directory already exists, skipping"; fi

#### .context directory (if doesn't exist)
!if [ ! -d ".context" ]; then mkdir -p .context && cp "${CLAUDE_PLUGIN_ROOT}/templates/context/"*.md ./.context/ && echo "Created .context directory with $(ls .context/*.md 2>/dev/null | wc -l | tr -d ' ') context files"; else echo ".context directory already exists, skipping"; fi

### 4. Track Claude files in git
!echo "Note: CLAUDE.md, .rules/, and .context/ are tracked in git by default."
!echo "Add to .gitignore only if explicitly requested by the user."

### 5. Python-specific setup (if Python project detected)
!if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then \
  if [ ! -d ".git" ]; then \
    echo "Warning: Not a git repository. Skipping pre-commit hook. Run 'git init' first, then re-run."; \
  elif [ ! -f ".git/hooks/pre-commit" ]; then \
    mkdir -p .git/hooks && \
    cp "${CLAUDE_PLUGIN_ROOT}/templates/config/pre-commit" .git/hooks/pre-commit && \
    chmod +x .git/hooks/pre-commit && \
    echo "Installed pre-commit hooks with ruff" || \
    echo "ERROR: Failed to install pre-commit hook"; \
  else \
    echo "Pre-commit hook already exists"; \
  fi; \
fi

### 6. Customize CLAUDE.md based on project context
Now analyze the project and customize the CLAUDE.md file using the project description provided by the user: `$ARGUMENTS`
- Replace template placeholders: {{PROJECT_NAME}} with the project name, {{framework}} with the detected framework
- Use `$ARGUMENTS` as the project purpose in the "Project Context" section
- Add project-specific instructions based on detected language/framework
- Update .rules/ contents to match project needs; remove irrelevant rules
- Update .context/ files with project requirements; keep minimal instructions for unused files
- Re-read CLAUDE.md to ensure only relevant context and rules are referenced

!echo "\n=== Analyzing project structure ===\n"
!ls -la
!if [ -f "package.json" ]; then echo "Detected: Node.js/JavaScript project"; fi
!if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then echo "Detected: Python project"; fi
!if [ -f "Cargo.toml" ]; then echo "Detected: Rust project"; fi
!if [ -f "go.mod" ]; then echo "Detected: Go project"; fi

### 7. Cursor setup (optional)
If the user also uses Cursor, offer to set up Cursor templates:
- Copy .cursorrules from templates/cursor/
- Copy core_rules/ .mdc files
- Copy planning workflow (default or advanced-taskmaster based on preference)

### 8. Verify initialization
!echo "\n=== Initialization Verification ===" && \
  for f in CLAUDE.md .rules .context; do \
    if [ -e "$f" ]; then echo "[OK] $f exists"; else echo "[MISSING] $f was NOT created"; fi; \
  done

Now help customize the CLAUDE.md file to document:
- Project-specific goals and instructions
- What's in the .context directory (plan, ideas, research, scratch_history)
- What rules are in .rules/ and which are relevant
- References to any existing planning documents
