#!/usr/bin/env bash

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

log() {
  echo "[code-simplifier-ts] $*"
}

die() {
  echo "[code-simplifier-ts] $*" >&2
  exit 1
}

ensure_pnpm() {
  if ! command -v pnpm >/dev/null 2>&1; then
    die "pnpm not found; install pnpm or run via your package manager"
  fi
}

usage() {
  cat <<'USAGE'
Usage:
  format.sh [--all] [--dir <pnpm-dir>] [<paths...>]
  check.sh  [--all] [--dir <pnpm-dir>] [<paths...>]
  verify.sh [--all] [--dir <pnpm-dir>] [<paths...>]
USAGE
}

collect_targets() {
  local all=0
  local pnpm_dir_override=""
  TARGETS=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --all) all=1 ;;
      --dir)
        shift
        pnpm_dir_override="${1:-}"
        ;;
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

  if [[ -n "$pnpm_dir_override" ]]; then
    CODEX_PNPM_DIR="$pnpm_dir_override"
  fi

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

find_pnpm_dir() {
  local hint="${1:-}"

  if [[ -n "${CODEX_PNPM_DIR:-}" ]]; then
    echo "$CODEX_PNPM_DIR"
    return 0
  fi

  if [[ -f "$ROOT/package.json" ]]; then
    echo "$ROOT"
    return 0
  fi

  if [[ -n "$hint" && "$hint" != "." ]]; then
    local dir
    dir="$(cd "$(dirname "$hint")" && pwd -P)"
    while [[ "$dir" != "/" && "$dir" != "." ]]; do
      if [[ -f "$dir/package.json" ]]; then
        echo "$dir"
        return 0
      fi
      dir="$(dirname "$dir")"
    done
  fi

  local found
  found="$(find "$ROOT" -name package.json -not -path "*/node_modules/*" -not -path "*/.git/*" -print -quit)"
  if [[ -n "$found" ]]; then
    dirname "$found"
    return 0
  fi

  return 1
}

run_prettier() {
  local action="$1"
  local pnpm_dir

  pnpm_dir="$(find_pnpm_dir "${TARGETS[0]}")" || die "no package.json found; set CODEX_PNPM_DIR or pass --dir"

  if [[ "${TARGETS[0]}" == "." ]]; then
    log "pnpm --dir \"$pnpm_dir\" exec prettier $action --ignore-unknown ."
    pnpm --dir "$pnpm_dir" exec prettier "$action" --ignore-unknown .
    return 0
  fi

  log "pnpm --dir \"$pnpm_dir\" exec prettier $action --ignore-unknown (file list)"
  printf '%s\0' "${TARGETS[@]}" | xargs -0 -n 200 pnpm --dir "$pnpm_dir" exec prettier "$action" --ignore-unknown
}
