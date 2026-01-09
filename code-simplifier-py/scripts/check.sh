#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

ruff_cmd() {
  if command -v ruff >/dev/null 2>&1; then
    echo "ruff"
    return 0
  fi
  echo "python -m ruff"
}

RUFF="$(ruff_cmd)"

FIX_ARGS=()
if [[ "${1:-}" == "--fix" ]]; then
  FIX_ARGS=(--fix)
fi

echo "[code-simplifier-py] ruff check ${FIX_ARGS[*]:-}"
$RUFF check . "${FIX_ARGS[@]}"

