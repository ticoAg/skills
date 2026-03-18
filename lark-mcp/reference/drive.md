# 云空间 (Drive)

适用场景：

- 创建文件夹
- 列目录
- 移动文件
- 删除文件

## 当前项目中的推荐入口

- `drive.folder.create`
- `drive.folder.list`
- `drive.file.move`
- `drive.file.delete`

若涉及协作者权限，请转到 `reference/permissions.md`。

身份建议：

- 这组能力在当前注册表中多数是 `dual`
- 如果目标是“创建后当前用户直接能打开和管理”，优先 `identity: "user"`
- 如果是机器人自动化目录，才考虑 `tenant`

## 关键注意事项

1. `folder_token` 和 `file_token` 不同，不要混用。
2. 删除 / 移动时常见还要传 `type`，必须与真实对象类型匹配。
3. tenant 身份下没有“我的空间”这一类用户私有根目录语义，很多场景需要显式父目录。
4. 用户只给了一个飞书链接时，先从 URL 提 token，再 `help` 确认字段。

## URL 到 token

常见文件夹 URL：

`https://xxx.feishu.cn/drive/folder/{folder_token}`

如果上下文直接给的是链接，通常需要先提取 `{folder_token}`。

## 典型工作流

### 新建项目目录

1. 确认父目录 `folder_token`
2. `drive.folder.create`
3. 如需授权，再接 `perm.permission-member.grant`

### 列目录后移动文件

1. `drive.folder.list`
2. 确认目标 `file_token`
3. `drive.file.move`

### 删除误建文件

1. 确认 `file_token`
2. 确认 `type`
3. `drive.file.delete`

## 常见类型

| 类型 | 说明 |
| --- | --- |
| `doc` | 旧版文档 |
| `docx` | 新版文档 |
| `sheet` | 电子表格 |
| `bitable` | 多维表格 |
| `folder` | 文件夹 |
| `file` | 上传文件 |
| `mindnote` | 思维导图 |
| `shortcut` | 快捷方式 |

## Common Mistakes

- 不传父目录就创建文件夹：在很多自动化上下文里会失败。
- 用 `folder_token` 当 `file_token` 传给移动/删除。
- `type` 跟真实对象不匹配，导致接口报错。
