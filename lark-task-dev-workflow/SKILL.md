---
name: lark-task-dev-workflow
description: Start a lightweight development workflow from a Feishu/Lark task guid, short task ID, or task applink. Use when Codex should read a task, auto-provision or repair the lightweight `研发状态` single-select field on the tasklist when permissions allow, then guide task understanding, implementation in a worktree, final commit, merge-back to the source branch, worktree cleanup, and task status sync without relying on local cached field metadata.
---

# Lark Task Dev Workflow

## Overview

Use Feishu Tasks as the human-facing entry point for lightweight development work. Preflight the task first, let the script auto-create or repair the `研发状态` field when possible, then read the task, explain the intended work, wait for approval, and only then move into implementation.

## Required Files

- Resolve bundled files relative to this `SKILL.md` directory. When your shell `workdir` is a project repo, call scripts with an absolute path like `python3 <skill-dir>/scripts/check_task_status_readiness.py`; do not assume `scripts/` exists in the repo.
- Use `scripts/check_task_status_readiness.py` before touching code. This script exists because current `lark-cli task` does not provide an equivalent one-shot bootstrap/repair flow for the `研发状态` custom field.
- Use `scripts/update_task_status.py` for status changes after approval. This script exists because the task status label must first be resolved to the tasklist custom-field option GUID at runtime.
- Use `scripts/task-v2-cli/main.py` when installed `lark-cli task ...` lacks a Task v2 resource or action, especially task comment reads. See `references/task-v2-cli.md`.
- Read `references/task-status-bootstrap.md` when the readiness check reports permissions, wrong field type, or other blocking conditions the agent cannot auto-repair.
- Read `references/task-custom-field-auth.md` only when the blocker is `task:custom_field:*` authorization and you need the known-good re-auth pattern.

## Constraints

- Prefer runtime discovery through Task OpenAPI over any local field/option cache.
- Prefer registered `lark-cli task ...` commands first. If the installed CLI does not expose the needed Task v2 resource or action, prefer the bundled `scripts/task-v2-cli/main.py` wrapper before falling back to raw `lark-cli api`.
- Keep custom scripts minimal and stable. In this skill, scripts are reserved for unsupported automation gaps: `研发状态` bootstrap/repair, runtime label→option GUID status sync, and the Task v2 CLI wrapper used when installed `lark-cli task ...` does not expose a needed Task v2 resource.
- If authorization, identity switching, scope repair, or `lark-cli` usage details become uncertain, prefer reading the relevant official `lark-*` skills first instead of reverse-engineering from trial and error.
- Do not persist tasklist field GUIDs or option GUID mappings in local files.
- The only supported lightweight status model is `待开始` → `开发中` → `待测试` → `修复中` → `已完成`.
- If the task is associated with multiple tasklists, use the first `tasklist_guid` returned by task detail as the workflow container unless the user explicitly says otherwise.
- If the installed `lark-cli task` command set cannot cover a needed Task v2 operation, use `scripts/task-v2-cli/main.py` as the default protocol-aware fallback. Only drop to raw `lark-cli api` when the wrapper itself still lacks the needed path.
- At task-understanding time, focus on information sources rather than a single command path: task `summary`, task `description`, relevant task comments, relevant attachments, and linked source docs are all part of the initial evidence set.
- If task execution, auth, attachment reading, comment writing, or people-resolution behavior becomes unclear, fall back to the relevant `lark-*` skills instead of improvising unsupported calls.

## Related Lark Skills

- Treat these official `lark-*` skills as the first fallback for auth or usage uncertainty before ad-hoc exploration.
- For auth, scopes, identity switching, and permission failures, read `lark-shared` first.
- For task read/write behavior, comments, tasklists, and task mutations, read `lark-task` first.
- For attachments, Drive files, imports, exports, comments on docs, or file tokens, read `lark-drive`.
- For resolving people names or user IDs, read `lark-contact`.
- When registered CLI commands are insufficient and you need raw Task OpenAPI paths, read `lark-openapi-explorer`.

## Workflow

### 1. Normalize the task ID

- Accept a raw task GUID, a short task ID like `t100169`, or a full Feishu task applink.
- If the input is an applink, extract the `guid` query parameter first.
- If the input is a short task ID, prefer native CLI discovery first, for example `lark-cli task +search --query "<short-id>" --format json`, then disambiguate with `task_id`, URL, or follow-up `lark-cli task tasks get`.
- Do not add ad-hoc helper scripts for routine task reading. Use registered `lark-cli task ...` commands first, then `scripts/task-v2-cli/main.py` for Task v2 gaps.

### 2. Run readiness check first

Run:

```bash
python3 <skill-dir>/scripts/check_task_status_readiness.py --task-id "<task-guid-short-id-or-applink>"
```

Interpret the result conservatively:

- If the command exits with `0`, treat it as a silent pass and continue directly.
- The readiness check may auto-create the `研发状态` field, auto-create missing options, and unhide required options when current permissions allow.
- If the command prints Markdown, stop. The printed guidance is the remaining blocking work, typically auth/scope repair or manual cleanup of an incorrectly typed field.
- Do not wrap the script result into JSON in your user-facing reply.
- If the blocker is specifically `task:custom_field:*`, read `references/task-custom-field-auth.md` and follow that narrower auth recovery note before retrying readiness.

