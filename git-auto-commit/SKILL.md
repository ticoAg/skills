---
name: git-auto-commit
description: Create a Conventional Commits message (Chinese) and run `git commit` after reviewing `git --no-pager diff HEAD` exactly once.
---

# Git Auto Commit (Conventional Commits)

Goal: review the full diff from `HEAD` once, then commit with a Conventional Commits message (Chinese).

## Steps

1. **Check repo + status**
    - `git rev-parse --show-toplevel`
    - `git status -sb`

2. **Review changes (exactly once)**
    - `bash ~/.codex/skills/git-auto-commit/scripts/observe_changes.sh`
    - This must be the only time you run `git --no-pager diff HEAD` for this commit.

3. **Draft commit message (Chinese, Conventional Commits)**
    - Line 1: `<type>(<scope>): <subject>` or `<type>: <subject>`
    - Line 2: blank
    - Optional: 1–5 bullets starting with `- `
    - Keep `<subject>` imperative and specific (<= 72 chars).
    - Common `type`: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `ci`, `build`.

4. **Commit**
    - `printf '%s\n' "$COMMIT_MSG" | bash ~/.codex/skills/git-auto-commit/scripts/commit.sh`
    - The script stages all changes (`git add -A`), no-ops if nothing to commit, then runs `git commit`.

## Minimal example

- Observe: `bash ~/.codex/skills/git-auto-commit/scripts/observe_changes.sh`
- Commit: `printf '%s\n' "$COMMIT_MSG" | bash ~/.codex/skills/git-auto-commit/scripts/commit.sh`
