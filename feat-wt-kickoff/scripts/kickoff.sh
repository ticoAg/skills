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
  - Initialize local feature notes under: .feat/{YYYYMMDD-HHMM}-{slug}/ (NOT tracked)
  - Auto-archive stale notes (>12h since last modification) to: .feat/_archive/
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

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

# 前置 hook：确保 feat-wt 已安装（首次使用时会自动安装并给出友好提示）。
feat_wt_target="${HOME}/.codex/bin/feat-wt"
if [[ -f "${script_dir}/install_feat_wt.sh" ]]; then
  if [[ -x "${feat_wt_target}" ]]; then
    bash "${script_dir}/install_feat_wt.sh" --quiet || echo "[WARN] feat-wt 安装/更新失败；可稍后手动运行：bash \"${script_dir}/install_feat_wt.sh\"" >&2
  else
    bash "${script_dir}/install_feat_wt.sh" || echo "[WARN] feat-wt 安装失败；可稍后手动运行：bash \"${script_dir}/install_feat_wt.sh\"" >&2
  fi
else
  echo "[WARN] 未找到 install_feat_wt.sh；跳过 feat-wt 安装。" >&2
fi

ensure_feat_ignored_in_info_exclude() {
  # Make .feat ignored immediately (local-only, shared across worktrees).
  local common_dir
  common_dir="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
  if [[ -z "${common_dir}" ]]; then
    common_dir="$(git rev-parse --git-common-dir)"
    if [[ "${common_dir}" != /* ]]; then
      common_dir="$(cd "${repo_root}" && cd "${common_dir}" && pwd -P)"
    fi
  fi

  local exclude_path="${common_dir}/info/exclude"
  mkdir -p "$(dirname "${exclude_path}")"
  touch "${exclude_path}"

  if grep -Eq '^[[:space:]]*\.feat(/|[[:space:]]|$)' "${exclude_path}"; then
    echo "[OK] 已在 .git/info/exclude 忽略 .feat（local-only）。"
    return 0
  fi

  cat >>"${exclude_path}" <<'EOF'

# Local feature notes (not tracked)
.feat/
EOF
  echo "[OK] 已写入 .git/info/exclude：忽略 .feat（local-only，不会进入 git）。"
}

ensure_feat_ignored_in_info_exclude

# Gate: base repo must be clean.
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

feat_root="${repo_root}/.feat"

# Auto-archive stale notes (safe guard: only when .feat is ignored, otherwise we may move tracked files).
if [[ -d "${feat_root}" && -f "${script_dir}/archive_old_notes.py" ]]; then
  if [[ -n "$(git ls-files -- .feat | head -n 1)" ]]; then
    echo "[INFO] 检测到 .feat 下存在 git 跟踪文件；跳过自动归档（避免产生意外变更）。"
  elif ! git check-ignore -q .feat >/dev/null 2>&1; then
    echo "[INFO] .feat 当前未被 ignore；跳过自动归档（避免移动可见文件）。"
  elif command -v python3 >/dev/null 2>&1; then
    python3 "${script_dir}/archive_old_notes.py" --feat-dir "${feat_root}" --threshold-hours 12
  else
    echo "[WARN] 未找到 python3；跳过自动归档（.feat/_archive）。"
  fi
fi

git worktree add "${worktree_dir}" -b "${feature_branch}" "${base_branch}"

notes_ts="$(date '+%Y%m%d-%H%M')"
notes_rel_dir=".feat/${notes_ts}-${slug}"
notes_dir="${repo_root}/${notes_rel_dir}"
mkdir -p "${notes_dir}"

created_at_local="$(date '+%Y-%m-%dT%H:%M:%S%z')"

cat >"${notes_dir}/requirements.md" <<EOF
---
summary: "Feature requirements and validation scope for ${slug}"
doc_type: requirements
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
base_branch: "${base_branch}"
feature_branch: "${feature_branch}"
worktree: "${worktree_dir}"
created_at_local: "${created_at_local}"
---
# Feature Requirements: ${slug}

> 使用与用户需求一致的语言填写本文档内容。

## Status
- Current: v0 (draft)
- Base branch: ${base_branch}
- Feature branch: ${feature_branch}
- Worktree: ${worktree_dir}
- Created (Local): ${created_at_local}

<!-- TODO_SYNC:BEGIN -->
## Workflow TODO（自动同步）
- [ ] Kickoff 已完成（分支/worktree/notes 初始化）
- [ ] vFinal 已确认（requirements.md 存在 \`## vFinal - YYYY-MM-DD\`）
- [ ] Context 已补齐（context.md 无 TODO 且包含 \`path:line\`）
- [ ] Delivery 已补齐（delivery.md 无 TODO）
<!-- TODO_SYNC:END -->

## v0 (draft) - ${created_at_local}

### Goals
- [ ] TODO

### Non-goals
- [ ] TODO

### Acceptance criteria
- [ ] TODO

### Open questions
- [ ] TODO

### Options / trade-offs
- Option A:
- Option B:

### Verification plan
- [ ] Unit tests:
- [ ] Integration tests:
- [ ] Manual steps:

## vFinal - TBD

> 在用户确认后补齐，并标注确认日期/版本差异。
EOF

cat >"${notes_dir}/context.md" <<EOF
---
summary: "Evidence-first context notes for ${slug}"
doc_type: context
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
created_at_local: "${created_at_local}"
---
# Context Notes

> 使用与用户需求一致的语言填写本文档内容。

目标：记录最小但关键的上下文证据（入口、现状、约束、关键定位）。
要求：用 \`path:line\` 锚点，避免把大段日志贴进对话。

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
summary: "Decision log for disagreements and trade-offs (if any)"
doc_type: disagreements
slug: "${slug}"
notes_dir: "${notes_rel_dir}"
created_at_local: "${created_at_local}"
---
# Disagreement Log

> 使用与用户需求一致的语言填写本文档内容。

当前暂无明确分歧。如后续出现方案取舍，将在此记录选项与决策。

## 记录格式（出现分歧时）
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
created_at_local: "${created_at_local}"
---
# Delivery Notes

> 使用与用户需求一致的语言填写本文档内容。

交付时的详细说明（用于复盘、PR 描述、以及合并前自检）。

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

if command -v python3 >/dev/null 2>&1 && [[ -f "${script_dir}/todo_sync.py" ]]; then
  if ! python3 "${script_dir}/todo_sync.py" todo sync --notes-dir "${notes_dir}" --quiet; then
    echo "[WARN] todo_sync 失败；请手动运行：python3 \"${script_dir}/todo_sync.py\" todo sync --notes-dir \"${notes_dir}\"" >&2
  fi
fi

echo "[OK] 已初始化 feature notes：${notes_dir}"

# Convenience: link the notes into the new worktree so you can edit/view them from there too.
feature_root="$(cd "${worktree_dir}" && git rev-parse --show-toplevel)"
echo "[INFO] 本工具默认仅写入 local ignore（.git/info/exclude），不会自动修改仓库 .gitignore。"

mkdir -p "${feature_root}/.feat"
link_path="${feature_root}/${notes_rel_dir}"
if [[ -e "${link_path}" ]]; then
  echo "[INFO] worktree 内已存在 notes 路径，跳过创建链接：${link_path}"
else
  ln -s "${notes_dir}" "${link_path}"
  echo "[OK] 已在 worktree 内创建 notes 链接：${link_path} -> ${notes_dir}"
fi

echo
echo "[OK] worktree 已创建：${worktree_dir}"
echo
echo "Next:"
echo "  1) cd \"${worktree_dir}\""
echo "  2) 做最小上下文探索，并把定位写入：${notes_rel_dir}/context.md（该路径在 base repo 与 worktree 中均可访问）"
echo "  3) 在实现前先写 v0 需求 + 提问；如出现分歧，先写 disagreements 并停下等确认"
