# Continuous Rule Improvement

## Philosophy: Rules Grow from Understanding
**Think deeply:** Why did this pattern emerge? What problem does it solve?
**Learn actively:** Every project teaches something - capture it.
**Evolve thoughtfully:** Rules should guide, not constrain creativity.

## Improvement Triggers
- Pattern used 3+ times → Create rule
- Common failures in .context/scratch_history.md → Add prevention rule
- Successful .context/research.md solutions → Standardize
- Mature .context/ideas.md concepts → Formalize
- Repeated PR feedback → Document standard

## Analysis Sources
1. **.context/scratch_history.md:** Mine for anti-patterns
2. **.context/research.md:** Extract proven solutions  
3. **.context/ideas.md:** Promote design principles
4. **.context/plan.md:** Identify workflow patterns
5. **Code reviews:** Track common feedback

## Rule Updates

### Add Rules When:
- New pattern appears 3+ times
- Common bug could be prevented
- Better approach discovered
- Security/performance pattern emerges

### Modify Rules When:
- Better examples found in codebase
- Edge cases discovered
- Implementation changed
- Related rules updated

### Remove Rules When:
- Tech stack changed
- Pattern deprecated
- No longer applicable

## Quality Checks
- **Actionable:** Clear what to do
- **Specific:** No ambiguity
- **Examples:** From actual code
- **Cross-referenced:** Link related rules

## Learning-Driven Creation
**Extract wisdom, not just fixes:**
```python
# From .context/scratch_history.md failure:
# "Database connections leaked after 24hrs"
# THINK: Why? Resource management issue.
# LESSON: Explicit cleanup isn't reliable.
# → Rule: Always use context managers

with get_db() as db:  # Guaranteed cleanup
    process(db)
# Not: db = get_db(); process(db); db.close()  # Risky
```

**Ask yourself:**
- What's the root cause?
- Will this prevent future issues?
- Is this a symptom of a bigger pattern?

## Thoughtful Maintenance Process
1. **Weekly:** Review .context/scratch_history.md - What patterns emerged?
2. **After features:** Mine .context/research.md - What worked well?
3. **Post-refactor:** Update rules - What changed fundamentally?
4. **Quarterly:** Audit all - Are rules still serving us?

**Critical questions:**
- Are developers following these rules naturally?
- Do rules prevent issues or create friction?
- What would a new team member need to know?

## The Bigger Picture
**Rules aren't just constraints** - they're collective wisdom.
**Good rules:** Enable creativity within proven patterns.
**Bad rules:** Create busywork without clear value.

**Remember:** You're codifying experience for future developers (including future you).

---
*Rules evolve from understanding. Think deeply, document failures, standardize successes thoughtfully.*