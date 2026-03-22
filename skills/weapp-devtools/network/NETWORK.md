---
name: weapp-devtools-network
description: 微信小程序网络操作指南。提供网络请求拦截和 Mock 功能，包括设置 Mock、移除 Mock 和清除所有 Mock 规则。
---

# 网络操作

网络请求拦截和 Mock 功能。

---

## 🎭 Mock 网络请求

拦截指定 URL 的请求并返回自定义响应。

```bash
mrc mock <URL> [响应JSON] --port 9420
```

**基础示例：**
```bash
# Mock 用户接口
mrc mock /api/user '{"name": "test", "id": 123}' --port 9420

# Mock 列表接口
mrc mock /api/list '{"items": [1, 2, 3]}' --port 9420

# Mock 成功响应
mrc mock /api/success '{"code": 0, "message": "success"}' --port 9420
```

**复杂响应示例：**
```bash
# Mock 用户详细信息
mrc mock /api/user/profile '{
  "code": 0,
  "data": {
    "id": 123,
    "nickname": "测试用户",
    "avatar": "https://example.com/avatar.jpg",
    "level": 5,
    "points": 1000
  }
}' --port 9420

# Mock 食物列表
mrc mock /api/foods '{
  "code": 0,
  "data": {
    "list": [
      {"id": 1, "name": "鸡蛋", "calories": 70},
      {"id": 2, "name": "牛奶", "calories": 120}
    ],
    "total": 2
  }
}' --port 9420
```

**输出示例：**
```
✅ Mock 已设置: /api/user
📦 数据: {
  "url": "/api/user",
  "response": {"name": "test", "id": 123}
}
```

---

## 🗑️ 移除 Mock

移除指定 URL 的 Mock。

```bash
mrc unmock <URL> --port 9420
```

**示例：**
```bash
# 移除用户接口的 Mock
mrc unmock /api/user --port 9420

# 移除列表接口的 Mock
mrc unmock /api/list --port 9420
```

**输出示例：**
```
✅ Mock 已移除: /api/user
```

---

## 🧹 清除所有 Mock

一次性清除所有 Mock 规则。

```bash
mrc clearMocks --port 9420
```

**输出示例：**
```
✅ 所有 Mock 已清除
```

---

## 典型工作流

### 场景 1：模拟后端数据

```bash
# 1. 设置 Mock
mrc mock /api/user/profile '{
  "code": 0,
  "data": {
    "nickname": "Mock用户",
    "level": 10
  }
}' --port 9420

# 2. 刷新页面触发请求
mrc relaunch /pages/profile/index --port 9420

# 3. 截图验证显示
mrc screenshot ./screenshots/weapp/profile-mocked.png --port 9420

# 4. 清除 Mock
mrc unmock /api/user/profile --port 9420
```

### 场景 2：测试错误处理

```bash
# Mock 错误响应
mrc mock /api/data '{
  "code": 500,
  "message": "服务器内部错误"
}' --port 9420

# 执行操作触发请求
mrc click view --port 9420
mrc wait 1000 --port 9420

# 检查错误提示是否显示
mrc screenshot ./screenshots/weapp/error-handling.png --port 9420

# 清除 Mock
mrc clearMocks --port 9420
```

### 场景 3：分页数据测试

```bash
# Mock 第一页数据
mrc mock /api/foods?page=1 '{
  "code": 0,
  "data": {
    "list": [
      {"id": 1, "name": "食物1"},
      {"id": 2, "name": "食物2"}
    ],
    "hasMore": true
  }
}' --port 9420

# 测试加载更多...

# 清除 Mock
mrc clearMocks --port 9420
```

---

## Mock 规则匹配

Mock 规则支持以下匹配方式：

### 精确匹配

```bash
# 完全匹配 URL
mrc mock /api/user '{"name": "test"}' --port 9420
# 匹配: /api/user
# 不匹配: /api/user/123, /api/user?id=1
```

### 前缀匹配

```bash
# 匹配以 /api/user 开头的 URL
mrc mock /api/user '{"name": "test"}' --port 9420
# 匹配: /api/user, /api/user/123, /api/user/profile
```

**⚠️ 注意：** 具体匹配行为取决于 miniprogram-automator 的实现版本。

---

## 与网络请求配合使用

Mock 会影响小程序中的所有网络请求：

- `wx.request`
- `wx.downloadFile`
- `wx.uploadFile`

**Mock 优先级：**
1. 先检查是否有匹配的 Mock 规则
2. 如果有，返回 Mock 响应
3. 如果没有，发送真实请求

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Mock 不生效 | URL 不匹配 | 检查 URL 路径是否完全一致 |
| Mock 数据格式错误 | JSON 格式问题 | 确保 JSON 格式正确，使用单引号包裹 |
| 清除 Mock 后仍返回 Mock 数据 | 缓存问题 | 重新启动开发者工具 |
| Mock 影响其他请求 | URL 匹配范围过大 | 使用更精确的 URL 路径 |

---

## 网络命令速查表

| 命令 | 作用 | 示例 |
|------|------|------|
| `mock` | 设置 Mock 规则 | `mrc mock /api/user '{"name":"test"}'` |
| `unmock` | 移除 Mock 规则 | `mrc unmock /api/user` |
| `clearMocks` | 清除所有 Mock | `mrc clearMocks` |

---

## 参考

- [微信小程序网络 API](https://developers.weixin.qq.com/miniprogram/dev/api/network/request/wx.request.html)
- [miniprogram-automator Mock 文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/auto/automator.html#mock)
