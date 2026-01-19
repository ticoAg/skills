#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  kickoff.sh <slug> [base-branch]

Example:
  kickoff.sh oauth-login
  kickoff.sh oauth-login main

Behavior:
  - Run in the base repo root.
  - Create a sibling worktree: ../{repo}-feat-{slug}
  - Create branch: feat/{slug} (based on base-branch; default: current branch)
  - Initialize tracked feature notes under: .feat/{YYYYMMDD-HHMM}-{slug}/
EOF
}

slug="${1:-}"
base_branch_arg="${2:-}"

if [[ -z "${slug}" ]]; then
  usage
  exit 2
fi

if [[ ! "${slug}" =~ ^[a-z0-9]+([a-z0-9-]*[a-z0-9])?$ ]]; then
  echo "[ERROR] slug '${slug}' 非法；请使用小写字母/数字/短横线（且不能以短横线结尾）。" >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[ERROR] 当前目录不是 git repo；请在 base repo 根目录执行。" >&2
  exit 1
}

cd "${repo_root}"

base_branch="${base_branch_arg:-$(git branch --show-current)}"
if [[ -z "${base_branch}" ]]; then
  echo "[ERROR] 无法识别 base branch；请显式传入第二个参数 base-branch。" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[ERROR] base repo 不干净；请先提交/暂存/清理未提交更改，再创建 worktree。" >&2
  git status -sb
  exit 1
fi

repo_name="$(basename "${repo_root}")"
worktree_dir="../${repo_name}-feat-${slug}"
feature_branch="feat/${slug}"

if [[ -e "${worktree_dir}" ]]; then
  echo "[ERROR] worktree 目录已存在：${worktree_dir}" >&2
  exit 1
fi

echo "[INFO] base repo: ${repo_root}"
echo "[INFO] base branch: ${base_branch}"
echo "[INFO] feature branch: ${feature_branch}"
echo "[INFO] worktree dir: ${worktree_dir}"

git worktree add "${worktree_dir}" -b "${feature_branch}" "${base_branch}"

feature_root="$(cd "${worktree_dir}" && git rev-parse --show-toplevel)"
notes_ts="$(date -u '+%Y%m%d-%H%M')"
notes_rel_dir=".feat/${notes_ts}-${slug}"
notes_dir="${feature_root}/${notes_rel_dir}"
mkdir -p "${notes_dir}"

created_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

cat >"${notes_dir}/requirements.md" <<EOF
---
summary: "Feature requirements and validation scope for ${slug}"
doc_type: requirements
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
base_branch: "${base_branch}"
feature_branch: "${feature_branch}"
worktree: "${worktree_dir}"
created_at_utc: "${created_at}"
---
# Feature Requirements: ${slug}

> 使用与用户需求一致的语言填写本文档内容。

## Status
- Current: v0 (draft)
- Base branch: ${base_branch}
- Feature branch: ${feature_branch}
- Worktree: ${worktree_dir}
- Created (UTC): ${created_at}

## v0 (draft) - ${created_at}

### Goals
- TODO

### Non-goals
- TODO

### Acceptance criteria
- TODO

### Open questions
- TODO

### Options / trade-offs
- Option A:
- Option B:

### Verification plan
- Unit tests:
- Integration tests:
- Manual steps:

## vFinal - TBD

> 在用户确认后补齐，并标注确认日期/版本差异。
EOF

cat >"${notes_dir}/context.md" <<EOF
---
summary: "Evidence-first context notes for ${slug}"
doc_type: context
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
created_at_utc: "${created_at}"
---
# Context Notes

> 使用与用户需求一致的语言填写本文档内容。

目标：记录最小但关键的上下文证据（入口、现状、约束、关键定位）。
要求：用 `path:line` 锚点，避免把大段日志贴进对话。

## Entrypoints
- TODO: path:line - why it matters

## Current behavior
- TODO

## Constraints / assumptions
- TODO

## Related tests / fixtures
- TODO
EOF

cat >"${notes_dir}/disagreements.md" <<EOF
---
summary: "Decision log for disagreements and trade-offs"
doc_type: disagreements
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
created_at_utc: "${created_at}"
---
# Disagreement Log

> 使用与用户需求一致的语言填写本文档内容。

当需求/方案存在分歧时，用这里显式记录，并给出选项与 trade-off（然后停下等用户选择）。

- Topic:
  - Option A:
  - Option B:
  - Decision:
  - Notes:
EOF

cat >"${notes_dir}/delivery.md" <<EOF
---
summary: "Delivery summary, verification, and impact notes"
doc_type: delivery
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
created_at_utc: "${created_at}"
---
# Delivery Notes

> 使用与用户需求一致的语言填写本文档内容。

交付时的详细说明（最终会随 squash merge 合回 base 分支）。

## Changes
- TODO

## Expected outcome
- TODO

## How to verify
- Commands:
- Manual steps:

## Impact / risks
- TODO

## References (path:line)
- TODO
EOF

# Ensure the notes are not ignored. If ignored, append a minimal unignore block
# in the current feature branch so the notes can be committed and squash-merged.
if git -C "${feature_root}" check-ignore -q "${notes_rel_dir}/requirements.md"; then
  gitignore_path="${feature_root}/.gitignore"
  marker_start="# --- Codex feature notes (tracked) ---"
  marker_end="# --- End Codex feature notes ---"

  if [[ ! -f "${gitignore_path}" ]]; then
    : >"${gitignore_path}"
  fi

  if command -v rg >/dev/null 2>&1; then
    has_marker="$(rg -F -q "${marker_start}" "${gitignore_path}" && echo 1 || echo 0)"
  else
    has_marker="$(grep -F -q "${marker_start}" "${gitignore_path}" && echo 1 || echo 0)"
  fi

  if [[ "${has_marker}" != "1" ]]; then
    cat >>"${gitignore_path}" <<EOF

${marker_start}
!.feat/
!.feat/**
${marker_end}
EOF
    echo "[INFO] 已追加 .gitignore 反忽略块：${gitignore_path}"
  fi

  if git -C "${feature_root}" check-ignore -q "${notes_rel_dir}/requirements.md"; then
    echo "[WARN] 仍然被忽略：${notes_rel_dir}/requirements.md"
    echo "       请手动检查 .gitignore / 全局 ignore 规则，确保该目录可被提交。"
  fi
fi

echo
echo "[OK] worktree 已创建：${worktree_dir}"
echo "[OK] feature notes：${notes_dir}"
echo
echo "Next:"
echo "  1) cd \"${worktree_dir}\""
echo "  2) 用 rg/目录结构做最小上下文探索，并把定位写入：${notes_rel_dir}/context.md"
echo "  3) 在实现前先写 v0 需求 + 提问，等用户确认 vFinal"
