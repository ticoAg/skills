---
name: feat-wt-kickoff
description: 使用 git worktree 启动一个 feature：澄清需求，创建 feat/{slug} 分支 + 同级 worktree，初始化并跟踪 .feat/{YYYYMMDD-HHMM}-{slug}/ 研发沉淀目录（需求/上下文/分歧/交付文档，含 YAML metadata 头部，正文语言随用户需求语言），并做最小化的 repo 上下文探索后再进入实现。
---

# Feature Worktree Kickoff

## 目标

- 在不污染主工作区的前提下启动一次 feature 开发：分支 + worktree + 可追溯的研发沉淀（会被合并回原分支）。
- 在写代码前完成：初版需求对齐 + 关键分歧显式化 + 最小上下文探索（入口/现状/约束）。

## 约定(MUST)

- 分支名：`feat/{slug}`（slug 用短横线小写，如 `oauth-login`）
- worktree 路径：`../{repo}-feat-{slug}`（与 base repo 同级目录）
- 研发沉淀目录（需要纳入 git 版本控制，最终会随 squash merge 合回 base 分支）：
  - `.feat/{YYYYMMDD-HHMM}-{slug}/`
  - 文件清单：`requirements.md` / `context.md` / `disagreements.md` / `delivery.md`
  - 每个文档头部必须包含 YAML metadata（字段灵活，模型自判；至少包含能概括该文档的 summary/用途信息）
- 文档正文语言随用户需求语言
- 过程中如有阶段性进展，可随时更新沉淀文档

## 快速开始（推荐用脚本）

在 base repo 根目录执行：

```bash
bash ~/.codex/skills/feat-wt-kickoff/scripts/kickoff.sh <slug>
```

脚本会：

- 校验 base repo 干净、记录 base branch
- 创建 worktree + `feat/{slug}` 分支
- 在新 worktree 初始化 `.feat/{YYYYMMDD-HHMM}-{slug}/` 文档骨架（含 YAML metadata 头部）
- 如遇到 `.feat` 被 gitignore：在当前 `feat/{slug}` 分支追加一个最小“反忽略”块，确保该目录可被提交（从而能合并回 base 分支）

## 工作流（Kickoff 阶段）

### 0. 确认门禁（MUST：出现分歧/选项就立刻停下）

在 Kickoff 过程中，只要出现任何需要用户拍板的点（需求歧义、范围不明、接口/架构选型、兼容性/迁移策略、安全策略、时间/成本权衡等），必须执行以下动作，并**立刻暂停工作流**：

1) 把该分歧写入 `.feat/.../disagreements.md`（至少 2 个选项 + trade-off + 推荐项(可选)）
2) 同步在 `.feat/.../requirements.md` 标注为 `draft` / `pending confirmation`（或在正文显式写 “待确认”）
3) 在对话里把“要确认的输出”发给用户（编号，便于逐条回复）
4) **停止**：不要继续做上下文探索、不要开始实现、不要继续运行命令；等待用户选择/确认后再继续

（核心目标：让工作流在“决策点”形成一个硬暂停，而不是边做边假设。）

对话输出建议用固定模板（便于用户快速回复）：

```text
需要你确认的分歧（请选择 1/2/...）：
1) <分歧点标题>
   - 选项 A：...（优点/缺点/影响）
   - 选项 B：...（优点/缺点/影响）
   - 我的建议：A/B（可选）
请回复：1A / 1B（以及必要的补充约束）。
```

### 1. 需求澄清：先写 v0，再提问，等用户确认

- 在 `.feat/.../requirements.md` 写 `v0 (draft)`：目标 / 非目标 / 验收标准 / 风险与选项 / 验证计划
- 把不确定点写成具体问题发给用户确认
- 若存在分歧：写入 `disagreements.md`，并提供 2 个选项 + trade-off；**触发“确认门禁”，立刻停下等用户选**
- 只有在用户确认 `vFinal`（写回 `requirements.md`）后再开始实现

### 2. 最小上下文探索（Evidence First）

- 用 `rg` / 目录结构 / 现有测试定位：入口、现有行为、相关模块边界
- 把关键定位沉淀到 `context.md`，用 `path:line` 锚点；不要把大段日志塞进对话
- 如果在探索过程中发现需要拍板的取舍（例如：现有实现不满足目标导致需要改接口/做迁移/兼容策略），同样触发“确认门禁”：先写 `disagreements.md` + 输出给用户 + 停下

### 3. Kickoff 阶段输出给用户(MUST)

- 给出 2 个路径：
- 需求文档：`.feat/{YYYYMMDD-HHMM}-{slug}/requirements.md`
- 上下文定位：`.feat/{YYYYMMDD-HHMM}-{slug}/context.md`
- 附一段简短“我理解的 v0 需求”摘要 + 明确待确认问题列表（可编号，便于用户逐条回复）

## 常见坑

- `.feat` 被忽略导致文档无法提交：先 `git check-ignore -v <path>`，再用脚本自动写入 `.gitignore` 反忽略块
- base repo 未 clean 就建 worktree：先处理未提交更改，避免把脏状态带入 feature
