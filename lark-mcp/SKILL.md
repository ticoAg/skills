---
name: lark-mcp
description: 集成飞书/Feishu 服务，优先通过命令式 MCP facade 操作文档、知识库、云空间、权限、消息、群组、多维表格、任务清单、任务评论、日历等。当用户提到飞书、Feishu、Lark，或需要在飞书里搜索文档、创建文件夹、发消息、建群、查表格、建任务、建任务清单、评论任务、安排日历时使用。
---

# Lark MCP (命令层)

本 Skill 面向新的命令式飞书 MCP 交互层，而不是直接调用 raw OpenAPI tool。

当前维护仓库：`ticoag/lark`

Development based on / fork source：`whatevertogo/FeiShuSkill`

补充说明：本仓已收口一批来自 `/Users/ticoag/Downloads/skills/feishu` 的飞书参考资料，但筛选标准不是“飞书相关就全收”，而是“是否帮助 agent 理解当前 monorepo 中的飞书接入与使用方式”。因此保留了权限、限制、工作流、字段结构、常见坑等知识，去掉了 NestJS 模块模板、内部 CLI / 插件依赖和不适配本仓默认路径的脚手架。

## 核心规则

### 1. 统一走 4 个工具
- `mcp__lark__ls`：列出当前可用的 command / resource / action
- `mcp__lark__help`：查看某个节点或参数说明
- `mcp__lark__run`：执行命令
- `mcp__lark__explain`：解释错误、权限或身份问题

额外约束：凡是飞书/Lark 官方描述里带 `历史版本（不推荐）/ Deprecated Version (Not Recommended)` 的 API，默认都视为不可用；只有用户或配置显式通过 `--deprecated-tools` 放开的旧版 API，才允许作为特例使用。

### 2. 交互模型
统一使用三段式：
- `command`
- `resource`
- `action`

例如：
- `doc document search`
- `drive folder create`
- `chat message create`
- `perm permission-member transfer-owner`

### 3. 使用顺序
默认遵循：
1. 先 `ls`
2. 再 `help`
3. 再 `run`
4. 出错时用 `explain`

不要上来猜 raw tool 名称。

### 4. 身份优先级
- 需要“创建后当前用户可直接访问”的资源时，优先 `identity: "user"`
- 后台自动化、机器人空间或租户级任务，才考虑 `identity: "tenant"`
- 不确定时，可先用 `identity: "auto"`，并查看 `help` 中的默认身份策略

### 5. Cite 与追溯
执行结果会返回：
- `help_target`
- `raw_tool`
- `docs_url`（若可映射）
- `resource_url` / `resource_tokens`（若执行结果可提取）

后续追问时，优先复用这些 cite 信息，不要重新猜资源标识。

### 6. GitHub Auto Issue 机制
- 当 `help -> run -> explain` 之后仍然失败，且失败更像是 Skill 文档缺口、facade 行为异常、参数映射错误、身份策略缺陷或 cite/示例不一致时，进入 GitHub issue 上报流程。
- 优先按失败面选择层：Skill / reference / 工作流文档问题归到 monorepo 内的 `lark-skill`；facade / schema / raw tool 路由 / 身份策略问题归到 `lark-openapi-mcp`；无法判断时默认归到 `lark-skill`，并在 issue 内写明怀疑的下游层。
- 上报前必须脱敏：不要提交 token、cookie、租户内部链接、完整消息正文、邮箱、手机号、群 ID、文档 token；保留字段结构、资源类型、错误码、`raw_tool`、`help_target`、`docs_url` 和必要的末 4 位片段即可。
- 能自动创建 issue 时，优先用仓库内模板发 GitHub issue；如果自动创建失败，则改为把脱敏后的 issue draft 按模板写入目标仓库并提交。
- 详细触发条件、仓库选择、脱敏清单、issue body 模板与 fallback draft 规范，见 `reference/github-issues.md`。

## 推荐工作流

### 发现能力
```yaml
工具: mcp__lark__ls
参数: {}
```

### 查看某个 command 下有哪些资源
```yaml
工具: mcp__lark__ls
参数:
  target: "doc"
```

### 查看某个 action 的说明
```yaml
工具: mcp__lark__help
参数:
  target: "doc.document.search"
```

### 查看某个参数说明
```yaml
工具: mcp__lark__help
参数:
  target: "doc.document.search"
  field: "data.search_key"
```

### 执行命令
```yaml
工具: mcp__lark__run
参数:
  command: "doc"
  resource: "document"
  action: "search"
  identity: "user"
  args:
    data:
      search_key: "项目"
      count: 10
```

### 错误解释
```yaml
工具: mcp__lark__explain
参数:
  target: "doc.document.search"
  error: "Current user_access_token is invalid or expired"
```

## 典型使用方式速查

### 先选类别

