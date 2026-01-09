---
name: code-simplifier-ts
description: Behavior-preserving TypeScript/JavaScript refactor for clarity and maintainability (respects repo ESM/CJS setup).
---

# TypeScript/JavaScript Code Simplifier (behavior-preserving)

Goal: refine recently changed TS/JS code for clarity and maintainability while **strictly preserving observable behavior**.

This skill assumes **Prettier** is the canonical formatter and **pnpm** is the package manager.

## When to use

- The user asks for `refactor` / `simplify` / `cleanup` and explicitly wants no behavior changes.
- You finished a feature/fix and want a small readability pass on the touched code and its immediate call sites.

## Hard constraints (do not violate)

1. **Behavior preserving**: return values, thrown errors / rejected promises, timing/ordering (where observable), I/O, and side effects stay the same.
2. **Follow repo standards**: `AGENTS.md`, ESLint/Prettier/tsconfig, and existing style win.
3. **Do not “flip” module systems**: ESM/CJS, import extensions, path aliases, and tsconfig module settings are build-sensitive—do not change unless the repo already uses it and the user asked.
4. **Avoid abstraction for its own sake**: only introduce interfaces/DI when the payoff is obvious and the diff is small.
5. **Keep the blast radius small**: avoid repo-wide formatting or sweeping renames unless requested.

## What to improve (safe, high-value)

- Flatten nested logic with guard clauses; avoid nested ternaries.
- Improve types at boundaries (exports, I/O, APIs) where it reduces ambiguity.
- Split multi-responsibility functions (parse/validate/transform/side-effects) into cohesive helpers.
- Reduce deep chaining when it harms readability; keep “why” comments, remove “what” comments.

## Workflow

1. Scope: focus on what changed (`git diff`) and its immediate call sites.
2. Refactor: make small edits first (naming, guards, small extractions), then optional structure improvements.
3. Automate: run the bundled scripts:
   - Format: `bash ~/.codex/skills/code-simplifier-ts/scripts/format.sh`
   - Prettier check: `bash ~/.codex/skills/code-simplifier-ts/scripts/check.sh`
   - Verify (also runs optional `pnpm run lint|typecheck|test` if present): `bash ~/.codex/skills/code-simplifier-ts/scripts/verify.sh`
4. Summarize: explain what changed and how to validate.

## Notes on the scripts

- `format.sh` runs `pnpm exec prettier --write .`
- `check.sh` runs `pnpm exec prettier --check .`
- `verify.sh` runs `check.sh`, then (if `package.json` has them) runs `pnpm -s run lint`, `pnpm -s run typecheck`, `pnpm -s run test`.
