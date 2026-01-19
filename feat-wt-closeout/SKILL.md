---
name: feat-wt-closeout
description: 完成一个基于 git worktree 的 feature：补齐 .feat/{YYYYMMDD-HHMM}-{slug}/ 交付说明并确认需求 vFinal，把 feat/{slug} 用 squash merge 合回原 base 分支，并按 git-auto-commit 流程生成最终单一提交，最后清理 worktree（兼容旧版 .cache/codex/features/{slug}/ 结构）。
---

# Feature Worktree Closeout

## 目标

- 把当前 `feat/{slug}` 的所有变更（含 `.feat/{YYYYMMDD-HHMM}-{slug}/` 沉淀文档）以 1 个 squash commit 合回 kickoff 时的 base 分支。
- 交付同时产出：详细交付文档路径 + 面向终版需求的简要实现概括。

## 前置检查（必须）

- feature worktree 上无未提交更改：`git status -sb` 干净
- `.feat/{YYYYMMDD-HHMM}-{slug}/` 在 git 里可见（非 ignored，且会被合并回 base 分支）
- 已运行最小验证（测试/构建/手动步骤），并记录在 `delivery.md`

## 收尾步骤

### 1. 更新研发沉淀（必须）

- `requirements.md`：补齐 `vFinal`（或把 v0 升级为 vFinal）并标注确认日期
- `delivery.md`：写清“做了什么 / 为何 / 影响 / 如何验证 / 风险”
- `context.md`：补齐关键实现点的 `path:line`

### 2. 确保 feature 分支包含这些沉淀文件（否则 squash 合并不到）

- `git add -A` 后确认 `.feat/{YYYYMMDD-HHMM}-{slug}/` 都被纳入
- 避免只存在于工作区未提交（untracked/ignored）的情况

### 3. squash merge 回 base 分支（推荐用脚本）

在 feature worktree 执行：

```bash
bash ~/.codex/skills/feat-wt-closeout/scripts/prepare-squash-merge.sh {slug}
```

脚本会：

- 读取 `.feat/*-{slug}/requirements.md` 的 YAML header 来获取 `base_branch`
- 通过 `git rev-parse --git-common-dir` 反查 base repo 根目录
- 在 base repo 执行：

- `git checkout <base-branch>`
- `git merge --squash feat/{slug}`

注意：脚本不会自动 commit（为了强制走 `git-auto-commit` 的 message 生成流程）。

（可选）你也可以用脚本读取本任务沉淀文档的 YAML header（输出带文件路径，Markdown 列表，默认隐藏重复字段如 slug/notes_dir）：

```bash
python3 ~/.codex/skills/feat-wt-closeout/scripts/read-notes-headers.py {slug}
```

### 4. 用 git-auto-commit 生成最终提交（必须）

按 `git-auto-commit` skill 流程执行（重点约束：只观察一次 diff）：

- 观察：`bash ~/.codex/skills/git-auto-commit/scripts/observe_changes.sh`
- 生成并提交：`printf '%s\n' "$COMMIT_MSG" | bash ~/.codex/skills/git-auto-commit/scripts/commit.sh`

期望结果：base 分支上最终只有 1 个 squash commit（无 merge commit）。

### 5. 清理 worktree（建议确认后做）

- `git worktree remove ../{repo}-feat-{slug}`
- `git worktree prune`
- （可选）删分支：`git branch -d feat/{slug}`

## 对用户的最终输出格式（必须）

- 详细交付文档路径：`.feat/{YYYYMMDD-HHMM}-{slug}/delivery.md`
- 简要概括：用 5-10 行说明“已实现终版需求哪些点 / 已知限制与风险 / 如何验证”
