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
- **`[skip ci]`:** append to the subject when the commit touches only files no CI job reads (notes, `.context/`, `.memory/`, docs CI does not build): `docs: clarify setup [skip ci]`
  - GitHub reads only the head commit of a push; never push it on top of untested code commits
  - The token matches anywhere in the message, body included; never quote it in a commit you want tested
  - On a PR with required checks (`gh pr checks N --required`), do not use it; a skipped required check blocks merge
  - Exception: post-merge bot bump and sync commits on the integration branch always carry it (see `.rules/ci_cd.md`)

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
6. Review per `.rules/code_review.md`: at most one full review and one delta review
7. Fix review findings with commits on the same branch (one push per round). If that branch blocks direct pushes (release PRs), use one fix PR per round into it
8. Squash merge to keep history clean

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
