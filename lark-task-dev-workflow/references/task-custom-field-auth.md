# `task:custom_field:*` 授权经验模块

只在以下情况读取本文件：

- `scripts/check_task_status_readiness.py` 明确报缺 `task:custom_field:read`
- `scripts/check_task_status_readiness.py` 明确报缺 `task:custom_field:write`
- 飞书后台已经显示权限已开启，但 `lark-cli` 当前 token 仍然拿不到这两个 scope

## 经验结论

- 如对授权流程、身份类型或 `lark-cli auth` 行为本身不确定，先看官方 `lark-shared` skill，再继续本文件。
- 先把 `lark-cli auth status` 和 `lark-cli auth check --scope ...` 当作唯一可信的 token 事实来源。
- 不要只看飞书后台配置页，也不要只看 `lark-cli auth login` 输出里的“全部权限”摘要。
- 实践里，默认的 `lark-cli auth login` 可能不会把新开的 Task 自定义字段权限自动带进本次授权请求。

## 标准排查顺序

1. 看应用是否支持这些 scope：

```bash
lark-cli auth scopes | rg 'task:custom_field'
```

2. 看当前 token 是否真的拿到这些 scope：

```bash
lark-cli auth check --scope "task:custom_field:read task:custom_field:write"
```

3. 如果第 1 步能看到 scope，但第 2 步失败，优先用显式最小 scope 重新登录：

```bash
lark-cli auth login --scope "task:custom_field:read task:custom_field:write task:task:read task:task:write task:tasklist:read task:tasklist:write task:comment:write"
```

4. 登录成功后再次确认：

```bash
lark-cli auth check --scope "task:custom_field:read task:custom_field:write"
```

## 经验解释

- 这通常不是飞书开放平台没有开权限，也不是 `lark-cli api` 不支持对应接口。
- 更常见的情况是：应用侧 scope 已可用，但当前 token 的本次授权请求没有包含这些新增 scope。
- 一旦显式 `--scope` 登录成功，Task Custom Field 相关 OpenAPI 就可以正常使用。

## 恢复完成的验收信号

满足以下两条即可判定 auth 问题已解除：

1. `lark-cli auth check --scope "task:custom_field:read task:custom_field:write"` 返回 `ok: true`
2. `python3 <skill-dir>/scripts/check_task_status_readiness.py --task-id "<task-guid-short-id-or-applink>"` 静默通过
