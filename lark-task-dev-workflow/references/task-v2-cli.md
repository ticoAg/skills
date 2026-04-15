# Task v2 CLI Wrapper

Use `scripts/task-v2-cli/main.py` when installed `lark-cli task ...` lacks a Task v2 resource or action, especially task comments.

The wrapper delegates all auth, profile, and identity handling to `lark-cli`; it does not read or manage tokens directly.

## Common Commands

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasks get --task-id t100169
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments list --task-id t100169 --page-size 100
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments get --task-id t100169 --comment-id "<comment_guid>"
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasklists tasks --tasklist-guid "<tasklist_guid>" --page-size 100
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py custom-fields list --params-json '{"resource_type":"tasklist","resource_id":"<tasklist_guid>"}'
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasks patch \
  --task-id t100169 \
  --data-json '{"task":{"summary":"updated title"},"update_fields":["summary"]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasklists patch \
  --tasklist-guid "<tasklist_guid>" \
  --data-json '{"tasklist":{"name":"updated list"},"update_fields":["name"]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py custom-fields create \
  --data-json '{"resource_type":"tasklist","resource_id":"<tasklist_guid>","name":"Priority","type":"text"}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py attachments upload \
  --task-id t100169 \
  --file /absolute/path/to/file.pdf \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasks add-members \
  --task-id t100169 \
  --data-json '{"members":[{"id":"<open_id>","type":"user","role":"assignee"}]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasks remove-tasklist \
  --task-id t100169 \
  --tasklist-guid "<tasklist_guid>" \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasklists add-members \
  --tasklist-guid "<tasklist_guid>" \
  --data-json '{"members":[{"id":"<open_id>","type":"user","role":"viewer"}]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py tasklists remove-members \
  --tasklist-guid "<tasklist_guid>" \
  --data-json '{"members":[{"id":"<open_id>","type":"user"}]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py custom-fields create-option \
  --custom-field-guid "<custom_field_guid>" \
  --data-json '{"name":"Blocked","color_index":16,"is_hidden":false}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py custom-fields patch-option \
  --custom-field-guid "<custom_field_guid>" \
  --option-guid "<option_guid>" \
  --data-json '{"option":{"is_hidden":false},"update_fields":["is_hidden"]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py subtasks create \
  --task-id t100169 \
  --data-json '{"summary":"child task"}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py sections create \
  --data-json '{"name":"In Progress","resource_type":"tasklist"}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py sections patch \
  --section-guid "<section_guid>" \
  --data-json '{"section":{"name":"Blocked"},"update_fields":["name"]}' \
  --yes
```

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py sections delete \
  --section-guid "<section_guid>" \
  --yes
```

## Write Safety

All write actions require either `--dry-run` or `--yes`.

Preview a comment write:

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments create \
  --task-id t100169 \
  --data-json '{"content":"handoff note"}' \
  --dry-run
```

Execute a comment write:

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments create \
  --task-id t100169 \
  --data-json '{"content":"handoff note"}' \
  --yes
```

Patch a comment. Task v2 comment patch requires top-level `comment` plus `update_fields`:

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments patch \
  --task-id t100169 \
  --comment-id "<comment_guid>" \
  --data-json '{"comment":{"content":"updated handoff note"},"update_fields":["content"]}' \
  --yes
```

Delete a comment. Do not pass `--data-json`:

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments delete \
  --task-id t100169 \
  --comment-id "<comment_guid>" \
  --yes
```

## Identity and Profile

Pass identity and profile the same way you would when using `lark-cli api`:

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments list \
  --task-id t100169 \
  --as user \
  --profile default
```

## Low-Level Escape Hatches

Use `--params-json` for query parameters and `--data-json` for request bodies when a Task v2 endpoint needs fields not exposed as first-class flags.

```bash
python3 <skill-dir>/scripts/task-v2-cli/main.py comments list \
  --task-id t100169 \
  --params-json '{"page_size":100}'
```

## Comment Scopes

Reading task comments requires Task v2 comment read permission:

- `task:comment:read`

Creating, updating, or deleting task comments requires write permission:

- `task:comment:write`

When comment reading returns a permission error under user identity, re-auth with the smallest needed scope:

```bash
lark-cli auth login --scope "task:comment:read"
```

For workflow status updates, existing `研发状态` scripts still require their own custom-field scopes.

## Protocol Notes

- `comments create` uses top-level Task v2 fields like `content`, `resource_type`, `resource_id`; do not wrap the body inside `comment`.
- `comments patch` uses the Task v2 partial-update shape: top-level `comment` plus top-level `update_fields`.
- `comments delete` does not accept a request body.
- `tasks create` uses Task v2 top-level fields like `summary`, `members`, `description`; do not wrap the body inside `task`.
- `tasks patch` uses top-level `task` plus top-level `update_fields`.
- `tasklists create` uses Task v2 top-level fields like `name`, `members`; do not wrap the body inside `tasklist`.
- `tasklists patch` uses top-level `tasklist` plus top-level `update_fields`.
- `custom-fields create` uses Task v2 top-level fields like `resource_type`, `resource_id`, `name`, `type`; do not wrap the body inside `custom_field`.
- `custom-fields patch` uses top-level `custom_field` plus top-level `update_fields`.
- `attachments upload` requires `--file`.
- `attachments delete` does not accept a request body.
- `tasks add-members` requires a top-level `members` array; each item must include non-empty `id` plus role `assignee` or `follower`.
- `tasks remove-tasklist` requires top-level `tasklist_guid`; this wrapper accepts `--tasklist-guid` and normalizes it into the request body.
- `tasklists add-members` requires a top-level `members` array; each item must include non-empty `id` plus role `editor` or `viewer`.
- `tasklists remove-members` requires a top-level `members` array and does not accept `role`.
- `custom-fields create-option` uses top-level fields like `name`, `color_index`, `is_hidden`; do not wrap the body inside `option`.
- `custom-fields patch-option` uses top-level `option` plus top-level `update_fields`.
- `subtasks create` uses Task v2 top-level fields like `summary`; do not wrap the body inside `task`.
- `sections create` uses Task v2 top-level fields like `name` and `resource_type`; do not wrap the body inside `section`.
- `sections patch` uses top-level `section` plus top-level `update_fields`.
- `sections delete` does not accept a request body.

## Typer Runtime

- The wrapper now uses `typer` for argument parsing.
- If the current Python interpreter cannot import `typer`, install it into the same interpreter environment used to run the script:

```bash
python3 -m pip install --user --break-system-packages 'typer>=0.12,<1'
```