| 类别 | 先看什么 | 适用目标 | 默认身份建议 |
| --- | --- | --- | --- |
| 文档 / 知识库 | `doc` / `wiki` | 搜索、导入、读取文档；搜索 Wiki 节点 | 优先 `user` |
| 云空间 / 权限 | `drive` / `perm` | 创建文件夹、授权、转移所有者 | 优先 `user` |
| 消息 / 群组 | `chat` / `group` | 发消息、建群、查群、查群成员 | 发消息多为 `tenant`，查群或用户相关可先看 `help` |
| 用户 / 通讯录 | `user` | 查用户 ID、查用户详情、按部门列成员、找部门 | 先看 `help`；很多能力是 `user_preferred` 或 `tenant_only` |
| 多维表格 | `base` | 建 Base、建表、查记录、写记录 | 优先 `user` |
| 任务 / 清单 / 评论 | `task` | 建任务、建任务清单、建任务分组、评论任务、删任务 | 优先 `user` |
| 日历 | `calendar` | 建事件、改事件、查忙闲 | 优先 `user` |
| 审批 / 考勤 | `approval` / `attendance` | 发起审批、处理审批、查考勤、查补卡、查考勤组 | 审批/考勤常更偏 `tenant` |

### 文档 / 知识库

**高频动作**

- `doc.document.search`：按关键词搜索文档；适合“找文档/列出我能访问的资料”
- `doc.document.import`：把 Markdown 导成文档；适合“生成周报/会议纪要/方案文档”
- `doc.document.read-content`：读取文档纯文本；适合“提取摘要/继续改写”
- `wiki.node.search`：搜索知识库节点；适合“在 Wiki 找页面或目录”

**高频选项**

- `search_key`：关键词；留空表示尽量广泛搜索
- `count`：一次取多少条；先用 `10`，需要汇总时再到 `20` 或 `50`
- `docs_types`：限制文档类型；常见值 `docx` / `sheet` / `slides` / `bitable` / `file`
- `field`：看参数时常先查 `data.search_key`、`data.count`

**何时这样选**

- 用户说“找某个文档/表格/PPT/知识库页面”时，先 `doc.document.search` 或 `wiki.node.search`
- 用户说“帮我生成一篇飞书文档”时，优先 `doc.document.import`
- 用户已经给了文档 token 或 URL，需要读内容时，用 `doc.document.read-content`

**进一步细节**

- 需要 `docs_types`、分页、按 owner/chat 过滤等细项时，再看 `reference/documents.md`
- 需要 Wiki 节点与实际文档对象的对应关系时，再看 `reference/wiki.md`

### 云空间 / 权限

**高频动作**

- `drive.folder.create`：建文件夹；适合“建项目目录/资料夹”
- `perm.permission-member.grant`：加协作者；适合“给人/群组开查看或编辑权限”
- `perm.permission-member.transfer-owner`：转移所有者；适合“把文档或文件交接给某人”

**高频选项**

- `type`：资源类型；常见值 `docx` / `sheet` / `file` / `wiki` / `bitable`
- `member_type`：授权对象类型；常见值 `openid` / `openchat` / `email`
- `perm`：权限级别；常见值 `view` / `edit` / `full_access`
- `perm_type`：作用范围；常见值 `single_page` / `container`
- `need_notification`：是否通知对方；默认协作场景通常设为 `true`

**何时这样选**

- 用户说“建个资料夹/项目目录”时，用 `drive.folder.create`
- 用户说“给某人编辑权限/给群只读权限”时，用 `perm.permission-member.grant`
- 用户说“把这个文档转给我/转给某负责人”时，用 `perm.permission-member.transfer-owner`

**进一步细节**

- 需要目录 token、父目录限制和文件移动/删除时，再看 `reference/drive.md`
- 需要判断 token 与 `type` 的对应关系、授权对象 ID 类型时，再看 `reference/permissions.md`

### 消息 / 群组

**高频动作**

- `chat.message.create`：发消息；适合发通知、提醒、卡片、富文本
- `group.chat.create`：建群；适合“拉个项目群/讨论组”
- `group.chat.list`：列群；适合“帮我找某个群”
- `group.chat-members.get`：查群成员；适合“确认谁在群里”

**高频选项**

- `receive_id_type`：消息接收对象类型；常见值 `chat_id` / `open_id`
- `msg_type`：消息类型；常见值 `text` / `post` / `interactive` / `image` / `file`
- `content`：必须是 JSON 字符串，不是对象
- `chat_type`：群类型；常见值 `private` / `public`
- `user_id_type`：建群、拉人、查成员时的用户 ID 类型；通常优先 `open_id`

**何时这样选**

- 用户说“发一条通知到某个群/某个人”时，用 `chat.message.create`
- 用户说“建个项目群/拉个讨论组”时，用 `group.chat.create`
- 用户不知道群 ID，只知道群名时，先 `group.chat.list`
- 用户要确认群成员、找负责人时，用 `group.chat-members.get`

