# Runtime Learnings

Use this log for time-stamped operational lessons discovered during real usage.

- Keep entries concise.
- Put the newest entry first.
- Promote only durable defaults into `SKILL.md` or the narrowest reference file.
- Prefer `scripts/capture_runtime_learning.py` to append new entries so formatting stays consistent.

## 2026-04-15 — Task comment rewrite path

- Signal: A posted task handoff comment needed replacement after user feedback, without leaving two conflicting summaries on the task.
- Action: Prefer `scripts/task-v2-cli/main.py comments patch --yes` with `comment.content` and `update_fields:["content"]` when rewriting an existing task comment.
- Promote to: `references/task-v2-cli.md`
- Source: `task:t100167`

## 2026-04-15 — Task comment handoff style

- Signal: User corrected a verbose task comment that mixed bullet lists, verification commands, and result text.
- Action: Default task comments to one short Markdown paragraph that only states what changed; keep verification details in the agent delivery message.
- Promote to: `SKILL.md`
- Source: `task:t100167`
