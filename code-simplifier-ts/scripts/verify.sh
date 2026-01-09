#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "[code-simplifier-ts] pnpm not found; install pnpm or run via your package manager" >&2
  exit 1
fi

if [[ ! -f "package.json" ]]; then
  echo "[code-simplifier-ts] package.json not found at repo root; run from your JS project root" >&2
  exit 1
fi

has_script() {
  local script_name="$1"
  node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts['${script_name}'] ? 0 : 1)" \
    >/dev/null 2>&1
}

echo "[code-simplifier-ts] verify: prettier + (optional) lint/typecheck/test"

bash "$SCRIPT_DIR/check.sh"

for s in lint typecheck test; do
  if has_script "$s"; then
    echo "[code-simplifier-ts] pnpm -s run $s"
    pnpm -s run "$s"
  else
    echo "[code-simplifier-ts] no \"$s\" script; skipping"
  fi
done
