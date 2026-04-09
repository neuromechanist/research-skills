---
name: update-rules
description: "This skill should be used when the user asks to \"update rules\", \"sync rules\", \"update CLAUDE.md\", \"refresh rules\", \"update project config\", \"sync templates\", \"update vibe rules\", \"check for rule updates\", \"update user rules\", \"update global config\", \"refresh CLAUDE.md\", \"sync .rules directory\", \"what's new in templates\", or wants to update existing Claude/rules configuration from the latest templates without overwriting customizations."
version: 0.1.0
---

# Update Rules and Configuration

Update existing CLAUDE.md and .rules/ files from the latest plugin templates. Non-destructive: never overwrite user customizations, always preview changes before applying.

## When to Use

- After plugin templates have been updated with new rules or improvements
- When adding a rule file introduced after initial project setup
- When checking if project rules are current with latest best practices
- When updating global (`~/.claude/CLAUDE.md`) development instructions
- When a user wants to know what changed in the templates since they last synced

## Two Operating Levels

### Project Level (`/update-rules project`)

Update the current project's configuration:

1. **`.rules/` directory sync** -- Compare each template rule file against the project's `.rules/` directory:
   - `MISSING` -- new in templates, not in project. Show purpose and offer to add.
   - `CHANGED` -- exists but differs from template. Show unified diff, suggest merge.
   - `CURRENT` -- matches template. Report as up to date.
   - `CUSTOM` -- user-added rule not in templates. Preserve completely, report.

2. **`CLAUDE.md` section comparison** -- Extract H2 headers from both template and project CLAUDE.md. Identify missing sections. For matching sections, compare content and suggest updates. Preserve all project-specific customizations (replaced placeholders, custom guidelines, architecture maps).

3. **What gets compared:**
   - Template `rules/*.md` vs `.rules/*.md`
   - Template `CLAUDE.md` sections vs `./CLAUDE.md` sections

### User Level (`/update-rules user`)

Update global development instructions:

1. **Section analysis** -- Extract sections from `~/.claude/CLAUDE.md` and compare against template best practices and core principles.

2. **Best practice suggestions:**
   - New tool recommendations from templates
   - New `[NEVER DO THIS]` entries (compare item-by-item)
   - Updated workflow steps
   - Sections in templates with no equivalent in user config

3. **What gets compared:**
   - User file sections vs template CLAUDE.md sections
   - Template rules that have universal applicability (testing.md, git.md)
   - Use `references/section-mapping.md` for cross-referencing sections

## Comparison Workflow

### Step 1: Run Comparison Script

Run `project-diff-rules <level>` to get structured comparison data. The script outputs KEY=VALUE pairs categorizing each rule file and listing section headers from both sources.

### Step 2: Read and Analyze

For project level:
- Read each `RULE_CHANGED` file from both template and project to understand the differences
- Read CLAUDE.md from both sources to compare sections
- Run `diff --unified "$(project-templates-path)/claude/rules/<file>" ".rules/<file>"` for each changed rule

For user level:
- Read `~/.claude/CLAUDE.md` in full
- Read template CLAUDE.md and relevant rule files for best-practice content
- Use `references/section-mapping.md` to map template sections to user sections

### Step 3: Present Update Plan

Present a numbered list of proposed changes. Each change marked as:
- `[ADD]` -- New content to add
- `[UPDATE]` -- Existing content to modify
- `[INFO]` -- No change needed, already current

Show preview of what will change for each item. Ask user to confirm which changes to apply. Never apply changes without confirmation.

### Step 4: Apply Approved Changes

- For existing files: use Edit tool for surgical modifications. Never use Write to overwrite.
- For new .rules/ files: use Write to create them (safe, creating new file).
- For CLAUDE.md sections: use Edit to insert or update specific sections.

### Step 5: Verify

Run `project-diff-rules <level>` again to confirm all approved changes were applied.

## Non-Destructive Guarantees

- NEVER overwrite a file without showing the diff first
- NEVER remove user-added content (custom rules, custom sections, custom guidelines)
- NEVER replace project-specific values (project name, tech stack, architecture) with template placeholders
- ALWAYS use Edit for existing files, never Write (except for brand-new rule files)
- For changed .rules/ files, present three options: (a) accept template version, (b) merge specific changes, (c) skip

## Distinguishing Template Improvements from User Customizations

For rule files: if the user has not modified the rule since init, it matches an older template version. The diff shows what the template improved. If the user customized it, the diff shows both template changes AND user changes; present both clearly and let the user decide.

For CLAUDE.md: sections that still contain `{{PLACEHOLDERS}}` were never customized. Sections with replaced placeholders contain user-specific content. Template-originated content (like the "[NEVER DO THIS]" list) can be compared item-by-item.

## Additional Resources

### Reference Files

- **`references/section-mapping.md`** -- Maps template CLAUDE.md sections to user CLAUDE.md sections for intelligent cross-level comparison
