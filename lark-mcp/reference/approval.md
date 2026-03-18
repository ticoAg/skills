# 审批 (Approval)

适用场景：

- 发起审批
- 查询审批详情或列表
- 查询审批人的待办任务
- 同意 / 拒绝 / 转交审批

## 当前项目中的推荐入口

优先使用这些 facade target：

- `approval.approval.get`
- `approval.instance.create`
- `approval.instance.get`
- `approval.instance.query`
- `approval.instance.cancel`
- `approval.task.search`
- `approval.task.query`
- `approval.task.approve`
- `approval.task.reject`
- `approval.task.transfer`

身份建议：

- 大多数审批能力默认更接近 `tenant`
- 若 `help` 显示为 `dual`，仍先按业务语义判断是否需要“代表当前用户”执行

## 关键注意事项

1. 飞书不会通过 API 列出所有审批定义，`approval_code` 往往需要业务侧预先提供，或由管理员从审批后台获取。
2. 审批实例的 `form` 不是普通对象，通常要按接口要求传 JSON 字符串。
3. 真正执行同意 / 拒绝 / 转交前，先拿到 `task_id`。
4. 撤回审批是否成功，受审批定义本身的配置影响，不是 API 参数问题。

## 获取 approval_code

常见方式：

1. 飞书审批管理后台进入开发者模式
2. 打开目标审批定义的编辑页
3. 从地址栏拿 `definitionCode=...`

如果上下文里没有现成 `approval_code`，不要在 agent 侧硬猜。

## 典型工作流

### 发起审批

1. `approval.approval.get`
   目的：确认表单控件结构和字段 ID。
2. `approval.instance.create`
   目的：按表单结构发起实例。
3. `approval.instance.get`
   目的：回查状态、任务列表、时间线。

### 处理待办审批

1. `approval.task.search` 或 `approval.task.query`
   目的：拿到待办任务和 `task_id`。
2. `approval.task.approve` / `approval.task.reject` / `approval.task.transfer`
   目的：执行审批动作。

## 高频字段

### `approval.instance.create`

- `data.approval_code`
- `data.open_id`
- `data.form`
- `data.department_id`

### `approval.task.search`

- `data.user_id`
- `data.approval_code`
- `data.task_status`
- `params.user_id_type`

### `approval.task.approve` / `reject` / `transfer`

- `data.approval_code`
- `data.instance_code`
- `data.user_id`
- `data.task_id`
- `data.comment`
- `data.transfer_user_id`，仅转交时需要

## 常见表单控件类型

| 控件类型 | 说明 | value 典型格式 |
| --- | --- | --- |
| `input` | 单行文本 | `"文本"` |
| `textarea` | 多行文本 | `"文本"` |
| `number` | 数字 | `123.45` |
| `date` | 日期时间 | `"2026-03-01T09:00:00+08:00"` |
| `radioV2` | 单选 | `"选项名称"` |
| `checkboxV2` | 多选 | `["选项1", "选项2"]` |
| `attachmentV2` | 附件 | `["file_token"]` |

## 常见状态与错误

### 审批实例状态

- `PENDING`
- `APPROVED`
- `REJECTED`
- `CANCELED`

### 查询列表时常见状态值

- `PENDING`
- `APPROVED`
- `REJECT`
- `RECALL`
- `ALL`

## Common Mistakes

- 想通过 API 列出全部审批定义：通常做不到，先拿 `approval_code`。
- 直接传对象给 `form`：多数情况下需要字符串化。
- 未获取 `task_id` 就执行 approve/reject/transfer：会失败。
- 把实例查询状态和值混用：`REJECT` 和 `REJECTED` 出现位置不同，按接口字段要求传。
