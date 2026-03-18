# 任务 / 清单 / 评论指南

## 适用范围

在以下场景下读取本文件：

- 创建任务、更新任务、删除任务
- 创建任务清单或自定义分组
- 把任务加入清单
- 在任务评论区回复、评论、@某人

如果只是判断“该走 `task` 还是别的 command”，先看 `SKILL.md` 主体；只有进入任务域实现细节时再读这里。

## 核心结论

### 1. 任务主路径默认走 v2

优先使用：

- `task.task.create`
- `task.task.patch`
- `task.task.delete`
- `task.task.add-tasklist`
- `task.tasklist.create`
- `task.section.create`
- `task.comment.create`

除非明确需要旧版兼容行为，否则不要主动选择 `task.task-comment.*` 这类 legacy 资源。

### 2. 任务评论 @ 人要先拿到用户 ID

要在任务评论区真正 @ 某人，必须先拿到该人的用户 ID，并与 `params.user_id_type` 保持一致。

推荐顺序：

1. 优先使用现成的 `open_id`
2. 如果上下文里只有姓名、邮箱、手机号，再先查用户 ID
3. 再调用 `task.comment.create`

常见情况：

- 已有 `open_id` -> 直接发评论
- 只有人名 -> 先查 ID，再发评论
- 不知道该用哪种 ID -> 统一优先 `open_id`

### 3. v2 评论中的 @ 语法

当前推荐的 v2 评论 mention 写法是：

```yaml
command: "task"
resource: "comment"
action: "create"
identity: "user"
args:
  params:
    user_id_type: "open_id"
  mentions:
    - user_id: "ou_xxxxx"
      user_id_type: "open_id"
  data:
    content: "请查看这个任务"
    resource_type: "task"
    resource_id: "<task_guid>"
```

facade 会把它转换成：

```text
<at id=ou_xxxxx></at> 请查看这个任务
```

再提交给 `task.v2.comment.create`。

### 4. 不要把评论内容写成对象式富文本

对于 `task.v2.comment.create`：

- `content` 应保持字符串
- 不要传 `{ text, elements }` 这种对象结构

已验证：

- `<at id=open_id></at>` 放在字符串里可以工作
- `<at user_id=\"...\">...</at>` 不可靠
- 对象式富文本 `content` 会被接口拒绝

## 高频动作与选择说明

### 创建任务

适用：

- “建一个待办”
- “指派一个任务”
- “生成测试任务”

用法：

```yaml
command: "task"
resource: "task"
action: "create"
identity: "user"
args:
  data:
    summary: "整理发布说明"
    description: "补 changelog 与验证记录"
```

高频字段：

- `summary`：任务标题
- `description`：任务说明
- `tasklists`：创建时直接加入清单时使用

### 更新任务

适用：

- 改标题
- 改描述
- 改截止时间
- 标记完成 / 恢复未完成

用法：

```yaml
command: "task"
resource: "task"
action: "patch"
identity: "user"
args:
  path:
    task_guid: "<task_guid>"
  data:
    task:
      summary: "新的标题"
    update_fields:
      - "summary"
```

### 删除任务

适用：

- 清理测试数据
- 删除误建任务

用法：

```yaml
command: "task"
resource: "task"
action: "delete"
identity: "user"
args:
  path:
    task_guid: "<task_guid>"
```

### 创建任务清单

适用：

- 建项目任务组
- 建测试清单
- 按项目管理多个任务

用法：

```yaml
command: "task"
resource: "tasklist"
action: "create"
identity: "user"
args:
  data:
    name: "Codex MCP 测试任务组"
```

高频字段：

- `name`：清单名称
- `members`：协作成员（可选）

### 创建清单内分组

适用：

- 在清单中按阶段分栏
- 做“测试任务 / 正式任务 / 已完成”这类区分

用法：

```yaml
command: "task"
resource: "section"
action: "create"
identity: "user"
args:
  data:
    name: "测试任务"
    resource_type: "tasklist"
    resource_id: "<tasklist_guid>"
```

### 把任务加入清单

适用：

- 已创建任务，要归档到某个清单或分组

用法：

```yaml
command: "task"
resource: "task"
action: "add-tasklist"
identity: "user"
args:
  path:
    task_guid: "<task_guid>"
  data:
    tasklist_guid: "<tasklist_guid>"
    section_guid: "<section_guid>"
```

### 在任务评论区 @ 某人

适用：

- “提醒某人处理这个任务”
- “在评论区通知负责人”
- “回复时 @ 某个协作者”

执行规则：

1. 先确认是否已经有该人的 `open_id`
2. 如果没有，先查到 ID
3. 再调用 `task.comment.create`

推荐用法：

```yaml
command: "task"
resource: "comment"
action: "create"
identity: "user"
args:
  params:
    user_id_type: "open_id"
  mentions:
    - user_id: "ou_xxxxx"
      user_id_type: "open_id"
  data:
    content: "请查看这个任务"
    resource_type: "task"
    resource_id: "<task_guid>"
```

## 失败时怎么判断

### 评论创建成功但没有真正 @ 到人

先检查：

1. 是否用了 `mentions`
2. `mentions[].user_id` 是否真的是用户 ID，而不是名字
3. `params.user_id_type` 是否与该 ID 一致
4. 是否仍在手动传 `<at user_id=...>` 或对象式 `content`

### 用户只给了姓名，没有 ID

不要直接发表评论。

先去查 ID，再评论。

### 任务接口里出现 legacy 路径

如果你只是做普通任务管理，不要主动切到 legacy `task.task-comment.*`。

只有在明确需要兼容旧版接口行为，且主路径不满足需求时，才把它当特例处理。
