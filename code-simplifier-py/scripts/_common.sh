#!/usr/bin/env bash

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

log() {
  echo "[code-simplifier-py] $*"
}

die() {
  echo "[code-simplifier-py] $*" >&2
  exit 1
}

ruff_cmd() {
  if command -v ruff >/dev/null 2>&1; then
    echo "ruff"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python -m ruff"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo "python3 -m ruff"
    return 0
  fi
  return 1
}

ensure_ruff() {
  if ! ruff_cmd >/dev/null 2>&1; then
    die "ruff not found; install ruff or add it to your environment"
  fi
}

usage() {
  cat <<'USAGE'
Usage:
  format.sh [--all] [<paths...>]
  check.sh  [--all] [--fix] [<paths...>]
  verify.sh [--all] [<paths...>]
USAGE
}

collect_targets() {
  local all=0
  TARGETS=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --all) all=1 ;;
      -h|--help)
        usage
        exit 0
        ;;
      --)
        shift
        TARGETS+=("$@")
        break
        ;;
      -*)
        die "unknown flag: $1"
        ;;
      *)
        TARGETS+=("$1")
        ;;
    esac
    shift
  done

  if [[ ${#TARGETS[@]} -eq 0 ]]; then
    if [[ "$all" -eq 1 ]]; then
      TARGETS=(".")
    elif git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      mapfile -t TARGETS < <(
        {
          git diff --name-only --diff-filter=ACMR HEAD 2>/dev/null || true
          git diff --name-only --diff-filter=ACMR --cached 2>/dev/null || true
        } | sort -u
      )
      if [[ ${#TARGETS[@]} -eq 0 ]]; then
        mapfile -t TARGETS < <(git ls-files)
      fi
    else
      TARGETS=(".")
    fi
  fi

  if [[ ${#TARGETS[@]} -eq 0 ]]; then
    die "no files found to format/check"
  fi

  if [[ "${TARGETS[0]}" != "." ]]; then
    local filtered=()
    for path in "${TARGETS[@]}"; do
      if [[ -e "$path" ]]; then
        filtered+=("$path")
      fi
    done
    TARGETS=("${filtered[@]}")
  fi

  if [[ ${#TARGETS[@]} -eq 0 ]]; then
    die "no existing files found to format/check"
  fi
}
