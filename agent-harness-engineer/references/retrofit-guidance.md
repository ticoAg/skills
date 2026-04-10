# Retrofit Guidance

Use this reference when the target repo already has some guidance docs.

## Default approach

Prefer `--write-mode safe`.

That gives you two behaviors:

- missing files are created in-place
- existing files get draft replacements under `.agent-native-bootstrap/`

## Retrofit workflow

1. Audit existing `AGENTS.md` and `docs/README.md`
2. Identify whether the repo already separates agent docs from engineering docs, architecture / ADR docs, or process archives
3. Generate drafts with the bootstrap script
4. Diff draft output against the current docs
5. Merge only the agent-layer improvements that fit the repo's real collaboration style
6. Re-run link checks after merging

## What to preserve

- repo-specific source-of-truth locations
- existing delivery expectations
- local security / approval / git-safety constraints
- any module-local `AGENTS.md` that already define real agent rules
- any adjacent engineering, architecture, ADR, or process doc trees that already carry real project truth

## What to normalize

- document layering and navigation
- tool / skill routing structure
- multi-agent collaboration expectations
- progressive-disclosure philosophy

## Boundary check

A retrofit is successful when:

- agent docs become clearer without expanding their scope
- engineering best practices remain in engineering docs or equivalent locations
- business / system decisions remain in architecture docs or equivalent locations
- plans, specs, and migration records remain in process / archive docs or equivalent locations

If a repo currently mixes these layers, the agent bootstrap should at most clarify the boundary and point to the right homes. It should not rewrite the entire project doc system into the agent layer.
