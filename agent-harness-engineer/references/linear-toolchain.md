# Linear Toolchain Guidance

Use this reference when the repo wants Linear as part of its development toolchain.

## Recommended scope

Document these items:

- workspace / team / project ownership
- issue labels, priorities, and status mapping
- cycle / milestone usage
- how Linear state maps to roadmap files, task files, or delivery docs

## Important boundary

Linear is a collaboration and planning system. It is not the source of truth for:

- implementation facts
- test results
- acceptance status
- merged code state

Those remain in code, docs, and verification artifacts.

## Integration rule

This bootstrap skill may scaffold `docs/dev-toolchain/linear.md`, but any actual issue/project operations should use the separate `linear` skill.
