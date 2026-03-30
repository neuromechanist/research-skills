#!/bin/bash
# Detect repository configuration for epic workflow.
# Outputs key=value pairs for consumption by the epic-dev command.
set -euo pipefail

# Validate we are inside a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR=Not inside a git repository"
  exit 1
fi

# Integration branch: prefer develop, fall back to default branch
if git rev-parse --verify develop >/dev/null 2>&1 || \
   git rev-parse --verify origin/develop >/dev/null 2>&1; then
  echo "INTEGRATION_BRANCH=develop"
else
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  if [ -z "$DEFAULT" ]; then
    DEFAULT=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
  fi
  if [ -z "$DEFAULT" ]; then
    if git rev-parse --verify main >/dev/null 2>&1; then
      DEFAULT="main"
    elif git rev-parse --verify master >/dev/null 2>&1; then
      DEFAULT="master"
    else
      DEFAULT="main"
      echo "INTEGRATION_BRANCH_WARNING=Could not detect default branch; assuming 'main'"
    fi
  fi
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

# Active worktrees
WORKTREE_OUTPUT=$(git worktree list --porcelain 2>&1) || {
  echo "WORKTREE_COUNT=0"
  echo "WORKTREE_ERROR=Failed to list worktrees"
  WORKTREE_OUTPUT=""
}
if [ -n "${WORKTREE_OUTPUT:-}" ]; then
  WORKTREE_COUNT=$(echo "$WORKTREE_OUTPUT" | grep -c '^worktree ' || echo "0")
  echo "WORKTREE_COUNT=${WORKTREE_COUNT}"
fi

# Check gh CLI availability and sub-issue extension
if ! command -v gh >/dev/null 2>&1; then
  echo "HAS_GH=false"
  echo "GH_ERROR=gh CLI is not installed"
elif ! gh auth status >/dev/null 2>&1; then
  echo "HAS_GH=false"
  echo "GH_ERROR=gh CLI is not authenticated (run 'gh auth login')"
else
  echo "HAS_GH=true"
  if gh extension list 2>/dev/null | grep -q 'sub-issue'; then
    echo "HAS_GH_SUBISSUE=true"
  else
    echo "HAS_GH_SUBISSUE=false"
  fi
fi

# Repo root (for absolute path construction)
REPO_ROOT=$(git rev-parse --show-toplevel 2>&1) || {
  echo "REPO_ROOT_ERROR=Failed to determine repository root: $REPO_ROOT"
  exit 1
}
echo "REPO_ROOT=${REPO_ROOT}"
