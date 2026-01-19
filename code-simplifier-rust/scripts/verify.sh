#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

MANIFEST="$(find_manifest "$@")"

log "verify: fmt + clippy + tests"

bash "$SCRIPT_DIR/format.sh" --manifest "$MANIFEST"
bash "$SCRIPT_DIR/check.sh" --manifest "$MANIFEST" "$@"

FEATURE_ARGS=(--manifest-path "$MANIFEST")
if [[ "${ALL_FEATURES:-}" == "1" || "$*" == *"--all-features"* ]]; then
  FEATURE_ARGS+=(--all-features)
fi

log "cargo test ${FEATURE_ARGS[*]:-}"
cargo test "${FEATURE_ARGS[@]}"