### 3. Read and restate the task

- Prefer native CLI commands to read task context:

```bash
lark-cli task tasks get --params '{"task_guid":"<task-guid>"}' --format json
```

- In the current CLI, `lark-cli task tasks get` provides task detail including fields such as `summary`, `description`, attachments, origin links, and tasklists.
- Before inventing a custom path for comments or other Task v2 resources, inspect the installed CLI first with `lark-cli task --help` and `lark-cli schema task`.
- If the current `lark-cli task` command set still has no registered Task v2 command for the needed read path, use the bundled Task v2 wrapper:

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments list --task-id "<task-guid-short-id-or-applink>" --page-size 100
```

- Read `references/task-v2-cli.md` for additional Task v2 wrapper examples and write-safety rules.
- Default task-understanding read order when native `lark-cli task ...` coverage is incomplete:
  1. `lark-cli task tasks get`
  2. `python3 <skill-dir>/scripts/task-v2-cli/main.py comments list`
  3. `python3 <skill-dir>/scripts/task-v2-cli/main.py custom-fields list` / `attachments list` / other needed Task v2 reads
  4. linked origin docs or attachments
- Do not jump straight from native CLI gaps to ad-hoc raw API calls if the wrapper already covers the Task v2 path.
- If the comment API paginates, continue with `page_token` until `has_more` is false.
- Always inspect these information sources before implementation:
  - task `summary`
  - task `description`
  - relevant task comments
  - relevant attachments or linked docs when present
- Do not rely on the title/summary alone.
- If description or comments are unread, or permissions block them, treat task understanding as incomplete and stop before implementation.
- If comment reading is blocked by permission, re-auth with at least `task:task:read` and `task:comment:read`, then retry the native `lark-cli` path.
- Inspect attachments if they are relevant to implementation.
- Summarize:
  - target outcome
  - scope and impact
  - acceptance signal
  - unresolved ambiguity
- Treat an explicit implementation request in the user's current turn (for example "修复/实现/开始开发 t123") as approval to proceed after the summary unless there is unresolved ambiguity, destructive risk, or repo workflow requiring a separate checkpoint.
- If the user only provides a task ID, asks for understanding, or the expected change is ambiguous, wait for approval before moving into worktree creation, status changes, or code changes.

### 4. Sync status before and during execution

- Treat `研发状态` as the current execution phase marker for the task, and actively keep it in sync with the real stage of work instead of updating it only at the very end.
- After approval and before coding, move the task to `开发中`:

```bash
python3 <skill-dir>/scripts/update_task_status.py --task-id "<task-guid-short-id-or-applink>" --label "开发中"
```

- If work has not started yet or you are still blocked before implementation, keep or restore the task at `待开始`.
- When handing work over for verification, move the task to `待测试`.
- If testing reveals issues, move the task to `修复中`.
- After fixing and handing back, move the task to `待测试` again.
- Only after user confirms the task passes should it move to `已完成`.
- Every time the task crosses one of these real workflow boundaries, call `scripts/update_task_status.py` promptly so the custom field reflects the true current stage.

### 5. Follow the implementation flow

- Use the approved task understanding as the implementation contract.
- Follow the existing repo's worktree or planning workflow for actual coding.
- If the repo expects isolated feature work, create a dedicated worktree from the current source/base branch before editing.
- Keep the source/base branch name and the feature worktree path explicit in progress notes so closeout is traceable.
- Keep the custom-field status lightweight and keep richer progress in task comments.

### 6. Close out the worktree and source branch

- After implementation and verification are complete, create a real commit on the feature branch.
- Merge the feature branch back into the original source/base branch using the repo's expected merge strategy.
- Remove the feature worktree after the merge succeeds.
- Delete the temporary feature branch after the worktree is removed.
- Only treat the development round as fully closed when commit, merge-back, worktree cleanup, and branch cleanup are all finished.

### 7. Write back results

- When a development round finishes, add a task comment summarizing:
  - what changed
  - how to verify
  - remaining risk
- Keep the task comment and the `研发状态` custom field aligned with the same handoff stage.
- Before moving the task to `已完成`, ensure the commit has been merged back to the source branch and the temporary worktree/branch have been cleaned up.
- Then update the `研发状态` field to match the handoff state.

## Automatic Bootstrap and Repair

- If the tasklist is missing `研发状态`, preflight should create it automatically as a `single_select` field with these labels:
  - `待开始`
  - `开发中`
  - `待测试`
  - `修复中`
  - `已完成`
- If the field exists but is missing some required labels, preflight should add them automatically.
- If a required label exists but is hidden, preflight should unhide it automatically.
- If the field exists with the wrong type, stop and use `references/task-status-bootstrap.md` to guide manual repair.
- If custom-field read/write scopes are missing, stop and use `references/task-status-bootstrap.md` to guide re-authorization.

## Output Expectations

- On success, stay quiet about the readiness check and continue into task understanding.
- On failure, reuse the script's Markdown guidance instead of inventing a separate error format.
- If blocked, keep the message focused on what must be repaired next.
