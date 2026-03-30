# TaskMaster Planning Approach

**Goal:** AI-powered task management combined with documentation-driven development for complex {{PROJECT_NAME}} projects.

## When to Use

### ✅ Recommended For
- **Complex projects** with 15+ major features
- **Multi-developer teams** needing coordination
- **Long-term projects** (3+ months development)  
- **Evolving requirements** needing iterative refinement
- **AI-assisted** task analysis and breakdown

### ❌ Not Recommended For
- **Simple scripts** or single-purpose tools
- **Solo projects** with clear scope
- **Quick prototypes** or proof-of-concepts

## Quick Setup

```bash
# Install and initialize
npm install -g @taskmaster/cli
task-master init --yes
task-master parse-prd scripts/prd.txt --num-tasks=15 --research
```

**Project structure created:**
```
{{PROJECT_NAME}}/
├── .context/              # Development context (gitignored)
│   ├── research.md       # Technical solutions
│   ├── ideas.md          # Design concepts
│   └── scratch_history.md # Failed attempts
├── .taskmaster/           # TaskMaster configuration
├── tasks/tasks.json       # Main task database
└── scripts/prd.txt        # Requirements document
```

## Daily Workflow

```bash
# Find next task
task-master next

# Check context (if needed)
# Review .context/ideas.md and .context/research.md for background

# Start work
task-master set-status <task-id> --status=in-progress

# Update progress (AI-powered)
task-master update-subtask <task-id>.<subtask-id> --prompt="Implementation notes"

# Document learnings
# Update .context/research.md with solutions
# Log failures in .context/scratch_history.md

# Complete task
task-master set-status <task-id> --status=done
```

## Key Features

### AI-Powered Task Management
```bash
# Generate research-backed tasks
task-master add --prompt="Feature requirement" --research

# Break down complex tasks
task-master expand-task <task-id> --num=5 --research

# Analyze complexity
task-master analyze-complexity --threshold=6
```

### MCP Integration (Recommended)
Use MCP server tools for better performance:
- `get_tasks`, `next_task`, `get_task` - Task viewing
- `update_subtask`, `add_task`, `expand_task` - AI operations
- `add_dependency`, `validate_dependencies` - Dependencies

### Dependency Management
```bash
# Add dependencies
task-master add-dependency <task-id> --depends-on=<prerequisite-id>

# Validate dependency graph
task-master validate-dependencies
```

## Git Integration

```bash
# Concise commits (no task IDs needed)
git commit -m "feat: implement auth system"

# Reference tasks in PR body only
echo "Implements Task 4" >> pr-description.md
```

## Best Practices

### Task Management
- **Start broad** with high-level features in PRD
- **Use `--research` flag** for AI-enhanced analysis
- **Break down incrementally** as you learn more
- **Update subtasks** with implementation details
- **Keep status current** for team coordination

### Documentation Integration
- **Capture ideas** in .context/ideas.md before tasks
- **Research solutions** and log in .context/research.md
- **Document failures** immediately in .context/scratch_history.md
- **Cross-reference** between TaskMaster and .context docs
- **Learn from history** to avoid repeated mistakes

## Documentation Files

### Supporting Documents (in .context/)
- **.context/research.md:** Technical exploration and references
- **.context/ideas.md:** High-level design and concepts
- **.context/scratch_history.md:** Failed attempts and lessons

### When to Use Each
- **TaskMaster:** Task tracking and dependencies
- **.context/research.md:** When exploring technical solutions
- **.context/ideas.md:** Before breaking down into tasks
- **.context/scratch_history.md:** After failed attempts

---

*See `taskmaster_reference.mdc` for complete MCP tool and CLI command reference.*
*Documentation-driven development + TaskMaster = comprehensive project tracking.* 