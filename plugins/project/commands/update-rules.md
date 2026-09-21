---
description: Update AGENTS.md/CLAUDE.md, .rules/, and .memory/ from latest templates
argument-hint: <user|project>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill
---

# Update Rules and Configuration

Update existing AGENTS.md/CLAUDE.md, `.rules/`, and project-memory
scaffolding from the latest plugin templates without overwriting user
customizations. Load the `project:update-rules` skill for the full comparison
strategy and non-destructive guarantees.

## Setup Process:

### 1. Parse Arguments

Determine the level from `$ARGUMENTS`:
- `user` -> load `project:install-user-instructions`, ask which supported
  systems to configure, and follow that skill instead of this command
- `project` -> update `./AGENTS.md` + Claude adapter `./CLAUDE.md` + `.rules/` + `.memory/` convention files

If `$ARGUMENTS` is empty or not one of `user`/`project`, ask the user which level to update.

### 2. Run Comparison
!project-diff-rules $ARGUMENTS

Run this comparison only for `project`. For `user`, do not run the legacy
Claude-only comparison script; transfer control to
`project:install-user-instructions`.

If the above command failed or the output does not contain `STATUS=complete` as the final line, the script terminated prematurely. Report the error to the user and stop. Do not proceed with remaining steps.

### 3. Analyze Results

#### For PROJECT level:

**Missing rules (RULE_MISSING):**
- Read the first 20 lines of the missing rule file from templates to understand its purpose
- Determine if the rule is relevant to this project (e.g., skip python.md for a JS-only project)
- Present each missing rule with a brief description and ask which to add

**Changed rules (RULE_CHANGED):**
- For each changed rule, show a unified diff by running `diff --unified "$(project-templates-path)/claude/rules/<filename>" ".rules/<filename>"` with the rule filename substituted
- Analyze: are the differences template improvements or user customizations?
- Present options: (a) accept template version, (b) merge specific changes, (c) skip

**Current rules (RULE_CURRENT):**
- Report as up to date (no action needed)

**Custom rules (RULE_CUSTOM):**
- Report as user-created (preserved, no action needed)

**Project memory comparison:**
- `MEMORY_FILE_MISSING` -> offer to add the missing template README or INDEX
- `MEMORY_FILE_CHANGED` -> show a unified diff and offer accept, merge, or skip
- `MEMORY_FILE_CURRENT` -> report as current
- Any other `.memory/*.md` file is a project fact and must be preserved

**AGENTS.md section comparison:**
- Read template AGENTS.md and the project AGENTS.md in full
- Compare H2 sections: identify sections in template missing from project
- For matching sections, compare content for improvements
- Respect project-specific content (replaced placeholders, architecture maps, custom guidelines)
- If the project only has CLAUDE.md, offer to migrate shared content into AGENTS.md and replace CLAUDE.md with the `@AGENTS.md` adapter plus Claude-only additions

#### For USER level:

The `install-user-instructions` skill owns detection, system selection,
preview, confirmation, application, verification, and downstream-duplication
audit. Do not duplicate that workflow here.

### 4. Present Update Plan

Show a numbered list of proposed changes:
- `[ADD]` - New content to add (new rules, new sections, new list items)
- `[UPDATE]` - Existing content to modify (improved wording, new steps)
- `[INFO]` - Already current, no change needed

For each `[ADD]` or `[UPDATE]`, show a preview of the change.

If everything is current, report "All rules and configuration are up to date." and stop.

Ask the user which changes to apply. Never apply without confirmation.

### 5. Apply Approved Changes

For each approved change:
- **New .rules/ files:** use Write to create them
- **Missing `.memory/` directory or template files:** create only missing files;
  never overwrite existing facts or customized README/INDEX
- **Existing .rules/ files:** use Edit for surgical modifications, or Write if accepting full template version
- **AGENTS.md sections:** use Edit to insert or update specific sections
- **CLAUDE.md adapter:** ensure it starts with `@AGENTS.md`, then preserves or appends only Claude-specific guidance
- **New list items:** use Edit to append to existing lists

### 6. Verify
!project-diff-rules $ARGUMENTS

Confirm that approved changes were applied. Report final status.
