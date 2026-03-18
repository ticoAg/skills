# 通讯录 / 用户 / 部门 (Contacts)

适用场景：

- 根据手机号 / 邮箱 / union_id 查用户 ID
- 查用户详情
- 按部门列成员
- 查部门层级

## 当前项目中的推荐入口

用户相关：

- `user.user.lookup-id`
- `user.user.get`
- `user.user.find-by-department`
- `user.user.batch`

部门相关：

- `user.department.get`
- `user.department.children`
- `user.department.parent`
- `user.department.search`
- `user.department.batch`

身份建议：

- `user.user.lookup-id` 在当前注册表里更偏 `tenant_only`
- `user.department.search` 更偏 `user_only`
- `user.user.get` / `find-by-department` 常见为 `user_preferred`

## 关键注意事项

1. 通讯录权限范围会直接影响能不能查到人和部门。
2. `open_id`、`union_id`、`user_id` 不可混用，要和参数里的 `*_id_type` 保持一致。
3. 如果要在任务评论、消息提及、权限授权里操作某个用户，通常先用这里把 ID 找准。
4. 搜索能力和遍历能力不是一回事：搜索往往更依赖用户身份，而按部门遍历通常更稳定。

## 典型工作流

### 已知邮箱或手机号，先找用户 ID

1. `user.user.lookup-id`
2. 拿到 `open_id` 后再去做消息、任务评论、权限等操作

### 查某个用户详情

1. `user.user.get`
2. 需要部门时再调用 `user.department.get`

### 查部门下所有成员

1. `user.department.search` 或先定位已知部门 ID
2. `user.user.find-by-department`

### 遍历组织结构

1. `user.department.children`
2. 递归子部门
3. `user.user.find-by-department`

## 高频字段

### `user.user.lookup-id`

常见输入类型：

- 邮箱
- 手机号
- `union_id`
- 其他业务侧已有外部标识

执行前建议：

- 先 `help` 看当前 schema 允许的输入结构
- 明确希望返回哪种 ID，通常优先 `open_id`

### `user.user.get`

- `path.user_id`
- `params.user_id_type`

### `user.user.find-by-department`

- `params.department_id`
- `params.department_id_type`
- `params.user_id_type`
- `params.page_size`

### `user.department.search`

- 按关键词找部门
- 适合只有“市场部 / 产品部”这类自然语言时先定位部门

## Common Mistakes

- 没配通讯录权限范围就以为接口坏了。
- `ou_` 当成 `user_id` 类型传：它是 `open_id`。
- 明明要提及用户，却没有先统一用户 ID 类型。
- 用搜索接口做全量拉取：大范围遍历更适合按部门分页。
