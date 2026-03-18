# GitHub Auto Issue / 失败上报

## 何时进入这个流程

只有在下面情况才进入 GitHub issue 流程，而不是继续普通重试：

- 已经按默认顺序执行过 `ls` / `help` / `run` / `explain`
- 确认不是简单的参数拼写错误、权限缺失、token 过期、用户未授权
- 失败更像是以下问题：
  - Skill 文档或 reference 缺口
  - facade 暴露的 schema / 示例与真实行为不一致
  - raw tool 路由、identity 策略、cite 返回有缺陷
  - 同一类失败经过一次合理修正后仍稳定复现

## 先选层

优先规则：

- `lark-skill`
  - `SKILL.md`
  - `reference/*.md`
  - 推荐工作流、示例、默认选择规则
- `lark-openapi-mcp`
  - facade `ls/help/run/explain`
  - command / resource / action 暴露
  - schema、handler、identity、cite、raw tool 映射

若一时无法判断，默认归到 `lark-skill`，并在 issue 正文中补一句：

```text
Suspected downstream layer: lark-openapi-mcp
```

## 脱敏规则

必须移除或替换：

- access token / refresh token / cookie / secret / app credential
- 完整飞书文档链接、完整资源 token、群 ID、用户 ID、租户内部 URL
- 邮箱、手机号、真实姓名、消息全文、文档正文、评论全文

建议保留：

- `command.resource.action`
- `raw_tool`
- `help_target`
- `docs_url`
- 错误码、错误摘要、`identity`
- 资源类型、字段名、参数结构
- 必要时只保留 ID 后 4 位，例如 `ou_***9ab2`

## 需要收集的最小信息

至少包含：

1. 行为：用户想做什么，实际发生了什么
2. 期望结果：本来应该成功得到什么
3. 调用工具：按时间顺序列出 `ls/help/run/explain`
4. 失败证据：错误摘要、错误码、cite、`raw_tool`
5. 脱敏说明：哪些字段已经掩码、哪些内容有意省略

## GitHub issue 标题建议

```text
[lark-mcp] <command.resource.action> <failure-summary>
```

例如：

```text
[lark-mcp] task.comment.create mention body converted incorrectly
```

## Issue Body 模板

优先复用 monorepo 根目录里的 GitHub 模板：`../.github/ISSUE_TEMPLATE/lark-mcp-auto-failure.md`

若需要手工拼接，正文结构如下：

```markdown
## Behavior
- User intent:
- Actual behavior:

## Expected Result
- Expected outcome:

## Tool Calls
1. `ls`: ...
2. `help`: ...
3. `run`: ...
4. `explain`: ...

## Evidence
- help_target:
- raw_tool:
- identity:
- docs_url:
- error summary:

## Redaction
- Removed:
- Masked:

## Suspected Layer
- `lark-skill` / `lark-openapi-mcp` / `unknown`
```

## 自动创建 issue 的优先方式

如果环境里有 GitHub CLI 且已登录，优先：

```bash
gh issue create \
  --repo ticoag/lark \
  --title "[lark-mcp] <command.resource.action> <failure-summary>" \
  --body-file <redacted-issue.md>
```

## 自动创建失败时的 fallback

如果自动创建 GitHub issue 失败：

1. 继续保留脱敏后的内容
2. 按模板生成 issue draft
3. 将 draft 写入 monorepo 根目录的 `issue-drafts/` 目录
4. 文件名使用：

```text
issue-drafts/YYYYMMDD-HHMM-<slug>.md
```

例如：

```text
issue-drafts/20260311-0010-task-comment-mention.md
```

5. draft 顶部补充失败原因，例如：

```text
Auto issue creation failed: gh auth missing
```

## 上游来源声明

- `lark-openapi-mcp` fork source: `larksuite/lark-openapi-mcp`
- `lark-skill` development based on / fork source: `whatevertogo/FeiShuSkill`

## 额外约束

- 不要把未经脱敏的原始请求体、原始响应体直接提交到仓库
- 不要把普通权限问题误报成产品缺陷；权限/授权问题优先让 `explain` 给下一步
- 若 issue 只与某个 reference 缺字、示例错误有关，正文里要明确这是“文档问题”，不要写成 API 缺陷
