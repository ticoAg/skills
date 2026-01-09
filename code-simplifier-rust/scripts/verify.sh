#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "[code-simplifier-rust] verify: fmt + clippy + tests"

bash "$SCRIPT_DIR/format.sh"
bash "$SCRIPT_DIR/check.sh" "${@:-}"

FEATURE_ARGS=()
if [[ "${ALL_FEATURES:-}" == "1" || "${1:-}" == "--all-features" ]]; then
  FEATURE_ARGS=(--all-features)
fi

echo "[code-simplifier-rust] cargo test ${FEATURE_ARGS[*]:-}"
cargo test "${FEATURE_ARGS[@]}"

