#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "[code-simplifier-py] verify: lint + compile + (optional) tests"

bash "$SCRIPT_DIR/check.sh"

echo "[code-simplifier-py] python -m compileall ."
python -m compileall .

if [[ -d "tests" || -d "test" ]]; then
  if python -c "import pytest" >/dev/null 2>&1; then
    echo "[code-simplifier-py] python -m pytest"
    python -m pytest
  else
    echo "[code-simplifier-py] pytest not available; skipping tests"
  fi
else
  echo "[code-simplifier-py] no tests/ directory found; skipping tests"
fi

