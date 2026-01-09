#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

FEATURE_ARGS=()
if [[ "${ALL_FEATURES:-}" == "1" || "${1:-}" == "--all-features" ]]; then
  FEATURE_ARGS=(--all-features)
fi

CLIPPY_ARGS=(--all-targets "${FEATURE_ARGS[@]}")
RUSTC_ARGS=()
if [[ "${DENY_WARNINGS:-}" == "1" || "${1:-}" == "--deny-warnings" || "${2:-}" == "--deny-warnings" ]]; then
  RUSTC_ARGS=(-D warnings)
fi

echo "[code-simplifier-rust] cargo clippy ${CLIPPY_ARGS[*]} ${RUSTC_ARGS[*]:-}"
if [[ ${#RUSTC_ARGS[@]} -gt 0 ]]; then
  cargo clippy "${CLIPPY_ARGS[@]}" -- "${RUSTC_ARGS[@]}"
else
  cargo clippy "${CLIPPY_ARGS[@]}"
fi

