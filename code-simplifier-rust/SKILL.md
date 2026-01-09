---
name: code-simplifier-rust
description: Behavior-preserving Rust refactor for idiomatic clarity and maintainability (ownership-aware).
---

# Rust Code Simplifier (behavior-preserving)

Goal: refine recently changed Rust code for idiomatic clarity and maintainability while **preserving behavior** (including error paths and concurrency semantics where applicable).

This skill assumes `cargo fmt` and `cargo clippy` are the canonical tools.

## When to use

- The user asks for a readability/idiomatic pass and explicitly wants no functional changes.
- You shipped a feature/fix and want a small, safe cleanup on the touched modules.

## Hard constraints (do not violate)

1. **Behavior preserving**: return values, error types/paths, boundary behavior, and observable side effects remain unchanged.
2. **Risk control**: prefer small, verifiable changes; avoid big module boundary rewrites or large trait/generic refactors.
3. **Follow repo standards**: `AGENTS.md`, existing `rustfmt`/`clippy` configuration, and crate conventions win.
4. **Avoid “clever”**: do not replace readable code with hard-to-read iterator chains or macros.
5. **Performance-aware**: avoid introducing extra allocations/clones; reduce unnecessary `.clone()` when it improves clarity.

## What to improve (safe, high-value)

- Reduce nesting with `match` / `if let` / `let else`.
- Prefer idiomatic `Result`/`Option` flows (`?`, clear matches) over manual branching.
- Remove unnecessary conversions and temporary allocations.
- Encapsulate deep field navigation behind methods (Law of Demeter) when it improves readability.
- Add `///` docs to public APIs when it clarifies behavior (without changing it).

## Workflow

1. Scope: focus on what changed (`git diff`) and its immediate call sites.
2. Refactor: do low-risk readability improvements first; keep diffs tight.
3. Automate: run the bundled scripts:
   - Format: `bash ~/.codex/skills/code-simplifier-rust/scripts/format.sh`
   - Clippy: `bash ~/.codex/skills/code-simplifier-rust/scripts/check.sh`
   - Clippy with all features: `ALL_FEATURES=1 bash ~/.codex/skills/code-simplifier-rust/scripts/check.sh`
   - Clippy deny warnings: `DENY_WARNINGS=1 bash ~/.codex/skills/code-simplifier-rust/scripts/check.sh`
   - Verify: `bash ~/.codex/skills/code-simplifier-rust/scripts/verify.sh`
4. Summarize: explain the refactor and call out any safety/ownership simplifications.

## Notes on the scripts

- `format.sh` runs `cargo fmt`
- `check.sh` runs `cargo clippy --all-targets` (optional `ALL_FEATURES=1`, `DENY_WARNINGS=1`)
- `verify.sh` runs `format.sh`, `check.sh`, then `cargo test` (optional `ALL_FEATURES=1`)
