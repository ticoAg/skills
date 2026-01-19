#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

ensure_ruff
collect_targets "$@"

log "verify: lint + compile + (optional) tests"

bash "$SCRIPT_DIR/check.sh" "$@"

if [[ "${TARGETS[0]}" == "." ]]; then
  log "python -m compileall ."
  python -m compileall .
else
  log "python -m compileall (file list)"
  python -m compileall "${TARGETS[@]}"
fi

if [[ -d "tests" || -d "test" ]]; then
  if python -c "import pytest" >/dev/null 2>&1; then
    log "python -m pytest"
    python -m pytest
  else
    log "pytest not available; skipping tests"
  fi
else
  log "no tests/ directory found; skipping tests"
fi
