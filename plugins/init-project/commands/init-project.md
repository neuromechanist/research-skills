---
description: Initialize a new project with vibe-rules templates for Claude
argument-hint: <project-description>
allowed-tools: Bash(echo:*), Bash(pwd:*), Bash(ls:*), Bash(rm:*), Bash(cp:*), Bash(mkdir:*), Bash(chmod:*), Bash(grep -q:*), Bash(cat:*), Bash(test:*), Bash([:*), Write, Edit, Read
---

# Project Initialization with Vibe Rules

Initialize this project using bundled vibe-rules templates from the init-project plugin.

## Setup Process:

### 1. Analyze Current Project
!echo "Project description: $ARGUMENTS"
!pwd
!ls -la

### 2. Locate Templates
!TEMPLATE_DIR="${CLAUDE_PLUGIN_ROOT}/templates"
!echo "Using templates from: $TEMPLATE_DIR"
!ls "$TEMPLATE_DIR"

### 3. Copy Claude Templates (with safety checks)

#### CLAUDE.md (if doesn't exist)
!if [ ! -f "CLAUDE.md" ]; then cp "${CLAUDE_PLUGIN_ROOT}/templates/claude/CLAUDE.md" ./CLAUDE.md && echo "Created CLAUDE.md"; else echo "CLAUDE.md already exists, skipping"; fi

#### .rules directory (if doesn't exist)
!if [ ! -d ".rules" ]; then mkdir -p .rules && cp "${CLAUDE_PLUGIN_ROOT}/templates/claude/rules/"*.md ./.rules/ && echo "Created .rules directory"; else echo ".rules directory already exists, skipping"; fi

#### .context directory (if doesn't exist)
!if [ ! -d ".context" ]; then mkdir -p .context && cp "${CLAUDE_PLUGIN_ROOT}/templates/context/"*.md ./.context/ && echo "Created .context directory"; else echo ".context directory already exists, skipping"; fi

### 4. Track Claude files in git
!echo "Note: CLAUDE.md, .rules/, and .context/ are tracked in git by default."
!echo "Add to .gitignore only if explicitly requested by the user."

### 5. Python-specific setup (if Python project detected)
!if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then \
  if [ ! -f ".git/hooks/pre-commit" ]; then \
    cp "${CLAUDE_PLUGIN_ROOT}/templates/config/pre-commit" .git/hooks/pre-commit && \
    chmod +x .git/hooks/pre-commit && \
    echo "Installed pre-commit hooks with ruff"; \
  else \
    echo "Pre-commit hook already exists"; \
  fi; \
fi

### 6. Customize CLAUDE.md based on project context
Now analyze the project and customize the CLAUDE.md file:
- Replace template placeholders ({{PROJECT_NAME}}, {{ENV_NAME}}, {{TECH_STACK}})
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
!echo "\n=== Initialization Complete ===\n"
!echo "Claude structure created:"
!ls -la CLAUDE.md .rules/ .context/ 2>/dev/null || true

Now help customize the CLAUDE.md file to document:
- Project-specific goals and instructions
- What's in the .context directory (plan, ideas, research, scratch_history)
- What rules are in .rules/ and which are relevant
- References to any existing planning documents
