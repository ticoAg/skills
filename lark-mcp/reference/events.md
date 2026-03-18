# 事件订阅与卡片回调（高级补充）

本文件用于帮助 agent 理解飞书事件和卡片交互的接入背景。

重要说明：

- 这不是当前 `lark-mcp` 已默认暴露的 facade 能力
- 当前仓库的 MCP 主路径主要是 OpenAPI 调用面，不是长连接事件服务
- 如果用户问的是“如何在宿主系统里接飞书事件 / 卡片按钮回调”，这里可以作为背景参考

## 飞书事件接入的关键结论

1. 飞书支持长连接事件订阅，不一定需要公网回调地址。
2. 卡片交互回调常见事件是 `card.action.trigger`。
3. 卡片回调返回结构和普通消息发送结构不同，尤其是 v2 卡片更新格式。

## 对 agent 有帮助的判断点

当用户需求是下面这些时，不要误导到普通 `chat.message.create`：

- “点卡片按钮后更新卡片”
- “接收飞书消息事件”
- “做机器人交互回调”
- “收事件推送并触发业务逻辑”

这类需求更像“宿主服务接飞书事件”，不是单纯的 MCP OpenAPI 单次调用。

## 长连接模式

长连接模式的价值：

- 不需要公网 HTTP 回调地址
- 不需要在当前问题里先处理验签 / 加解密细节
- 更适合本地开发和内部服务接事件

## card.action.trigger

卡片交互时常见可用信息：

- `action.value`
- `action.tag`
- `action.option`
- `action.form_value`
- `operator.open_id`
- `context.open_message_id`
- `context.open_chat_id`

## v2 卡片更新要点

返回卡片更新内容时，关注这些结构：

- `card.type = "raw"`
- `card.data.schema = "2.0"`
- 卡片元素在 `card.data.body.elements`

## 对当前仓的实际建议

- 如果用户只是“发一张卡片消息”，先看 `reference/messages.md`
- 如果用户要“接卡片点击并更新卡片”，这是宿主服务设计问题，不能只靠当前 facade 文档解决
