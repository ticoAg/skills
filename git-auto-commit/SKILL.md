---
name: git-auto-commit
description: Workflow skill for generating a Conventional Commits message (English) and running `git commit` after reviewing `git --no-pager diff HEAD` exactly once.
---

# Git Commit Helper (Conventional Commits)

Goal: without missing any changes, review the full diff from `HEAD` once, then write a Conventional Commits message (in English) and run `git commit`.

## Workflow

1. **Confirm you are in the right repo**
    - `git rev-parse --show-toplevel`
    - `git status -sb`

2. **Review all changes from `HEAD` (single shot)**
    - Run `~/.codex/skills/git-auto-commit/scripts/observe_changes.sh` (it runs `git --no-pager diff HEAD` exactly once)
    - Focus on: intent, external behavior changes (API/protocol/error codes/contracts), migration/config risk

3. **Write the commit message (English + Conventional Commits)**
    - Format (follow strictly):
        - Line 1: `<type>(<scope>): <subject>` or `<type>: <subject>`
        - Line 2: blank
        - Lines 3–7: 1–5 bullets, each starts with `- ` (bullets optional)
    - Subject guidelines:
        - Start with an imperative verb, English, <= 72 chars (incl. punctuation)
        - Avoid vague subjects like “update stuff” or “misc changes”
    - Suggested `type`:
        - `feat` feature; `fix` bugfix; `refactor` refactor; `perf` performance; `docs` docs; `test` tests; `chore` tooling/deps; `ci` pipeline; `build` build system
    - Suggested `scope` (pick 1 based on the main folder you touched):
        - `api` / `backend-rs` / `openspec` / `conf` / `docs` / `migrations` / `subprojects`
    - Bullet suggestions:
        - Key behavior changes / fixes
        - Impact radius (modules, APIs, deploy)
        - Migration / rollback notes (if any)

4. **Run the commit**
    - Pipe your commit message into `~/.codex/skills/git-auto-commit/scripts/commit.sh`
    - The script will:
        - `git add -A` (add/update/delete)
        - Exit early if the index is empty
        - `git commit -F <message-file>`

## Example usage (for the AI)

- Observe: `bash ~/.codex/skills/git-auto-commit/scripts/observe_changes.sh`
- Generate a commit message (per the format above)
- Commit: `printf '%s\n' "$COMMIT_MSG" | bash ~/.codex/skills/git-auto-commit/scripts/commit.sh`
