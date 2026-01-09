#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: current directory is not inside a git repository" >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"

echo "== Repo =="
echo "$repo_root"
echo

echo "== Branch =="
echo "${branch}"
echo

echo "== Status (short) =="
git status -sb
echo

echo "== Status (porcelain) =="
git status --porcelain=v1
echo

echo "== Untracked =="
git ls-files --others --exclude-standard || true
echo

echo "== Diff from HEAD (single shot) =="
# Constraint: run this command exactly once to review all changes from HEAD
git --no-pager diff HEAD
