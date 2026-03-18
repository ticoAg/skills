# 日历与会议室 (Calendar)

适用场景：

- 创建 / 更新 / 删除日程
- 查询忙闲
- 增删参与人
- 搜索会议室

## 当前项目中的推荐入口

日历相关：

- `calendar.calendar.primary`
- `calendar.calendar-event.create`
- `calendar.calendar-event.get`
- `calendar.calendar-event.list`
- `calendar.calendar-event.patch`
- `calendar.calendar-event.delete`
- `calendar.calendar-event-attendee.create`
- `calendar.calendar-event-attendee.list`
- `calendar.calendar-event-attendee.batch-delete`
- `calendar.freebusy.list`

会议室相关：

- `vc.room.search`
- `vc.room.list`
- `vc.room.get`

身份建议：

- `calendar.*` 里很多能力是 `dual`
- 如果希望当前用户后续能直接看到/继续编辑事件，优先从 `identity: "user"` 开始
- `vc.room.search` 在当前注册表中更偏 `user_only`

## 关键注意事项

1. 主日历常见 `calendar_id` 为 `primary`。
2. 飞书日历时间字段经常用 Unix 秒级时间戳字符串。
3. 忙闲查询在当前命令层是 `calendar.freebusy.list`，不要想当然写成别的 action。
4. 会议室在 `vc.room.*` 域，不在 `calendar.*` 域。
5. 把会议室加为参与人后，不代表立即预订成功，仍要看后续状态。

## 典型工作流

### 安排一个普通日程

1. `calendar.calendar.primary`
2. `calendar.calendar-event.create`
3. `calendar.calendar-event-attendee.create`

### 安排会议室

1. `vc.room.search`
2. `calendar.freebusy.list`
3. `calendar.calendar-event.create`
4. `calendar.calendar-event-attendee.create`
5. `calendar.calendar-event-attendee.list`

### 改时间 / 取消会议

1. `calendar.calendar-event.patch`
2. 必要时 `calendar.calendar-event-attendee.batch-delete`
3. 或直接 `calendar.calendar-event.delete`

## 高频字段

### `calendar.calendar-event.create`

- `path.calendar_id`
- `data.summary`
- `data.description`
- `data.start_time.timestamp`
- `data.end_time.timestamp`

### `calendar.calendar-event.patch`

- `path.calendar_id`
- `path.event_id`
- 仅更新需要变化的字段

### `calendar.calendar-event-attendee.create`

- `path.calendar_id`
- `path.event_id`
- `data.attendees`
- `params.user_id_type`

### `calendar.freebusy.list`

- `data.time_min`
- `data.time_max`
- `data.user_id`
- `data.room_id`

## Common Mistakes

- 直接传 ISO 日期字符串给时间字段：优先确认是否需要 Unix 秒字符串。
- 以为会议室属于 `calendar.*`：会议室搜索和详情在 `vc.room.*`。
- 创建事件时漏传 `calendar_id`：主日历也要显式传 `primary`。
- 认为添加会议室参与人就一定预约成功：还要回查状态。