**进一步细节**

- 需要复杂富文本、卡片结构、群主/管理员细项时，再看 `reference/messages.md` 和 `reference/groups.md`

### 用户 / 通讯录

**高频动作**

- `user.user.lookup-id`：按邮箱/手机号/其他标识换用户 ID；适合“我要 @ 某人/给某人授权，但只有邮箱或手机号”
- `user.user.get`：查用户详情；适合“确认此人的 open_id / 部门 / employee_id”
- `user.user.find-by-department`：列部门成员；适合“找某部门所有人”
- `user.department.search`：按名字找部门；适合“只有部门名，不知道部门 ID”

**高频选项**

- `user_id_type`：通常优先 `open_id`
- `department_id_type`：部门 ID 类型必须和真实 ID 匹配

**何时这样选**

- 任务评论 `@人`、发消息 `@人`、授权给某人之前，优先先把用户 ID 找准
- 用户只给你一个“市场部 / 产品部”，先找部门，再拉人

**进一步细节**

- 见 `reference/contacts.md`

### 多维表格

**高频动作**

- `base.app.create`：建 Base 应用；适合“新建一个项目表/CRM 表”
- `base.app-table.create`：在 Base 里建表；适合“新建任务表/客户表”
- `base.app-table-record.search`：查记录；适合“筛状态、查负责人、做统计前取数”
- `base.app-table-record.create`：写记录；适合“新增一条任务/客户/工单”
- `base.app-table-record.update`：改记录；适合“更新状态/负责人/截止日期”

**高频选项**

- 字段类型优先看 `ui_type`；常见值 `Text` / `Number` / `SingleSelect` / `DateTime` / `User` / `Checkbox`
- 查询过滤常见 `operator`：`is` / `contains` / `isNotEmpty`
- 过滤 `value` 通常要传数组
- `user_id_type` 通常优先 `open_id`

**何时这样选**

- 用户说“建一个项目管理表/跟踪表”时，先 `base.app.create` 再 `base.app-table.create`
- 用户说“查进行中的记录/统计某状态任务”时，用 `base.app-table-record.search`
- 用户说“新增一条记录/批量录入”时，用 `base.app-table-record.create`
- 用户说“把状态改成已完成/换负责人”时，用 `base.app-table-record.update`

**进一步细节**

- 需要字段类型、过滤器、记录结构细项时，再看 `reference/bitable.md`

### 任务 / 清单 / 评论

**高频动作**

- `task.task.create`：建任务；适合“建待办/指派事项”
- `task.task.patch`：改任务；适合“改标题、描述、截止时间、完成状态”
- `task.task.delete`：删任务；适合清理测试数据或误建任务
- `task.tasklist.create`：建任务清单；适合“建项目清单/测试任务分组”
- `task.task.add-tasklist`：把任务加进清单
- `task.comment.create`：评论任务；适合“补充说明/在评论区回复”
- `task.section.create`：在清单里建自定义分组；适合“按阶段/优先级分栏”

**高频选项**

- 任务标题字段通常用 `summary`
- 任务详情字段通常用 `description`
- 评论内容字段用 `content`
- 如需评论区 `@人`，先拿到目标用户的 ID，再传 `mentions`
- 评论对象常用 `resource_type: "task"` 与 `resource_id: "<task_guid>"`
- 清单名称字段用 `name`
- 分组创建时常用 `resource_type: "tasklist"` 或 `resource_type: "my_tasks"`

**何时这样选**

- 用户说“帮我建一个待办/任务”时，用 `task.task.create`
- 用户说“建个任务清单/测试分组”时，先 `task.tasklist.create`
- 用户说“把这个任务放到某个清单里”时，用 `task.task.add-tasklist`
- 用户说“在任务评论区回复/艾特某人”时，用 `task.comment.create`
- 用户说“在清单中按阶段分区”时，用 `task.section.create`

**进一步细节**

- 任务相关资源较多，先用 `ls target="task"` 看资源，再用 `ls target="task.task"`、`task.tasklist`、`task.comment` 缩小范围
- 若任务相关失败看起来是 Skill / facade 缺陷，而不是普通权限或参数问题，再看 `reference/github-issues.md`
- 进入任务域实现细节后，再读 `reference/tasks.md`

### 日历

**高频动作**

- `calendar.calendar-event.create`：建事件；适合会议、提醒、排期
- `calendar.calendar-event.patch`：改事件；适合调整时间、地点、标题
- `calendar.calendar.primary`：取主日历；适合先拿 calendar 标识
- `calendar.freebusy.list`：查忙闲；适合安排会议前看空闲时间

**高频选项**

