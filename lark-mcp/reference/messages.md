# 消息发送与群组管理指南

## 当前项目中的推荐入口

当前项目默认通过命令层 facade 来理解消息与群组，而不是直接记 raw tool 名。优先关注这些 target：

- `chat.message.create`
- `chat.message.reply`
- `chat.message.update`
- `chat.message.patch`
- `group.chat.create`
- `group.chat.list`
- `group.chat.search`
- `group.chat-members.get`

下方很多示例仍保留 raw 工具名和 payload 细节，这是为了说明消息内容结构与字段约束；真正执行时，请先 `help` 对应的 facade target，再把这些内容结构迁移到 `args.data` / `args.params` 中。

## ⚠️ 关键注意事项

**1. content 必须是 JSON 字符串，不是对象**
```yaml
❌ content: {"text": "hello"}
✅ content: '{"text": "hello"}'
```

**2. receive_id_type 必须匹配 receive_id**
```yaml
# 发送到群组
receive_id: "oc_xxxxx"  # chat_id
receive_id_type: "chat_id"

# 发送到用户
receive_id: "ou_xxxxx"  # open_id
receive_id_type: "open_id"
```

**3. 富文本消息结构复杂，注意嵌套层级**
```yaml
post.zh_cn.content: 三维数组
[
  [  # 第一段
    {"tag": "text", "text": "内容"}
  ],
  [  # 第二段
    {"tag": "text", "text": "更多内容"}
  ]
]
```

**4. 卡片消息需要完整的 JSON schema**

**5. 获取聊天历史需要区分 container_type**

## 发送消息

### 文本消息（最简单）

```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "oc_xxxxx"  # 群组 chat_id
  msg_type: "text"
  content: '{"text": "这是一条文本消息"}'
params:
  receive_id_type: "chat_id"
```

### 发送到用户

```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "ou_xxxxx"  # 需要替换为实际的用户 open_id
  msg_type: "text"
  content: '{"text": "发送给用户的消息"}'
params:
  receive_id_type: "open_id"
  user_id_type: "open_id"  # 如果消息中提及用户
```

### 发送到群组

```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "oc_xxxxx"  # 群组 chat_id
  msg_type: "text"
  content: '{"text": "发送到群组的消息"}'
params:
  receive_id_type: "chat_id"
```

### 富文本消息（post）

**简单富文本：**
```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "oc_xxxxx"  # 需要替换为实际的群组 chat_id
  msg_type: "post"
  content: '{
    "post": {
      "zh_cn": {
        "title": "消息标题",
        "content": [
          [
            {"tag": "text", "text": "这是第一段内容"}
          ],
          [
            {"tag": "text", "text": "这是第二段，", "style": ["bold"]},
            {"tag": "text", "text": "加粗文字"}
          ]
        ]
      }
    }
  }'
params:
  receive_id_type: "chat_id"
```

**富文本格式选项：**
```yaml
# 纯文本
{"tag": "text", "text": "内容"}

# 加粗
{"tag": "text", "text": "内容", "style": ["bold"]}

# 斜体
{"tag": "text", "text": "内容", "style": ["italic"]}

# 删除线
{"tag": "text", "text": "内容", "style": ["strikethrough"]}

# 下划线
{"tag": "text", "text": "内容", "style": ["underline"]}

# 链接
{"tag": "a", "text": "链接文字", "href": "https://example.com"}

# @用户
{"tag": "at", "user_id": "ou_xxxxx", "text": "@张三"}

# @所有人
{"tag": "at", "user_id": "all", "text": "@所有人"}

# 图片
{"tag": "img", "image_key": "img_xxxxx"}

# @群组
{"tag": "at", "user_id": "oc_xxxxx", "text": "@群组名"}
```

**完整富文本示例：**
```json
{
  "post": {
    "zh_cn": {
      "title": "周报汇总",
      "content": [
        [
          {"tag": "text", "text": "大家好，", "style": ["bold"]},
          {"tag": "text", "text": "以下是本周工作总结："}
        ],
        [
          {"tag": "text", "text": "1. 完成项目A开发", "style": ["bold", "underline"]}
        ],
        [
          {"tag": "text", "text": "2. 修复了", "style": ["italic"]},
          {"tag": "text", "text": "3个bug", "style": ["bold", "strikethrough"]}
        ],
        [
          {"tag": "a", "text": "查看详情", "href": "https://example.com"}
        ],
        [
          {"tag": "at", "user_id": "ou_xxxxx", "text": "@张三"},
          {"tag": "text", "text": " 请审核"}
        ]
      ]
    }
  }
}
```

### 图片消息

```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "oc_xxxxx"
  msg_type: "image"
  content: '{"image_key": "img_xxxxx"}'
params:
  receive_id_type: "chat_id"
```

**获取 image_key：** 需要先上传图片到飞书，返回的 image_key 用于发送消息。

### 文件消息

```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "oc_xxxxx"
  msg_type: "file"
  content: '{"file_key": "file_xxxxx"}'
params:
  receive_id_type: "chat_id"
```

### 卡片消息（interactive）

