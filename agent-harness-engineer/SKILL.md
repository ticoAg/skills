---
name: agent-harness-engineer
description: Bootstrap or retrofit a repository with agent-only collaboration guidance, including AGENTS.md, docs/agent-skill-routing.md, docs/README.md, and optional docs/dev-toolchain/linear.md. Use when initializing a repo for agent-native collaboration, standardizing agent behavior across repos, or extracting business/framework-agnostic guidance from an existing repository. Keep the agent layer separate from project engineering best-practice docs, business or system architecture docs, and process or archive docs.
metadata:
  author: "github/ticoAg"
---

# Agent Harness Engineer

Bootstrap a repository with a focused agent-collaboration layer: agent behavior, tool usage, skill routing, progressive disclosure, and optional Linear toolchain documentation.

Author: `github/ticoAg`.

## Quick start

1. Audit only the agent-relevant repo context: `README.md`, existing `AGENTS.md`, existing `docs/README.md`, and any task / roadmap docs.
2. Decide whether this is a greenfield bootstrap or a retrofit of existing guidance.
3. Run the bootstrap script:
   - `python3 "$CODEX_SKILL_ROOT/scripts/bootstrap_repo.py" <repo-root>`
   - add `--with-linear` if the repo wants a documented Linear toolchain
   - add `--write-mode overwrite` only when you intentionally want to replace existing files
4. Review the generated files and replace placeholders or generic wording with repo-specific collaboration facts only where needed.
5. Verify links, commands, and document boundaries before claiming the bootstrap is complete.

## Scope

This skill is intentionally narrow.

It should define only:

- agent behavior and collaboration rules
- tool usage expectations
- skill selection and multi-agent routing
- progressive-disclosure document layering for agent docs
- optional project-management toolchain guidance such as Linear

It should not define:

- business-domain architecture
- product-specific workflows
- framework-specific engineering rules
- language-specific coding conventions
- verification matrices or implementation ownership models
- process plans, stage records, or migration archives

Those belong to the repo itself, not to this bootstrap skill.

## Document boundary principle

Preserve a clean separation between four documentation strata:

1. **Agent layer**
   - `AGENTS.md`
   - `docs/agent-skill-routing.md`
   - `docs/README.md`
   - optional agent toolchain docs such as `docs/dev-toolchain/linear.md`
2. **Engineering best-practice layer**
   - implementation rules
   - testing taxonomy
   - cross-cutting engineering guidance
3. **Architecture / decision layer**
   - business-boundary explanations
   - system partitioning
   - long-lived decision records
4. **Process / archive layer**
   - plans
   - stage designs
   - migration notes
   - implementation history

This skill owns only the first layer.

When a repo already has distinct engineering, architecture, or process docs, the generated agent docs should point to them, not absorb or rewrite them.

## Required workflow

### Step 1: Audit the repo at the agent layer

Read only the minimum needed to place the agent docs correctly:

- `README.md`
- existing `AGENTS.md`
- existing `docs/README.md`
- existing adjacent doc portals when present, such as engineering, architecture, ADR, decisions, plans, or archive indexes
- roadmap / plan / task-tracking docs if present

Goal: determine whether the repo already has an agent layer, what should remain the repo's source of truth, whether adjacent engineering / architecture / process trees already exist, and whether new docs should be created in-place or drafted for merge.

### Step 2: Choose bootstrap mode

Use one of these modes:

- `safe` (default): create missing files in-place; if a target already exists, write a draft copy under `.agent-native-bootstrap/`
- `draft`: write all generated output under `.agent-native-bootstrap/` for review first
- `overwrite`: replace target files directly

Default to `safe` for retrofits.

### Step 3: Generate the agent file set

Core file set:

- `AGENTS.md`
- `docs/agent-skill-routing.md`
- `docs/README.md`

Optional file set:

- `docs/dev-toolchain/linear.md` when `--with-linear` is enabled

Run:

```bash
python3 "$CODEX_SKILL_ROOT/scripts/bootstrap_repo.py" /path/to/repo --write-mode safe
```

With Linear:

```bash
python3 "$CODEX_SKILL_ROOT/scripts/bootstrap_repo.py" /path/to/repo --with-linear --write-mode safe
```

### Step 4: Keep the output generic and focused

When adapting generated docs, keep only repo-specific facts that help agents collaborate safely:

- where the repo's source-of-truth docs live
- where adjacent engineering, architecture, or process docs live when they already exist
- how the repo expects agents to communicate and deliver work
- which project-management toolchain is used

Do not add business logic, architecture ownership, framework conventions, or verification matrices unless the repo itself wants those elsewhere.
Do not collapse project engineering guidance, architecture guidance, or process archives into the agent layer just because the repo lacks perfect structure today.

### Step 5: Preserve progressive disclosure

Keep this layering intact:

1. `AGENTS.md` -> repo entry and high-level agent rules
2. `docs/agent-skill-routing.md` -> skill-selection logic
3. `docs/README.md` -> agent-doc portal and placement rules

Do not collapse everything into `AGENTS.md`.
Do not let `docs/README.md` pretend to be the repo's full architecture or engineering handbook; it should route to those docs when they exist.

## When to read references

- Read `references/file-set.md` when deciding which agent docs to create.
- Read `references/retrofit-guidance.md` when the target repo already has guidance docs.
- Read `references/linear-toolchain.md` when enabling Linear as part of the agent toolchain.

## Validation checklist

Before finishing:

- confirm generated paths match the intended agent-doc layout
- confirm `docs/README.md` links resolve
- confirm `AGENTS.md` and routing docs do not contradict each other
- confirm the generated agent docs do not absorb engineering best practices, business architecture, or process/archive content
- if the repo already has adjacent engineering / architecture / process docs, confirm the agent docs point to them instead of duplicating them
- if `--with-linear` was used, confirm the repo actually wants Linear documented at the toolchain layer

## Notes

- This skill scaffolds only the agent-collaboration layer.
- It may reference adjacent project docs, but it should not become the source of truth for them.
- For actual Linear issue/project operations after bootstrap, use the separate `linear` skill.
