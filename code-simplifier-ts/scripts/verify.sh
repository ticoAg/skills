#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

ensure_pnpm
collect_targets "$@"

has_script() {
  local pkg_dir="$1"
  local script_name="$2"
  node -e "const p=require('${pkg_dir}/package.json'); process.exit(p.scripts && p.scripts['${script_name}'] ? 0 : 1)" \
    >/dev/null 2>&1
}

log "verify: prettier + (optional) lint/typecheck/test"

bash "$SCRIPT_DIR/check.sh" "$@"

pnpm_dir="$(find_pnpm_dir "${TARGETS[0]}")" || die "no package.json found; set CODEX_PNPM_DIR or pass --dir"

for s in lint typecheck test; do
  if has_script "$pnpm_dir" "$s"; then
    log "pnpm --dir \"$pnpm_dir\" -s run $s"
    pnpm --dir "$pnpm_dir" -s run "$s"
  else
    log "no \"$s\" script in $pnpm_dir; skipping"
  fi
done