- `summary`：事件标题
- `start_time` / `end_time`：时间范围
- 需要安排会议前先查忙闲时，优先 `freebusy.list`

**何时这样选**

- 用户说“约个会/建个日程”时，用 `calendar.calendar-event.create`
- 用户说“帮我改时间/延期”时，用 `calendar.calendar-event.patch`
- 用户说“看某人这段时间是否有空”时，用 `calendar.freebusy.list`

**进一步细节**

- 需要会议室搜索、参与人、主日历、时间戳格式时，再看 `reference/calendar.md`

### 审批 / 考勤

**高频动作**

- `approval.instance.create`：发起审批
- `approval.task.search` / `approval.task.query`：查审批待办
- `approval.task.approve` / `reject` / `transfer`：处理审批
- `attendance.user-task.query`：查考勤
- `attendance.user-task-remedy.query`：查补卡
- `attendance.group.get`：查考勤组

**高频选项**

- 审批常需要业务方给出 `approval_code`
- 考勤常需要 `employee_id`

**何时这样选**

- 只要出现审批流或待办处理，先去 `approval`
- 只要出现打卡、迟到、补卡、考勤组，先去 `attendance`

**进一步细节**

- 见 `reference/approval.md` 和 `reference/attendance.md`

### 高级补充

以下内容不是当前仓默认的 MCP facade 使用主路径，但在理解飞书接入时有帮助：

- `reference/oauth.md`
- `reference/events.md`

适用：

- 用户明确在问 user OAuth 授权
- 用户明确在问长连接事件、卡片点击回调、交互卡片更新

## 常用判断模板

### 用户只描述目标时

- “找文档 / 找知识库页面” -> `doc` / `wiki`
- “建文件夹 / 给权限 / 转所有者” -> `drive` / `perm`
- “发通知 / 拉群 / 查群成员” -> `chat` / `group`
- “建表 / 查表 / 写表” -> `base`
- “建任务 / 建任务清单 / 评论任务” -> `task`
- “建日程 / 查忙闲” -> `calendar`

### 先问 help 还是直接 run

- 不确定字段名、枚举值、身份策略 -> 先 `help`
- 用户已经给出清晰目标和必要 ID -> 可直接 `run`
- 用户只给模糊目标 -> 先 `ls` 再 `help`

### 常用身份决策

- 文档、文件夹、Base、任务、日历这类“用户创建后还要继续使用”的资源 -> 优先 `identity: "user"`
- 机器人通知、群消息广播 -> 通常 `identity: "tenant"`
- 不确定时 -> 先看 `help` 的默认身份，再决定

## 常见模式

### 搜索文档
```yaml
command: "doc"
resource: "document"
action: "search"
identity: "user"
args:
  data:
    search_key: "Q4"
    count: 10
```

### 导入 Markdown 文档
```yaml
command: "doc"
resource: "document"
action: "import"
identity: "user"
args:
  data:
    file_name: "项目说明.md"
    markdown: "# 项目说明"
```

### 创建文件夹
```yaml
command: "drive"
resource: "folder"
action: "create"
identity: "user"
args:
  data:
    name: "lark-bot"
```

### 发送群消息
```yaml
command: "chat"
resource: "message"
action: "create"
identity: "tenant"
args:
  params:
    receive_id_type: "chat_id"
  data:
    receive_id: "oc_xxxxx"
    msg_type: "text"
    content: '{"text":"你好"}'
```

### 转移文档所有者
```yaml
command: "perm"
resource: "permission-member"
action: "transfer-owner"
identity: "user"
args:
  path:
    token: "doc_token"
  params:
    type: "docx"
  data:
    member_type: "openid"
    member_id: "ou_xxxxx"
```

### 创建任务
```yaml
command: "task"
resource: "task"
action: "create"
identity: "user"
args:
  data:
    summary: "整理命令层迁移说明"
    description: "补 README、Skill 与迁移文档"
```

### 创建日历事件
```yaml
command: "calendar"
resource: "calendar-event"
action: "create"
identity: "user"
args:
  data:
    summary: "命令层评审"
    start_time:
      timestamp: "1762400400"
    end_time:
      timestamp: "1762404000"
```

## 行为准则

- 若用户只描述目标，不知道 command/resource/action，先用 `ls` / `help` 缩小范围。
- 若结果里已经给出 `help_target`，下一步直接复用，不要重新猜。
- 若用户要“看说明/参数/怎么用”，优先 `help`，不要直接执行。
- 若出现权限、token、scope、身份问题，优先 `explain`，再决定是否重试。
- 若任务会创建用户希望长期使用的资源，优先 `identity: "user"`。

## Legacy 说明

仓库中仍保留 raw OpenAPI 参考文档和旧示例，供内部映射和排查时使用；但默认面对用户时，不再直接暴露 raw tool 名称或要求用户理解 `path/params/data/useUAT` 的 raw 心智。
