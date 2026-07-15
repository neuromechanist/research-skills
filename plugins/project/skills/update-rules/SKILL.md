---
name: update-rules
description: "This skill should be used when the user asks to \"update rules\", \"sync rules\", \"update AGENTS.md\", \"update CLAUDE.md\", \"refresh rules\", \"update project config\", \"sync templates\", \"update vibe rules\", \"check for rule updates\", \"update user rules\", \"update global config\", \"refresh AGENTS.md\", \"refresh CLAUDE.md\", \"sync .rules directory\", \"what's new in templates\", or wants to update existing agent/rules configuration from the latest templates without overwriting customizations."
version: 0.1.0
---

# Update Rules and Configuration

Update existing AGENTS.md/CLAUDE.md and .rules/ files from the latest plugin templates. Non-destructive: never overwrite user customizations, always preview changes before applying.

## When to Use

- After plugin templates have been updated with new rules or improvements
- When adding a rule file introduced after initial project setup
- When checking if project rules are current with latest best practices
- When checking existing project rules against newer templates. For installing
  or updating user-level instructions across Claude, Codex, Copilot, or Cursor,
  use `install-user-instructions` instead.
- When a user wants to know what changed in the templates since they last synced

## Two Operating Levels

### Project Level (`/update-rules project`)

Update the current project's configuration:

1. **`.rules/` directory sync** -- Compare each template rule file against the project's `.rules/` directory:
   - `MISSING` -- new in templates, not in project. Show purpose and offer to add.
   - `CHANGED` -- exists but differs from template. Show unified diff, suggest merge.
   - `CURRENT` -- matches template. Report as up to date.
   - `CUSTOM` -- user-added rule not in templates. Preserve completely, report.

2. **`AGENTS.md` section comparison** -- Extract H2 headers from both template and project AGENTS.md. Identify missing sections. For matching sections, compare content and suggest updates. Preserve all project-specific customizations (replaced placeholders, custom guidelines, architecture maps). If the project only has CLAUDE.md, offer to migrate shared content into AGENTS.md and leave CLAUDE.md as the Claude adapter.

3. **What gets compared:**
   - Template `rules/*.md` vs `.rules/*.md`
   - Template `AGENTS.md` sections vs `./AGENTS.md` sections (script emits `PROJECT_SECTION_SOURCE=agents|claude` so a CLAUDE.md fallback is never silently treated as AGENTS.md)
   - The CLAUDE.md adapter check is performed as an LLM read step (verify it begins with `@AGENTS.md` and contains only Claude-specific additions), not part of the script output

### User Level (`/update-rules user`)

Delegate to `install-user-instructions`. That skill detects and asks which of
Claude Code, Codex, GitHub Copilot CLI, and Cursor the user wants to configure,
previews non-destructive managed-block changes, and prevents general defaults
from being copied into downstream projects. Do not silently interpret `user`
as Claude-only.

## Comparison Workflow

### Step 1: Run Comparison Script

Run `project-diff-rules <level>` to get structured comparison data. The script outputs KEY=VALUE pairs categorizing each rule file and listing section headers from both sources.

### Step 2: Read and Analyze

For project level:
- Read each `RULE_CHANGED` file from both template and project to understand the differences
- Read AGENTS.md from both sources to compare sections
- Read CLAUDE.md to verify it imports AGENTS.md with `@AGENTS.md` and contains only Claude-specific additions
- Run `diff --unified "$(project-templates-path)/claude/rules/<file>" ".rules/<file>"` for each changed rule

For user level, stop this comparison workflow and use
`install-user-instructions`. Read only the selected systems' targets and
platform reference after the user chooses them.

### Step 3: Present Update Plan

Present a numbered list of proposed changes. Each change marked as:
- `[ADD]` -- New content to add
- `[UPDATE]` -- Existing content to modify
- `[INFO]` -- No change needed, already current

Show preview of what will change for each item. Ask user to confirm which changes to apply. Never apply changes without confirmation.

### Step 4: Apply Approved Changes

- For existing files: use Edit tool for surgical modifications. Use Write only when the user explicitly approves replacing a file with the template version.
- For new .rules/ files: use Write to create them (safe, creating new file).
- For AGENTS.md sections: use Edit to insert or update specific sections.
- For CLAUDE.md: use Edit to keep the adapter import (`@AGENTS.md`) and preserve Claude-only additions.

### Step 5: Verify

Run `project-diff-rules <level>` again to confirm all approved changes were applied.

## Non-Destructive Guarantees

- NEVER overwrite a file without showing the diff first
- NEVER remove user-added content (custom rules, custom sections, custom guidelines)
- NEVER replace project-specific values (project name, tech stack, architecture) with template placeholders
- ALWAYS use Edit for existing files when merging selective changes. Write is acceptable only for new rule files or when the user explicitly approves replacing a file with the template version.
- For changed .rules/ files, present three options: (a) accept template version, (b) merge specific changes, (c) skip

## Distinguishing Template Improvements from User Customizations

For rule files: if the user has not modified the rule since init, it matches an older template version. The diff shows what the template improved. If the user customized it, the diff shows both template changes AND user changes; present both clearly and let the user decide.

For AGENTS.md: sections that still contain `{{PLACEHOLDERS}}` were never customized. Sections with replaced placeholders contain user-specific content. Template-originated content (like the "[NEVER DO THIS]" list) can be compared item-by-item.

## Additional Resources

### Reference Files

- **`references/section-mapping.md`** -- Legacy Claude user-file mapping kept
  for older installations. New cross-agent user setup belongs to
  `install-user-instructions`.
