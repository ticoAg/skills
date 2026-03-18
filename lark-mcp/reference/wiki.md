# 知识库 (Wiki)

适用场景：

- 搜索 Wiki 节点
- 列知识空间
- 获取节点详情
- 创建 / 移动 / 重命名节点

## 当前项目中的推荐入口

- `wiki.node.search`
- `wiki.space.list`
- `wiki.space.get`
- `wiki.space.get-node`
- `wiki.space-node.list`
- `wiki.space-node.create`
- `wiki.space-node.move`
- `wiki.space-node.update-title`

身份建议：

- `wiki.node.search` 在当前注册表中更偏 `user_only`
- 大多数 `wiki.space*` / `wiki.space-node*` 为 `user_preferred`

## 关键注意事项

1. `node_token` 和 `obj_token` 不是同一个东西。
2. 搜索到或从 URL 提到的通常是 wiki 节点 token，不一定能直接拿去调文档 API。
3. 真正需要读写页面内容时，经常要先 `wiki.space.get-node` 拿到 `obj_token`，再去走文档域。
4. 机器人或当前用户是否在知识空间成员列表里，会直接影响可见性。

## 典型工作流

### 找一个 Wiki 页面

1. `wiki.node.search`
2. 或已知空间时 `wiki.space-node.list`
3. 需要详情时 `wiki.space.get-node`

### 在知识空间里建新页面

1. `wiki.space.list`
2. 选择 `space_id`
3. `wiki.space-node.create`

### 读写 Wiki 页内容

1. `wiki.space.get-node`
2. 拿 `obj_token`
3. 转到 `reference/documents.md` 中的文档 target

## URL 与 token

常见 URL：

`https://xxx.feishu.cn/wiki/{token}`

这里的 `{token}` 通常是 wiki 节点 token。只有在 `wiki.space.get-node` 返回的 `obj_token` 才是实际文档对象的 token。

## Common Mistakes

- 直接把 wiki URL 里的 token 当文档 token 使用。
- 以为 Wiki API 可以全文搜索正文：当前更适合搜索节点、列树、再进入文档域。
- 没把成员可见性问题和 API 参数问题区分开。
