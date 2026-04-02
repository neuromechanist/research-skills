# Simple Planning Approach

**Goal:** Documentation-driven development for {{PROJECT_NAME}} using multiple markdown files for comprehensive tracking and learning.

## When to Use

### ✅ Recommended For
- **Solo developers** or small teams (2-3 people)
- **Learning-oriented** projects needing documentation
- **Research-heavy** work with exploration phases
- **Short-to-medium term** projects (1-8 weeks)
- **Projects needing** decision tracking and rationale

### ❌ Not Recommended For
- **Large teams** (4+ developers) needing coordination
- **Complex dependencies** and multi-phase projects
- **Long-term projects** (3+ months) with evolving scope

## Quick Setup

```bash
# Copy templates to project
cp -r templates/planning/simple/.context ./
cp templates/planning/simple/*.mdc ./

# Replace placeholders in all files
find .context -name "*.md" -exec sed -i 's/{{PROJECT_NAME}}/my-project/g' {} \;
sed -i 's/{{PROJECT_NAME}}/my-project/g' *.mdc

# Add to .gitignore (if not already present)
echo ".context/" >> .gitignore
```

## Usage

### Task Tracking (.context/plan.md)
- **Pending:** `- [ ] Task name`
- **In Progress:** `- [⚠️] Task name`  
- **Researching:** `- [🔬] Task name`
- **Complete:** `- [x] Task name`

### Documentation Files (in .context/)
- **.context/plan.md:** Task lists and project phases
- **.context/research.md:** Technical solutions and references
- **.context/ideas.md:** Design concepts before implementation
- **.context/scratch_history.md:** Failed attempts and lessons

### Best Practices
- **Start with .context/ideas.md** for design exploration
- **Update .context/research.md** when exploring solutions
- **Track failures** in .context/scratch_history.md immediately
- **Keep tasks small:** 2-8 hours of work each
- **Cross-reference docs:** Use `(see research.md#section)`
- **Update daily** during active development

### Git Integration
```bash
# Concise commits without task references
git commit -m "feat: implement user model"

# .context stays local (in .gitignore)
# Only force-add if sharing with team:
git add -f .context/plan.md .context/research.md
git commit -m "docs: share project context"
```

## File Structure
```
{{PROJECT_NAME}}/
├── .context/           # Development context (gitignored)
│   ├── plan.md        # Task tracking
│   ├── research.md    # Technical research
│   ├── ideas.md       # Design concepts
│   └── scratch_history.md  # Failed attempts
├── dev_workflow.mdc    # AI workflow rules
├── src/                # Source code
├── tests/              # Test files
└── README.md          # Project overview
```

## Workflow Example

1. **Ideation:** Write high-level concept in .context/ideas.md
2. **Research:** Explore approaches in .context/research.md
3. **Planning:** Break down into tasks in .context/plan.md
4. **Development:** Implement while updating task status
5. **Learning:** Document failures in .context/scratch_history.md
6. **Iteration:** Update all .context docs with insights

---

*Documentation-driven development helps you learn from every project.* 