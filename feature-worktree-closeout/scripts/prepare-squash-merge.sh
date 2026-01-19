#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  prepare-squash-merge.sh <slug>

Run from the feature worktree (feat/{slug}).

This script:
  - Reads .cache/codex/features/{slug}/meta.json to locate the base repo + base branch
  - Checks both working trees are clean
  - Runs squash merge into the base branch (does NOT commit)

After this script:
  - Use the git-auto-commit skill to create the final (single) commit on the base branch.
EOF
}

slug="${1:-}"
if [[ -z "${slug}" ]]; then
  usage
  exit 2
fi

feature_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[ERROR] 当前目录不是 git repo；请在 feature worktree 内执行。" >&2
  exit 1
}

cd "${feature_root}"

meta_path=".cache/codex/features/${slug}/meta.json"
if [[ ! -f "${meta_path}" ]]; then
  echo "[ERROR] 未找到 meta.json：${meta_path}" >&2
  echo "       请确认你在对应的 feature worktree 且 slug 正确。" >&2
  exit 1
fi

read_json() {
  local key="$1"
  python3 - <<PY
import json
from pathlib import Path

meta = json.loads(Path("${meta_path}").read_text())
print(meta.get("${key}", ""))
PY
}

base_repo="$(read_json base_repo)"
base_branch="$(read_json base_branch)"
feature_branch="$(read_json feature_branch)"
feature_worktree="$(read_json feature_worktree)"

if [[ -z "${base_repo}" || -z "${base_branch}" || -z "${feature_branch}" || -z "${feature_worktree}" ]]; then
  echo "[ERROR] meta.json 内容不完整；需要 base_repo/base_branch/feature_branch/feature_worktree。" >&2
  exit 1
fi

if [[ -n "$(git -C "${feature_root}" status --porcelain)" ]]; then
  echo "[ERROR] feature worktree 不干净；请先提交或清理未提交更改再进行 squash merge。" >&2
  git -C "${feature_root}" status -sb
  exit 1
fi

if [[ -n "$(git -C "${base_repo}" status --porcelain)" ]]; then
  echo "[ERROR] base repo 不干净；请先提交或清理未提交更改再进行 squash merge。" >&2
  git -C "${base_repo}" status -sb
  exit 1
fi

echo "[INFO] base repo: ${base_repo}"
echo "[INFO] base branch: ${base_branch}"
echo "[INFO] feature branch: ${feature_branch}"
echo "[INFO] feature worktree: ${feature_worktree}"

git -C "${base_repo}" checkout "${base_branch}"

echo "[INFO] Running: git merge --squash ${feature_branch}"
if ! git -C "${base_repo}" merge --squash "${feature_branch}"; then
  echo "[ERROR] squash merge 失败（可能有冲突）。" >&2
  echo "       请在 base repo 内解决冲突后，再继续用 git-auto-commit 生成最终提交。" >&2
  exit 1
fi

echo
echo "[OK] squash merge 已完成（尚未 commit），当前 staged changes 位于 base repo：${base_repo}"
echo
echo "Next (must):"
echo "  1) cd \"${base_repo}\""
echo "  2) 按 git-auto-commit skill 流程生成最终 commit message 并提交（只观察一次 diff）"
echo
echo "Optional cleanup (after commit):"
echo "  git -C \"${base_repo}\" worktree remove \"${feature_worktree}\""
echo "  git -C \"${base_repo}\" worktree prune"
echo "  git -C \"${base_repo}\" branch -d \"${feature_branch}\""

