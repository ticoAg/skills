#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

ensure_ruff

FIX_ARGS=()
FILTERED_ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--fix" ]]; then
    FIX_ARGS=(--fix)
  else
    FILTERED_ARGS+=("$arg")
  fi
done

collect_targets "${FILTERED_ARGS[@]}"

RUFF="$(ruff_cmd)"

if [[ "${TARGETS[0]}" == "." ]]; then
  log "ruff check ${FIX_ARGS[*]:-} ."
  $RUFF check . "${FIX_ARGS[@]}"
else
  log "ruff check ${FIX_ARGS[*]:-} (file list)"
  $RUFF check "${TARGETS[@]}" "${FIX_ARGS[@]}"
fi
