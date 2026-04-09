---
description: Update CLAUDE.md and .rules/ from latest templates
argument-hint: <user|project>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Update Rules and Configuration

Update existing CLAUDE.md and .rules/ files from the latest plugin templates without overwriting user customizations. Load the `project:update-rules` skill for the full comparison strategy and non-destructive guarantees.

## Setup Process:

### 1. Parse Arguments

Determine the level from `$ARGUMENTS`:
- `user` -> update `~/.claude/CLAUDE.md`
- `project` -> update `./CLAUDE.md` + `.rules/`

If `$ARGUMENTS` is empty or not one of `user`/`project`, ask the user which level to update.

### 2. Run Comparison
!project-diff-rules $ARGUMENTS

If the above command failed or the output does not contain `STATUS=complete` as the final line, the script terminated prematurely. Report the error to the user and stop. Do not proceed with remaining steps.

### 3. Analyze Results

#### For PROJECT level:

**Missing rules (RULE_MISSING):**
- Read the first 20 lines of the missing rule file from templates to understand its purpose
- Determine if the rule is relevant to this project (e.g., skip python.md for a JS-only project)
- Present each missing rule with a brief description and ask which to add

**Changed rules (RULE_CHANGED):**
- For each changed rule, show a unified diff:
  !diff --unified "$(project-templates-path)/claude/rules/<filename>" ".rules/<filename>"
- Analyze: are the differences template improvements or user customizations?
- Present options: (a) accept template version, (b) merge specific changes, (c) skip

**Current rules (RULE_CURRENT):**
- Report as up to date (no action needed)

**Custom rules (RULE_CUSTOM):**
- Report as user-created (preserved, no action needed)

**CLAUDE.md section comparison:**
- Read both CLAUDE.md files in full
- Compare H2 sections: identify sections in template missing from project
- For matching sections, compare content for improvements
- Respect project-specific content (replaced placeholders, architecture maps, custom guidelines)

#### For USER level:

**Section comparison:**
- Read `~/.claude/CLAUDE.md` in full
- Read template CLAUDE.md for best-practice content
- Use `references/section-mapping.md` to map template sections to user sections
- Read relevant template rules (testing.md, git.md) for universally applicable best practices

**Item-by-item checks:**
- Compare `[NEVER DO THIS]` lists item-by-item; suggest missing entries
- Check tool recommendations match (UV, Bun, ruff, ty, biome)
- Check workflow steps for new best practices
- Identify template sections with no equivalent in user config

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
- **Existing .rules/ files:** use Edit for surgical modifications, or Write if accepting full template version
- **CLAUDE.md sections:** use Edit to insert or update specific sections
- **New list items:** use Edit to append to existing lists

### 6. Verify
!project-diff-rules $ARGUMENTS

Confirm that approved changes were applied. Report final status.
