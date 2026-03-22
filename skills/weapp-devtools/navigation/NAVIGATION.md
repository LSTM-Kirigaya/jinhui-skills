# 页面导航

管理小程序页面跳转和导航栈。

---

## 🔄 切换 Tab 页面

切换到 tabBar 配置的页面。

```bash
mrc switchTab <页面路径> --port 9420
```

**示例：**
```bash
# 切换到首页
mrc switchTab /pages/index/index --port 9420

# 切换到社区/圈子页面
mrc switchTab /pages/community/index --port 9420

# 切换到记录页面
mrc switchTab /pages/record/index --port 9420

# 切换到个人中心
mrc switchTab /pages/profile/index --port 9420
```

**输出示例：**
```
✅ 已切换到: pages/community/index
📦 数据: {
  "path": "pages/community/index"
}
```

**⚠️ 注意：**
- 只能跳转到 `app.json` 中 `tabBar` 配置的页面
- 路径必须以 `/` 开头
- 不会触发页面栈变化（Tab 页面是独立的）

---

## 🔙 返回上一页

返回页面栈中的上一页。

```bash
mrc back --port 9420
```

**输出示例：**
```
✅ 已返回，当前页面: pages/community/index
📦 数据: {
  "path": "pages/community/index"
}
```

**行为说明：**
- 等同于用户点击左上角返回按钮
- 如果当前是页面栈的第一个页面，则返回 Tab 页面或退出

**完整示例：**
```bash
# 1. 当前在首页
mrc where --port 9420
# 输出: pages/index/index

# 2. 跳转到详情页（假设点击了某个元素）
mrc click view --port 9420

# 3. 检查当前页面
mrc where --port 9420
# 输出: pages/detail/index

# 4. 返回上一页
mrc back --port 9420

# 5. 确认回到首页
mrc where --port 9420
# 输出: pages/index/index
```

---

## 🚀 重启到指定页面

关闭所有页面，打开指定页面。

```bash
mrc relaunch <页面路径> --port 9420
```

**示例：**
```bash
# 重启到首页
mrc relaunch /pages/index/index --port 9420

# 重启到分析页面
mrc relaunch /pages/analyze/index --port 9420

# 重启到食物库
mrc relaunch /pages/food-library/index --port 9420

# 重启到登录页
mrc relaunch /pages/login/index --port 9420
```

**输出示例：**
```
✅ 已重启到: pages/analyze/index
📦 数据: {
  "path": "pages/analyze/index"
}
```

**使用场景：**
- 需要清空页面栈重新进入
- 跳转到非 TabBar 页面
- 登录后跳转到首页

**与 switchTab 的区别：**

| 命令 | 适用页面 | 页面栈行为 |
|------|---------|-----------|
| `switchTab` | TabBar 页面 | 不修改页面栈，切换 Tab |
| `relaunch` | 任意页面 | 清空页面栈，打开新页面 |

---

## 📚 获取页面栈

获取当前页面栈信息。

```bash
mrc stack --port 9420
```

**输出示例（单层栈）：**
```json
{
  "depth": 1,
  "stack": [
    {
      "index": 0,
      "path": "pages/index/index",
      "query": {},
      "url": "pages/index/index?"
    }
  ],
  "current": {
    "index": 0,
    "path": "pages/index/index",
    "query": {},
    "url": "pages/index/index?"
  }
}
```

**输出示例（多层栈）：**
```json
{
  "depth": 3,
  "stack": [
    {
      "index": 0,
      "path": "pages/index/index",
      "query": {},
      "url": "pages/index/index?"
    },
    {
      "index": 1,
      "path": "pages/list/index",
      "query": {},
      "url": "pages/list/index?"
    },
    {
      "index": 2,
      "path": "pages/detail/index",
      "query": {"id": "123"},
      "url": "pages/detail/index?id=123"
    }
  ],
  "current": {
    "index": 2,
    "path": "pages/detail/index",
    "query": {"id": "123"},
    "url": "pages/detail/index?id=123"
  }
}
```

**字段说明：**
- `depth`：页面栈深度（页面数量）
- `stack`：页面栈数组，索引 0 为第一个页面
- `current`：当前页面信息
- `path`：页面路径
- `query`：页面参数
- `url`：完整 URL（含参数）

---

## 📍 获取当前页面信息

获取当前页面的详细信息。

```bash
mrc where --port 9420
# 或
mrc pageInfo --port 9420
```

**输出示例：**
```
✅ 当前页面: pages/community/index
📦 数据: {
  "path": "pages/community/index",
  "query": {},
  "url": "pages/community/index?"
}
```

**JSON 格式输出：**
```bash
mrc where --json --port 9420
```

**输出：**
```json
{
  "success": true,
  "data": {
    "path": "pages/community/index",
    "query": {},
    "url": "pages/community/index?"
  },
  "message": "当前页面: pages/community/index"
}
```

---

## 典型工作流

### 场景 1：Tab 页面切换测试

```bash
# 切换到社区页面
mrc switchTab /pages/community/index --port 9420

# 截图验证
mrc screenshot ./community.png --port 9420

# 切换到记录页面
mrc switchTab /pages/record/index --port 9420

# 截图验证
mrc screenshot ./record.png --port 9420
```

### 场景 2：页面跳转和返回测试

```bash
# 1. 在首页
mrc where --port 9420

# 2. 点击跳转到详情（假设按钮触发跳转）
mrc click view --port 9420
mrc wait 1000 --port 9420

# 3. 检查页面栈
mrc stack --port 9420

# 4. 返回
mrc back --port 9420

# 5. 确认回到首页
mrc where --port 9420
```

### 场景 3：带参数页面测试

```bash
# 重启到带参数的分析页面
mrc relaunch /pages/analyze/index --port 9420

# 检查页面信息和参数
mrc where --json --port 9420
```

---

## 导航命令速查表

| 命令 | 作用 | 适用页面 | 示例 |
|------|------|---------|------|
| `switchTab` | 切换 Tab | TabBar 页面 | `mrc switchTab /pages/index/index` |
| `back` | 返回上一页 | 任意 | `mrc back` |
| `relaunch` | 重启到页面 | 任意 | `mrc relaunch /pages/login/index` |
| `where` | 获取当前页 | 任意 | `mrc where` |
| `stack` | 获取页面栈 | 任意 | `mrc stack` |

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `switchTab failed` | 页面不在 tabBar 配置中 | 检查 `app.json` 的 tabBar 配置 |
| `back no effect` | 已经是第一个页面 | 检查页面栈深度 |
| `relaunch error` | 页面路径错误 | 确认路径以 `/` 开头且页面存在 |
| 页面参数丢失 | 参数未正确传递 | 使用 `relaunch` 时 URL 带参数 |
