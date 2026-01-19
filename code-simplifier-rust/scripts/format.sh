#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_common.sh"

MANIFEST="$(find_manifest "$@")"

log "cargo fmt --manifest-path \"$MANIFEST\""
cargo fmt --manifest-path "$MANIFEST"
