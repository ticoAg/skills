#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "[code-simplifier-ts] pnpm not found; install pnpm or run via your package manager" >&2
  exit 1
fi

echo "[code-simplifier-ts] pnpm exec prettier --check ."
pnpm exec prettier --check .

