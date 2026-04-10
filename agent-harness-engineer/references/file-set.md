# File Set Guidance

Use this reference when deciding which files the bootstrap should create.

## Core file set

These files make up the focused agent layer:

- `AGENTS.md` -> repo entry, red lines, delivery rules, tool behavior
- `docs/agent-skill-routing.md` -> process/domain/collaboration/finishing skill routing
- `docs/README.md` -> portal for the repo's agent-facing docs

These files can link to adjacent project docs, but they should not absorb project engineering rules, architecture decisions, or process archives.

## Optional file set

Add only when the repo actually needs them:

- `docs/dev-toolchain/linear.md` -> if Linear is part of the project-management toolchain
- deeper module-level `AGENTS.md` -> if a subdirectory truly needs more specific agent rules

Adjacent project-doc trees such as `docs/engineering/`, `docs/architecture/`, `docs/adr/`, or `docs/process/` are not part of this skill's scaffold output. If they already exist, point agents to them. If they do not exist, do not invent their content inside the agent layer.

## Heuristic

- Default to the core file set.
- Keep the generated layer business-agnostic, framework-agnostic, and language-agnostic.
- Let project-specific architecture and implementation guidance live outside this bootstrap layer.
