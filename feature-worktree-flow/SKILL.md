---
name: feature-worktree-flow
description: A git-worktree-based feature development flow: clarify requirements, create a `feat/<name>` branch in a sibling worktree, ship an MVP, validate, explain changes, then squash-merge back to the baseline branch.
---

# Feature Worktree Flow

## Overview

This workflow uses `git worktree` to keep feature work isolated while staying fast to switch. It emphasizes clarifying requirements (and disagreements) first, shipping an MVP, then explaining/validating the result and squash-merging back to the baseline branch (the original branch you want to merge into; by default, your current branch).

## Flow Summary

1. Propose an approach and wait for confirmation
2. Clarify requirements and record disagreements
3. Create a worktree + `feat/<name>` branch (based on the baseline branch)
4. Build the MVP and self-test
5. Explain changes and how to verify them
6. Squash-merge back to the baseline branch (single commit) and clean up the worktree

## Step 0: Requirement Clarification + Disagreement Log

- Ask clarifying questions: goals, scope, acceptance criteria, timeline, edge cases
- Make disagreements explicit and write them down; if unresolved, pause before coding
- Use this template:

```
Disagreement Log
- Topic:
- View A:
- View B:
- Current decision:
- Open questions:
```

## Step 1: Create the Worktree + Branch

- Ensure the original repo is clean and you are on the baseline branch you want to merge into (default: current branch)
- Note the baseline branch name (you will merge back into it later)
- Create the worktree as a sibling directory; branch naming: `feat/<name>`

Example (run from the original repo):

```
BASE_BRANCH="$(git branch --show-current)"
git fetch origin
git pull --ff-only
git worktree add ../<repo-name>-feat-<name> -b feat/<name> "$BASE_BRANCH"
```

## Step 2: Build the MVP

- Implement the smallest end-to-end slice that satisfies the current requirements; avoid scope creep
- If requirements become unclear or disagreements expand, return to Step 0

## Step 3: Self-Test + Prepare for Acceptance

- Run relevant tests or the minimal verification steps
- Summarize the key changes and prepare to explain the outcome

## Step 4: Acceptance + Explanation

- Explain “what changed, what it enables/fixes, and how to verify”
- Use this structure:

```
Acceptance Notes
- Changes:
- Expected outcome:
- How to verify:
- Impact / risks:
```

## Step 5: Commit + Squash-Merge Back to Baseline

- While developing, use `git-auto-commit` to help craft a Conventional Commit message and commit
- When merging back, use a squash merge so the final history has a single commit (no `Merge:` entry)

Back in the original repo, return to the baseline branch and update it:

```
git checkout <base-branch>
git pull --ff-only
```

Run a squash merge:

```
git merge --squash feat/<name>
```

- Resolve conflicts as needed; after that, the changes will be staged and ready to commit
- Use `git-auto-commit` (or your team's standard) to create the final squash commit
- Push or open a PR per your team's process (on hosting platforms you can also choose “Squash and merge”)

## Step 6: Clean Up the Worktree (Required)

After merging, remove the worktree directory (avoid leftover working dirs + worktree metadata):

```
git worktree remove ../<repo-name>-feat-<name>
git worktree prune
```

- If `git worktree remove` complains the worktree is not clean: check for uncommitted changes (commit/stage/discard), and only use `--force` if you accept losing uncommitted work.

(Optional) delete the merged branch:

```
git branch -d feat/<name>
git push origin --delete feat/<name>
```

## Notes

- Do not proceed to coding while key disagreements are unresolved
- Default baseline branch is your current branch; branch naming: `feat/<name>`
- Keep the worktree directory as a sibling to the original project directory
