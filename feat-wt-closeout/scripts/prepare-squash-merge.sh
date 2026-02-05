#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  prepare-squash-merge.sh <slug>

Run from the feature worktree (feat/{slug}).

This script:
  - Reads .feat/*-{slug}/requirements.md YAML header to locate base branch
  - Infers base repo root via `git rev-parse --git-common-dir`
  - Checks both working trees are clean
  - Runs squash merge into the base branch (does NOT commit)

After this script:
  - Use the /prompts:commit prompt to create the final (single) commit on the base branch.
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

if [[ -n "$(git -C "${feature_root}" status --porcelain)" ]]; then
  echo "[ERROR] feature worktree 不干净；请先提交或清理未提交更改再进行 squash merge。" >&2
  git -C "${feature_root}" status -sb
  exit 1
fi

notes_dir=""
notes_mode=""

# Prefer new layout: .feat/{YYYYMMDD-HHMM}-{slug}/
if compgen -G ".feat/*-${slug}" >/dev/null; then
  # When multiple matches exist, pick the latest by lexicographic order (timestamp prefix).
  notes_dir="$(ls -d .feat/*-${slug} 2>/dev/null | sort | tail -n 1)"
  notes_mode="feat"
elif [[ -f ".cache/codex/features/${slug}/meta.json" ]]; then
  # Back-compat: legacy layout.
  notes_dir=".cache/codex/features/${slug}"
  notes_mode="cache"
else
  echo "[ERROR] 未找到 feature notes：.feat/*-${slug} 或 .cache/codex/features/${slug}/meta.json" >&2
  echo "       请确认你在对应的 feature worktree 且 slug 正确。" >&2
  exit 1
fi

common_dir="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
if [[ -z "${common_dir}" ]]; then
  common_dir="$(git rev-parse --git-common-dir)"
fi
if [[ "${common_dir}" != /* ]]; then
  common_dir="$(cd "${feature_root}" && cd "${common_dir}" && pwd -P)"
fi

base_repo="$(cd "$(dirname "${common_dir}")" && pwd -P)"
feature_branch="$(git branch --show-current 2>/dev/null || true)"
feature_branch="${feature_branch:-feat/${slug}}"
feature_worktree="${feature_root}"

base_branch=""

if [[ "${notes_mode}" == "feat" ]]; then
  requirements_path="${notes_dir}/requirements.md"
  if [[ ! -f "${requirements_path}" ]]; then
    echo "[ERROR] 未找到 requirements.md：${requirements_path}" >&2
    exit 1
  fi

  base_branch="$(python3 - <<PY
import re
from pathlib import Path

p = Path("${requirements_path}")
lines = p.read_text(encoding="utf-8").splitlines()
if not lines or lines[0].strip() != "---":
    print("")
    raise SystemExit(0)

data = {}
for line in lines[1:]:
    if line.strip() == "---":
        break
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = re.match(r"^([A-Za-z0-9_]+)\\s*:\\s*(.*)$", line)
    if not m:
        continue
    k = m.group(1)
    v = m.group(2).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    data[k] = v

print(data.get("base_branch", ""))
PY
)"

  if [[ -z "${base_branch}" ]]; then
    echo "[ERROR] 未能从 YAML header 解析 base_branch：${requirements_path}" >&2
    echo "       期望 requirements.md 以 '---' 开头，并在 header 中包含 'base_branch:' 字段。" >&2
    exit 1
  fi
else
  meta_path="${notes_dir}/meta.json"
  read_json() {
    local key="$1"
    python3 - <<PY
import json
from pathlib import Path

meta = json.loads(Path("${meta_path}").read_text())
print(meta.get("${key}", ""))
PY
  }

  legacy_base_repo="$(read_json base_repo)"
  legacy_base_branch="$(read_json base_branch)"
  legacy_feature_branch="$(read_json feature_branch)"
  legacy_feature_worktree="$(read_json feature_worktree)"

  if [[ -n "${legacy_base_repo}" ]]; then
    base_repo="${legacy_base_repo}"
  fi
  base_branch="${legacy_base_branch}"
  if [[ -n "${legacy_feature_branch}" ]]; then
    feature_branch="${legacy_feature_branch}"
  fi
  if [[ -n "${legacy_feature_worktree}" ]]; then
    feature_worktree="${legacy_feature_worktree}"
  fi

  if [[ -z "${base_repo}" || -z "${base_branch}" ]]; then
    echo "[ERROR] meta.json 内容不完整；需要至少 base_repo/base_branch。" >&2
    exit 1
  fi
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
echo "[INFO] notes dir: ${notes_dir}"

git -C "${base_repo}" checkout "${base_branch}"

echo "[INFO] Running: git merge --squash ${feature_branch}"
if ! git -C "${base_repo}" merge --squash "${feature_branch}"; then
  echo "[ERROR] squash merge 失败（可能有冲突）。" >&2
  echo "       请在 base repo 内解决冲突后，再继续用 /prompts:commit 生成最终提交。" >&2
  exit 1
fi

echo
echo "[OK] squash merge 已完成（尚未 commit），当前 staged changes 位于 base repo：${base_repo}"
echo
echo "Next (must):"
echo "  1) cd \"${base_repo}\""
echo "  2) 按 /prompts:commit 流程生成最终 commit message 并提交（只观察一次 diff）"
echo
echo "Optional cleanup (after commit):"
echo "  git -C \"${base_repo}\" worktree remove \"${feature_worktree}\""
echo "  git -C \"${base_repo}\" worktree prune"
echo "  git -C \"${base_repo}\" branch -d \"${feature_branch}\""
