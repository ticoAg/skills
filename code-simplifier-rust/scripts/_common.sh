#!/usr/bin/env bash

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

log() {
  echo "[code-simplifier-rust] $*"
}

die() {
  echo "[code-simplifier-rust] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  format.sh [--manifest <path> | --dir <dir>]
  check.sh  [--manifest <path> | --dir <dir>] [--all-features] [--deny-warnings]
  verify.sh [--manifest <path> | --dir <dir>] [--all-features]
USAGE
}

find_manifest() {
  local manifest_override=""
  local dir_override=""
  local paths=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --manifest)
        shift
        manifest_override="${1:-}"
        ;;
      --dir)
        shift
        dir_override="${1:-}"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      --)
        shift
        paths+=("$@")
        break
        ;;
      *)
        paths+=("$1")
        ;;
    esac
    shift
  done

  if [[ -n "${CODEX_CARGO_MANIFEST:-}" ]]; then
    echo "$CODEX_CARGO_MANIFEST"
    return 0
  fi

  if [[ -n "$manifest_override" ]]; then
    echo "$manifest_override"
    return 0
  fi

  if [[ -n "$dir_override" ]]; then
    echo "$dir_override/Cargo.toml"
    return 0
  fi

  if [[ -f "$ROOT/Cargo.toml" ]]; then
    echo "$ROOT/Cargo.toml"
    return 0
  fi

  if [[ ${#paths[@]} -gt 0 ]]; then
    local dir
    dir="$(cd "$(dirname "${paths[0]}")" && pwd -P)"
    while [[ "$dir" != "/" && "$dir" != "." ]]; do
      if [[ -f "$dir/Cargo.toml" ]]; then
        echo "$dir/Cargo.toml"
        return 0
      fi
      dir="$(dirname "$dir")"
    done
  fi

  local found
  found="$(find "$ROOT" -name Cargo.toml -not -path "*/target/*" -not -path "*/.git/*" -print -quit)"
  if [[ -n "$found" ]]; then
    echo "$found"
    return 0
  fi

  die "Cargo.toml not found; pass --manifest/--dir or set CODEX_CARGO_MANIFEST"
}