**简单卡片：**
```json
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "title": {
      "content": "卡片标题",
      "tag": "plain_text"
    }
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "content": "卡片内容",
        "tag": "lark_md"
      }
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "content": "查看详情",
            "tag": "plain_text"
          },
          "type": "default",
          "url": "https://example.com"
        }
      ]
    }
  ]
}
```

**使用方式：**
```yaml
工具: mcp__lark__im_v1_message_create
data:
  receive_id: "oc_xxxxx"
  msg_type: "interactive"
  content: '{上面的完整JSON}'
params:
  receive_id_type: "chat_id"
```

### 群名片

```yaml
data:
  receive_id: "oc_xxxxx"
  msg_type: "share_chat"
  content: '{"chat_id": "oc_yyyyy"}'
params:
  receive_id_type: "chat_id"
```

### 个人名片

```yaml
data:
  receive_id: "oc_xxxxx"
  msg_type: "share_user"
  content: '{"user_id": "ou_xxxxx"}'
params:
  receive_id_type: "chat_id"
  user_id_type: "open_id"
```

### 音频消息

```yaml
data:
  receive_id: "oc_xxxxx"
  msg_type: "audio"
  content: '{"file_key": "audio_xxxxx"}'
params:
  receive_id_type: "chat_id"
```

### 视频消息

```yaml
data:
  receive_id: "oc_xxxxx"
  msg_type: "media"
  content: '{"file_key": "video_xxxxx"}'
params:
  receive_id_type: "chat_id"
```

### 表情消息

```yaml
data:
  receive_id: "oc_xxxxx"
  msg_type: "sticker"
  content: '{"key": "sticker_xxxxx"}'
params:
  receive_id_type: "chat_id"
```

## 消息类型总结

| msg_type | content 格式 | 说明 |
|----------|-------------|------|
| text | `{"text": "文本"}` | 纯文本 |
| post | 复杂 JSON | 富文本 |
| image | `{"image_key": "xxx"}` | 图片 |
| file | `{"file_key": "xxx"}` | 文件 |
| audio | `{"file_key": "xxx"}` | 音频 |
| media | `{"file_key": "xxx"}` | 视频 |
| sticker | `{"key": "xxx"}` | 表情 |
| interactive | 卡片 JSON | 卡片 |
| share_chat | `{"chat_id": "xxx"}` | 群名片 |
| share_user | `{"user_id": "xxx"}` | 个人名片 |

## 获取聊天历史

### 获取群聊消息

```yaml
工具: mcp__lark__im_v1_message_list
params:
  container_id_type: "chat"
  container_id: "oc_xxxxx"  # 需要替换为实际的群组 chat_id
  page_size: 20
  sort_type: "ByCreateTimeDesc"  # 或 "ByCreateTimeAsc"
```

### 获取私聊消息

```yaml
params:
  container_id_type: "chat"  # 私聊也是 chat
  container_id: "oc_xxxxx"  # 会话 ID
```

### 获取话题消息（thread）

```yaml
params:
  container_id_type: "thread"
  container_id: "主题消息的 message_id"
```

### 时间范围过滤

```yaml
params:
  start_time: "1704067200"  # 开始时间（秒，10位）
  end_time: "1704153600"    # 结束时间（秒，10位）
```

**注意：** thread 类型不支持时间范围查询。

## 创建群组

### 创建基础群组

```yaml
工具: mcp__lark__im_v1_chat_create
data:
  name: "项目讨论组"  # 可以修改为您需要的群组名称
  user_id_list: ["ou_xxxxx", "ou_yyyyy"]  # 需要替换为实际的用户 open_id 列表
  chat_type: "private"  # 或 "public"
params:
  user_id_type: "open_id"
```

### 创建群组并设置所有者

```yaml
data:
  name: "项目组"  # 可以修改为您需要的群组名称
  owner_id: "ou_xxxxx"  # 需要替换为实际的群主 open_id
  user_id_list: ["ou_yyyyy", "ou_zzzzz"]  # 需要替换为实际的成员 open_id 列表
params:
  user_id_type: "open_id"
```

### 创建公开群组

```yaml
data:
  name: "公开群组"
  chat_type: "public"  # 公开群
  description: "群组描述"
  user_id_list: ["ou_xxxxx"]
params:
  user_id_type: "open_id"
```

### 邀请机器人

```yaml
data:
  name: "群组名称"
  user_id_list: ["ou_xxxxx"]
  bot_id_list: ["cli_xxxxx"]  # 机器人 app_id
params:
  user_id_type: "open_id"
  set_bot_manager: true  # 设置机器人为管理员
```

### 高级群组配置

```yaml
data:
  name: "高级配置群组"
  user_id_list: ["ou_xxxxx"]
  chat_type: "group"
  description: "群组说明"
  i18n_names:
    zh_cn: "中文名称"
    en_us: "English Name"
  add_member_permission: "all_members"  # 谁可邀请成员
  share_card_permission: "all_members"  # 谁可分享群名片
  at_all_permission: "only_owner"       # 谁可@所有人
  edit_permission: "all_members"        # 谁可编辑群信息
  approval_required: false              # 加群是否需要审批
  admin_ids: ["ou_xxxxx"]               # 管理员列表
params:
  user_id_type: "open_id"
```

