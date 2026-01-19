---
name: feature-worktree-kickoff
description: 使用 git worktree 启动一个 feature：澄清需求，创建 feat/{slug} 分支 + 同级 worktree，初始化并跟踪 .cache/codex/features/{slug}/ 研发沉淀目录（需求/上下文/分歧/交付文档），并做最小化的 repo 上下文探索后再进入实现。
---

# Feature Worktree Kickoff

## 目标

- 在不污染主工作区的前提下启动一次 feature 开发：分支 + worktree + 可追溯的研发沉淀（会被合并回原分支）。
- 在写代码前完成：初版需求对齐 + 关键分歧显式化 + 最小上下文探索（入口/现状/约束）。

## 约定（必须）

- 分支名：`feat/{slug}`（slug 用短横线小写，如 `oauth-login`）
- worktree 路径：`../{repo}-feat-{slug}`（与 base repo 同级目录）
- 研发沉淀目录（需要纳入 git 版本控制，最终会随 squash merge 合回 base 分支）：
  - `.cache/codex/features/{slug}/`
  - 文件清单：`meta.json` / `requirements.md` / `context.md` / `disagreements.md` / `delivery.md`

## 快速开始（推荐用脚本）

在 base repo 根目录执行：

```bash
bash ~/.codex/skills/feature-worktree-kickoff/scripts/kickoff.sh <slug>
```

脚本会：

- 校验 base repo 干净、记录 base branch
- 创建 worktree + `feat/{slug}` 分支
- 在新 worktree 初始化 `.cache/codex/features/{slug}/` 文档骨架
- 如遇到 `.cache` 被 gitignore：在当前 `feat/{slug}` 分支追加一个最小“反忽略”块，确保该目录可被提交（从而能合并回 base 分支）

## 工作流（Kickoff 阶段）

### 1) 需求澄清：先写 v0，再提问，等用户确认

- 在 `.cache/.../requirements.md` 写 `v0 (draft)`：目标 / 非目标 / 验收标准 / 风险与选项 / 验证计划
- 把不确定点写成具体问题发给用户确认
- 若存在分歧：写入 `disagreements.md`，并提供 2 个选项 + trade-off（然后停下等用户选）
- 只有在用户确认 `vFinal`（写回 `requirements.md`）后再开始实现

### 2) 最小上下文探索（Evidence First）

- 用 `rg` / 目录结构 / 现有测试定位：入口、现有行为、相关模块边界
- 把关键定位沉淀到 `context.md`，用 `path:line` 锚点；不要把大段日志塞进对话

### 3) Kickoff 阶段输出给用户（必须）

- 给出 2 个路径：
  - 需求文档：`.cache/codex/features/{slug}/requirements.md`
  - 上下文定位：`.cache/codex/features/{slug}/context.md`
- 附一段简短“我理解的 v0 需求”摘要 + 明确待确认问题列表（可编号，便于用户逐条回复）

## 常见坑

- `.cache` 被忽略导致文档无法提交：先 `git check-ignore -v <path>`，再用脚本自动写入 `.gitignore` 反忽略块
- base repo 未 clean 就建 worktree：先处理未提交更改，避免把脏状态带入 feature
