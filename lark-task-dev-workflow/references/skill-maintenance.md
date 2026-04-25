# Skill Maintenance

Use this reference when a real task run teaches you something new about how `lark-task-dev-workflow` should behave.

## Document Layers

Keep changes in the narrowest durable layer.

1. **Stable workflow layer**
   - `SKILL.md`
   - Put only repeatable defaults, durable routing, and cross-session behavior here.

2. **Topic-specific reference layer**
   - `references/task-v2-cli.md`
   - `references/task-status-bootstrap.md`
   - `references/task-custom-field-auth.md`
   - Put command semantics, payload shapes, auth repair notes, and other focused operational facts here.

3. **Runtime experience layer**
   - `references/runtime-learnings.md`
   - Put dated observations, user corrections, and recently discovered friction here first when they are not yet mature enough for the stable layers.

4. **Automation layer**
   - `scripts/*.py`
   - Add or update scripts only when the lesson reveals a repeated deterministic gap that documentation alone will not solve reliably.

## Promotion Rules

Promote a lesson from the runtime layer into a stable layer when at least one of these is true:

- the user explicitly asks for the behavior to become the new default
- the same issue appears across multiple runs
- the lesson changes how the skill should normally write, route, or mutate data
- the lesson is tool-specific and would otherwise be rediscovered by trial and error

Keep one-off or uncertain findings in `references/runtime-learnings.md` until they prove stable.

## Update Decision Matrix

- **Workflow default changed** → update `SKILL.md`
- **Task v2 payload / comment / patch nuance** → update `references/task-v2-cli.md`
- **Auth or field bootstrap nuance** → update the relevant auth/bootstrap reference
- **Fresh user correction or recent operational surprise** → append to `references/runtime-learnings.md`
- **Repeated manual step should become deterministic** → add or patch a script

## Capture Loop

When a live run produces a correction or new lesson:

1. Summarize the signal in one sentence.
2. Decide the narrowest layer that should own it.
3. Append the raw lesson to `references/runtime-learnings.md` with `scripts/capture_runtime_learning.py`.
4. If the lesson is already durable, patch the stable target in the same session.
5. Keep the stable docs concise; do not copy the whole runtime note into `SKILL.md`.

## Example

- User says task comments should stop including verification commands by default.
- Append the dated lesson to `references/runtime-learnings.md`.
- Update `SKILL.md` because this changes the default write-back behavior.
- If the comment mutation path itself had command-specific nuances, also update `references/task-v2-cli.md`.