### 创建保密群组

```yaml
data:
  name: "保密群组"
  user_id_list: ["ou_xxxxx"]
  chat_mode: "group"
  restricted_mode_setting:
    status: true
    screenshot_has_permission_setting: "not_anyone"  # 禁止截图
    download_has_permission_setting: "not_anyone"   # 禁止下载
    message_has_permission_setting: "not_anyone"    # 禁止转发
params:
  user_id_type: "open_id"
```

## 获取群组列表

```yaml
工具: mcp__lark__im_v1_chat_list
params:
  page_size: 50
  sort_type: "ByActiveTimeDesc"  # 按活跃时间排序
useUAT: true
```

## 获取群成员

```yaml
工具: mcp__lark__im_v1_chatMembers_get
path:
  chat_id: "oc_xxxxx"  # 需要替换为实际的群组 chat_id
params:
  page_size: 50
  member_id_type: "open_id"  # 或 "union_id", "user_id"
useUAT: true
```

## 消息模板库

### 模板1: 项目通知

```json
{
  "post": {
    "zh_cn": {
      "title": "项目更新通知",
      "content": [
        [
          {"tag": "text", "text": "项目：", "style": ["bold"]},
          {"tag": "text", "text": "[项目名称]"}
        ],
        [
          {"tag": "text", "text": "状态：", "style": ["bold"]},
          {"tag": "text", "text": "[进行中/已完成]", "style": ["bold", "underline"]}
        ],
        [
          {"tag": "text", "text": "更新内容："}
        ],
        [
          {"tag": "text", "text": "- 完成了模块A开发\n- 修复了3个bug\n- 更新了文档"}
        ],
        [
          {"tag": "a", "text": "查看详情", "href": "https://example.com"}
        ],
        [
          {"tag": "at", "user_id": "ou_xxxxx", "text": "@负责人"},
          {"tag": "text", "text": " 请审核"}
        ]
      ]
    }
  }
}
```

### 模板2: 任务提醒

```json
{
  "post": {
    "zh_cn": {
      "title": "⏰ 任务提醒",
      "content": [
        [
          {"tag": "text", "text": "您有一个任务即将到期：", "style": ["bold", "italic"]}
        ],
        [
          {"tag": "text", "text": "任务：", "style": ["bold"]},
          {"tag": "text", "text": "[任务名称]"}
        ],
        [
          {"tag": "text", "text": "截止时间：", "style": ["bold"]},
          {"tag": "text", "text": "[2024-01-15 18:00]"}
        ],
        [
          {"tag": "text", "text": "优先级：", "style": ["bold"]},
          {"tag": "text", "text": "高", "style": ["bold", "strikethrough"]}
        ]
      ]
    }
  }
}
```

### 模板3: 数据报告

```json
{
  "post": {
    "zh_cn": {
      "title": "📊 数据报告",
      "content": [
        [
          {"tag": "text", "text": "本周数据汇总：", "style": ["bold"]}
        ],
        [
          {"tag": "text", "text": "新增用户：", "style": ["bold"]},
          {"tag": "text", "text": "1,234", "style": ["underline"]}
        ],
        [
          {"tag": "text", "text": "活跃用户：", "style": ["bold"]},
          {"tag": "text", "text": "5,678"}
        ],
        [
          {"tag": "text", "text": "转化率：", "style": ["bold"]},
          {"tag": "text", "text": "12.5%"}
        ],
        [
          {"tag": "a", "text": "查看完整报告", "href": "https://example.com/report"}
        ]
      ]
    }
  }
}
```

## 常见错误与解决方案

### 错误1: "invalid content format"

**原因：** content 不是有效的 JSON 字符串

**解决：**
```yaml
❌ content: {"text": "hello"}                    # 对象，不是字符串
❌ content: '{"text": "hello with \n newline"}'  # 未转义特殊字符
✅ content: '{"text": "hello"}'                  # 正确
✅ content: '{"text": "hello with \\n newline"}' # 转义后的
```

### 错误2: "receive_id not found"

**原因：**
1. receive_id_type 错误
2. 用户/群组不存在
3. 机器人不在群组中

**解决：**
```yaml
# 检查 receive_id_type
群组 → receive_id_type: "chat_id"
用户 → receive_id_type: "open_id"

# 确认机器人已在群组中
```

### 错误3: "permission denied"

**原因：**
1. 没有发送消息权限
2. 群组禁用了机器人发言
3. token 类型错误

**解决：**
```yaml
# 用户操作使用 user access token
useUAT: true

# 检查群组权限设置
```

### 错误4: 富文本消息显示异常

**原因：** content 数组结构错误

**错误示例：**
```json
❌ "content": [
    {"tag": "text", "text": "第一段"}
  ]
```

**正确示例：**
```json
✅ "content": [
    [
      {"tag": "text", "text": "第一段"}
    ]
  ]
```

**注意：** content 是三维数组：`[段落][行][元素]`

## 消息格式示例

更多消息格式示例请参考：[examples/message-formats.md](../examples/message-formats.md)
