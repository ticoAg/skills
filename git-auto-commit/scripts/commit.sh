#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: current directory is not inside a git repository" >&2
  exit 2
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

msg_file="$tmp_dir/commit-msg.txt"
cat >"$msg_file"

if [[ ! -s "$msg_file" ]]; then
  echo "Error: commit message is empty" >&2
  exit 2
fi

git add -A

if git diff --cached --quiet; then
  echo "No staged changes: nothing to commit" >&2
  exit 0
fi

git commit -F "$msg_file"
