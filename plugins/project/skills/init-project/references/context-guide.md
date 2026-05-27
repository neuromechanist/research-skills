# Context Directory Guide

The `.context/` directory provides structured documentation that persists across development sessions. Each file has a specific purpose and format.

## Files

### plan.md

**Purpose:** Track current tasks and phases of development.

**Structure:**
- Project overview (goal, timeline, tech stack)
- Phase-based task breakdown (Foundation, Core Features, Integration, Release)
- Each task has a status: `[ ]` pending, `[~]` in progress, `[x]` complete
- Success criteria as checkboxes
- Implementation notes and blockers

**When to update:** At the start of each work session. Mark completed tasks, add new tasks discovered during implementation.

### ideas.md

**Purpose:** Capture high-level concepts, design decisions, and architectural ideas.

**Structure:**
- Core concepts and project vision
- Architecture ideas with system design notes
- Feature ideas with complexity and priority ratings
- Design patterns being considered
- User experience flows and considerations

**When to update:** When making design decisions or considering new approaches. Record the decision and the reasoning.

### research.md

**Purpose:** Document technical explorations, solutions considered, and references found.

**Structure:**
- Research log entries with date and context
- Explored solutions with pros, cons, and references
- Technical decisions with options considered and choice rationale
- Implementation notes and gotchas discovered

**When to update:** After investigating a technical question or evaluating options. Record what was tried and what was learned.

### scratch_history.md

**Purpose:** Document failed attempts, lessons learned, and anti-patterns to avoid.

**Structure:**
- Failed attempts log (date, goal, implementation tried, what went wrong, root cause, lesson)
- Common pitfalls (symptoms, cause, solution)
- Abandoned approaches with rationale for abandonment
- Debugging notes including red herrings and actual root causes
- Key learnings summary

**When to update:** Immediately after a failed attempt. Capture the details while they are fresh. This file prevents repeating the same mistakes.

### decisions/

**Purpose:** Architecture Decision Records (ADRs). One file per significant decision, tucked together so they are easy to find later.

**Structure:**
- `README.md` documents the convention (numbering, statuses, when to write one).
- `0000-template.md` is the template; copy it to start a new ADR. Do not edit it directly.
- Decisions are numbered `NNNN-short-kebab-title.md` (zero-padded to four digits, sequential).
- Each ADR has: Status, Date, Owner, Context, Decision, Consequences, Alternatives considered, Receipts.
- Status flows `proposed` -> `accepted` -> (later) `superseded by ADR-NNNN`. Never delete an ADR; supersede it.

**When to write one:** When the decision will be hard or expensive to reverse, cuts off other reasonable paths, has been argued about more than once, or embeds a non-obvious constraint (legal, performance, schedule). Skip ADRs for routine choices already obvious from the code.

**Relation to ideas.md and research.md:** `ideas.md` and `research.md` are exploratory and frequently rewritten. ADRs are the durable record of what was actually chosen and why. Promote an idea or research conclusion to an ADR once the decision is final.

## Usage Guidelines

1. Keep entries concise but complete enough to be useful months later
2. Always include dates for research and scratch_history entries
3. Cross-reference between files (e.g., a failed attempt in scratch_history might link to the research that led to a better solution)
4. These files are tracked in git by default, providing a shared knowledge base for the team
5. For unused context files, keep the template structure with minimal instructions on how to start using them
