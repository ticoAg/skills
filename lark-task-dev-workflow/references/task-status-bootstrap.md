# `研发状态` 自动初始化与故障排查

默认情况下，`scripts/check_task_status_readiness.py` 会在预检阶段自动完成以下事情：

- 若清单缺少 `研发状态` 字段，则自动创建
- 若字段缺少必需状态选项，则自动补齐
- 若必需状态选项存在但被隐藏，则自动取消隐藏

目标字段约定始终固定为：

- 字段名：`研发状态`
- 字段类型：`single_select`
- 目标状态：`待开始` / `开发中` / `待测试` / `修复中` / `已完成`

## 仍然会阻塞的情况

以下情况仍然需要人工处理：

1. 当前 `lark-cli` 身份缺少以下任一权限
   - `task:custom_field:read`
   - `task:custom_field:write`
2. 清单里已经存在同名字段 `研发状态`，但类型不是 `single_select`
3. 清单里存在多个同名字段 `研发状态`
4. 任务本身不在任何任务清单里

## 权限修复

如对授权、身份、scope 或 `lark-cli` 用法本身不确定，先回看官方 `lark-*` skills，尤其是 `lark-shared`，不要直接靠试错继续排查。

如预检提示权限不足，先重新授权：

```bash
lark-cli auth login
```

然后确认当前身份对任务自定义字段有足够 scope：

- 至少需要 `task:custom_field:read` 才能读取字段和选项
- 若希望 agent 自动创建/补齐字段与选项，还需要 `task:custom_field:write`

先用下面这条命令核验当前 token，而不是只看飞书后台或“全部权限”摘要：

```bash
lark-cli auth check --scope "task:custom_field:read task:custom_field:write"
```

如果这里仍然失败，说明当前 token 没真正拿到这两个 scope。此时不要在本文件里继续展开，先看 `lark-shared`，再转到 `references/task-custom-field-auth.md` 按专门的 auth 经验模块处理。

修复后重新运行：

```bash
python3 <skill-dir>/scripts/check_task_status_readiness.py --task-id "<task-guid-short-id-or-applink>"
```

## 字段类型错误时的人工修复

如果清单里已有 `研发状态`，但类型不是 `single_select`，当前脚本不会冒险自动替换。请在飞书 UI 中：

1. 删除或重命名错误类型的 `研发状态` 字段
2. 再次运行预检脚本，让 agent 自动创建正确字段

## 手工创建时的目标结构

如果你更想手工创建，也请保持以下结构完全一致：

- 字段名：`研发状态`
- 类型：单选
- 选项：
  - `待开始`
  - `开发中`
  - `待测试`
  - `修复中`
  - `已完成`

创建完成后再次运行预检，脚本会自动校验并补齐缺项。
