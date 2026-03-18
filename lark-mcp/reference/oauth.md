# OAuth 用户授权（高级补充）

本文件是“飞书接入背景知识”，帮助 agent 理解什么时候必须走用户授权，而不是继续用应用身份。

重要说明：

- 这不是当前 `lark-mcp` 默认 facade 的主入口文档
- 当前仓库重点仍是 `ls / help / run / explain` + 命令层 target
- 只有在你明确处理“个人日历 / 代表当前用户调用 / 持久化 user_access_token”这类集成问题时，再读这里

## 什么时候需要 OAuth

默认 `tenant_access_token` 代表应用身份。

以下场景更常需要 `user_access_token`：

- 操作当前用户的个人日历
- 搜索依赖用户上下文的联系人/部门
- 需要“以用户身份”访问而不是“以应用身份”访问的数据

## 授权流程概念

1. 构造授权地址并跳转用户
2. 回调里用 `code` 换取 token
3. 保存 `access_token` / `refresh_token`
4. 调用 API 时带上用户 token

## 对 agent 有帮助的关键结论

1. 如果 `help` / `explain` 提示当前能力更偏 `user_only` 或 `user_preferred`，但上下文又明显没有用户登录态，问题往往不在参数，而在授权前置条件。
2. `refresh_token` 会轮转，不能假设刷新后旧值仍能继续用。
3. 这类问题更像“宿主系统的飞书接入设计”，不是 `lark-skill` 内部文档能单独解决的字段错误。

## 常见排查提示

- “当前用户 token 无效或过期”：优先检查用户登录态和 token 刷新逻辑。
- “tenant 能调、user 不能调”：优先检查用户是否完成 OAuth，而不是先怀疑字段。
- “搜索联系人只能查部分人”：先分辨是 OAuth 问题还是通讯录权限范围问题。
