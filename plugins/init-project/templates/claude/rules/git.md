# Git & Version Control Standards

## Commit Messages
- **Format:** `<type>: <description>`
- **Length:** <50 characters
- **No emojis** in commits or PR titles
- **No AI attribution** (no "Co-Authored-By: Claude" or similar)
- **Types:**
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation only
  - `refactor:` Code restructuring
  - `test:` Adding tests (real tests only)
  - `chore:` Maintenance tasks

## Branch Strategy
- **Feature branches:** `feature/issue-N-short-description`
- **Bugfix branches:** `fix/issue-N-description`
- **Use `gh issue develop`** to create branches from issues
- **No spaces** in branch names, use hyphens
- **Delete after merge**

## Commit Practice
- **Atomic commits** - One logical change per commit
- **Test before commit** - Ensure code works
- **No broken commits** - Each commit should work independently

## Pull Request Process
1. Create issue first (for significant changes)
2. Use `gh issue develop` to create branch
3. Make atomic commits
4. Push branch
5. Create PR with `gh pr create`:
   - Clear title (<70 chars, no emojis)
   - Description with "Fixes #123"
   - Test results summary
6. Run `/review-pr` and address ALL findings
7. Squash merge to keep history clean

## Merge Strategy
- **Squash merge** for feature branches (clean history)
- **Rebase** to update feature branches from base (`git rebase origin/main`)
- **Never force-push** to shared branches (main, develop)
- **Delete branch** after merge

## Git Commands
```bash
# Start feature from issue
gh issue develop 123

# Atomic commits
git add -p  # Stage selectively
git commit -m "feat: add user authentication"

# Update branch
git fetch origin
git rebase origin/main

# Push and create PR
git push -u origin feature/issue-123-auth
gh pr create
```

## .gitignore Essentials
```
__pycache__/     # Python
node_modules/    # JavaScript
.env             # Secrets
*.log            # Logs
.venv/           # Virtual environments
```

---
*Atomic commits, clear messages, clean history. No emojis, no AI attribution.*
