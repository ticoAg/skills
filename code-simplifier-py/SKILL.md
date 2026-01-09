---
name: code-simplifier-py
description: Behavior-preserving Python refactor for readability (PEP 8, Pythonic idioms, minimal SOLID).
---

# Python Code Simplifier (behavior-preserving)

Goal: refine recently changed Python code for clarity and maintainability while **strictly preserving observable behavior**.

This skill assumes **Ruff** is the canonical formatter/linter.

## When to use

- The user asks for `simplify` / `refactor` / `cleanup` and explicitly wants “no behavior changes”.
- You just implemented a feature/fix and want a small, safe readability pass on the touched areas.

## Hard constraints (do not violate)

1. **Behavior preserving**: outputs, exceptions (type + message), return values, I/O, side effects, and externally visible logs stay the same.
2. **Small diffs**: do not “format the whole repo” unless requested.
3. **Follow repo standards**: `AGENTS.md` + existing style + existing tooling config wins over generic rules.
4. **No new dependencies**: do not add third-party packages.
5. **No “SOLID theater”**: only introduce abstractions when the benefit is obvious and the diff is small.

## What to improve (safe, high-value)

- Flatten control flow with guard clauses / early returns.
- Split oversized functions into cohesive helpers with intention-revealing names.
- Replace overly clever comprehensions with readable loops when it helps.
- Remove magic constants via named constants (without changing exported APIs).
- Tighten error handling boundaries without changing error semantics.

## Workflow

1. Scope: focus on the code touched in the current change (`git diff`).
2. Refactor: apply small, behavior-preserving edits in priority order: clarity → structure (only if low-risk).
3. Automate: run the bundled scripts (they respect repo Ruff config):
   - Format: `bash ~/.codex/skills/code-simplifier-py/scripts/format.sh`
   - Lint: `bash ~/.codex/skills/code-simplifier-py/scripts/check.sh`
   - Optional auto-fix lint: `bash ~/.codex/skills/code-simplifier-py/scripts/check.sh --fix`
   - Verify: `bash ~/.codex/skills/code-simplifier-py/scripts/verify.sh`
4. Summarize: explain what changed and why it is safer/clearer.

## Notes on the scripts

- `format.sh` runs `ruff format .`
- `check.sh` runs `ruff check .` (optionally `--fix`)
- `verify.sh` runs `check.sh`, then `python -m compileall .`, then runs `pytest` only when a `tests/` (or `test/`) folder exists and `pytest` is available.
