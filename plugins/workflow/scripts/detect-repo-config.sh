#!/bin/bash
# Detect repository configuration for epic workflow.
# Outputs key=value pairs for consumption by the epic-dev command.
set -euo pipefail

# Integration branch: prefer develop, fall back to default branch
if git rev-parse --verify develop >/dev/null 2>&1 || \
   git rev-parse --verify origin/develop >/dev/null 2>&1; then
  echo "INTEGRATION_BRANCH=develop"
else
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
  echo "INTEGRATION_BRANCH=${DEFAULT}"
fi

# Epic state file
if [ -f .claude/epic.local.md ]; then
  echo "HAS_EPIC_STATE=true"
else
  echo "HAS_EPIC_STATE=false"
fi

# Current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
echo "CURRENT_BRANCH=${BRANCH}"

# Active worktrees (excluding the main one)
WORKTREE_COUNT=$(git worktree list --porcelain 2>/dev/null | grep -c '^worktree ' || echo "1")
echo "WORKTREE_COUNT=${WORKTREE_COUNT}"

# Check gh sub-issue extension
if gh extension list 2>/dev/null | grep -q 'sub-issue'; then
  echo "HAS_GH_SUBISSUE=true"
else
  echo "HAS_GH_SUBISSUE=false"
fi

# Repo root (for absolute path construction)
echo "REPO_ROOT=$(git rev-parse --show-toplevel)"
