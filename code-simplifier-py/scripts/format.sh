#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

ensure_ruff
collect_targets "$@"

RUFF="$(ruff_cmd)"

if [[ "${TARGETS[0]}" == "." ]]; then
  log "ruff format ."
  $RUFF format .
else
  log "ruff format (file list)"
  $RUFF format "${TARGETS[@]}"
fi
