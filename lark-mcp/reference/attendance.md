# 考勤 (Attendance)

适用场景：

- 查询个人或团队考勤
- 查询补卡记录
- 查询考勤组 / 考勤规则

## 当前项目中的推荐入口

优先使用这些 facade target：

- `attendance.user-task.query`
- `attendance.user-task-remedy.query`
- `attendance.group.get`
- `attendance.group.list`
- `attendance.group.search`
- `attendance.group.list-user`
- `user.user.get`
- `user.user.lookup-id`

身份建议：

- 当前仓里大多数考勤相关 target 更偏 `tenant`
- 先用 `help` 看默认身份与字段说明，再决定是否需要补用户 ID 转换

## 关键注意事项

1. 考勤 API 经常需要 `employee_id`，不是 `open_id`。
2. 如果上下文只有 `open_id`，先通过 `user.user.get` 拿用户资料，再确认是否有 `employee_id`。
3. `attendance.user-task.query` 的日期通常是 `yyyyMMdd` 整数，而不是日期字符串。
4. `user_ids` 常见上限是 50，团队查询要分批。
5. 补卡记录的时间范围与打卡结果的日期格式不同，别混用。

## 典型工作流

### 查看个人一周考勤

1. `user.user.get`
2. `attendance.user-task.query`
3. 如需解释规则，再查 `attendance.group.get`

### 查看补卡记录

1. `attendance.user-task-remedy.query`
2. 结合状态码解释审批结果。

### 批量看团队考勤

1. `user.user.find-by-department`
2. 提取标识后分批调用 `attendance.user-task.query`
3. 需要规则时补查 `attendance.group.get`

## 高频字段

### `attendance.user-task.query`

- `params.employee_type`
- `data.user_ids`
- `data.check_date_from`
- `data.check_date_to`

### `attendance.user-task-remedy.query`

- `params.employee_type`
- `data.user_ids`
- `data.check_time_from`
- `data.check_time_to`
- `data.status`

### `attendance.group.get`

- `path.group_id`
- `params.employee_type`

## 常见状态码

### 打卡状态

| 值 | 含义 |
| --- | --- |
| `Normal` | 正常 |
| `Late` | 迟到 |
| `Early` | 早退 |
| `Lack` | 缺卡 |
| `Todo` | 未打卡 |
| `NoNeedCheck` | 无需打卡 |

### 补卡状态

| 值 | 含义 |
| --- | --- |
| `0` | 待审批 |
| `1` | 未通过 |
| `2` | 已通过 |
| `3` | 已取消 |
| `4` | 已撤回 |

## Common Mistakes

- 直接把 `open_id` 拿去调考勤：通常要先确认或转换为 `employee_id`。
- 把 `check_date_from` 传成 `"2026-02-09"`：应按接口要求传 `20260209`。
- 一次查询人数过多：超过上限需要分批。
- 补卡查询把时间当整数时间戳传：很多接口要字符串。
