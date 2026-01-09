# Codex Skills

This repository contains reusable Codex CLI skills.

- Each skill folder contains a `SKILL.md` with instructions.
- OpenAI upstream skills are kept under their original namespaces: `.curated/`, `.experimental/`, and `.system/`.
  - Convenience: top-level symlinks exist for `.curated/` and `.experimental/` skills.
  - `.system/` skills are *not* symlinked (they are already available under `.system/`).

## Structure

- `code-simplifier-py/`: Python refactor skill
- `code-simplifier-rust/`: Rust refactor skill
- `code-simplifier-ts/`: TypeScript/JavaScript refactor skill
- `.curated/`: Curated upstream skills (mirrors `openai/skills`)
- `.experimental/`: Experimental upstream skills (mirrors `openai/skills`)
- `feature-worktree-flow/`: Feature development workflow using `git worktree`
- `git-auto-commit/`: Helper workflow for crafting a Conventional Commit and running `git commit`
- `.system/`: Internal helper skills (e.g., skill installer/creator)
