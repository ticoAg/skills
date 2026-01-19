#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

MANIFEST="$(find_manifest "$@")"

CLIPPY_ARGS=(--all-targets --manifest-path "$MANIFEST")
if [[ "${ALL_FEATURES:-}" == "1" || "$*" == *"--all-features"* ]]; then
  CLIPPY_ARGS+=(--all-features)
fi
RUSTC_ARGS=()
if [[ "${DENY_WARNINGS:-}" == "1" || "$*" == *"--deny-warnings"* ]]; then
  RUSTC_ARGS=(-D warnings)
fi

log "cargo clippy ${CLIPPY_ARGS[*]} ${RUSTC_ARGS[*]:-}"
if [[ ${#RUSTC_ARGS[@]} -gt 0 ]]; then
  cargo clippy "${CLIPPY_ARGS[@]}" -- "${RUSTC_ARGS[@]}"
else
  cargo clippy "${CLIPPY_ARGS[@]}"
fi
