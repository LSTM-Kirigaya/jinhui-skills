# API 参考

## 获取用户信息

```http
GET https://watcha.cn/oauth/api/userinfo?access_token=your_access_token
```

### 成功响应

```json
{
  "statusCode": 200,
  "data": {
    "user_id": 12345,
    "nickname": "用户昵称",
    "avatar_url": "https://watcha.tos-cn-beijing.volces.com/dev/user/profile/avatar/12000000_1757187302_user_12000000.png",
    "email": "user@example.com",
    "phone": "13800138000"
  }
}
```

### 异常响应

```json
{
  "statusCode": 400,
  "code": "ERROR",
  "message": "无效的 access_token"
}
```

### 字段说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | number | 用户唯一标识（用于关联账号） |
| `nickname` | string | 用户昵称 |
| `avatar_url` | string | 头像 URL，存在时才返回 |
| `email` | string | 用户邮箱，需 `email` scope 且用户同意后才返回 |
| `phone` | string | 用户手机号，需 `phone` scope 且用户同意后才返回 |

> **注意**：`email` 和 `phone` 字段仅在授权时请求了对应 scope 且用户同意后才会返回。若用户未绑定对应信息，即使授权了相应 scope，响应中也不会包含该字段。第三方应用需自行处理字段缺失的情况。

---

## 刷新 AccessToken

```http
POST https://watcha.cn/oauth/api/token
Content-Type: application/x-www-form-urlencoded
```

请求体：

```json
{
    "grant_type": "refresh_token",
    "refresh_token": "your_refresh_token"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `grant_type` | string | 是 | 固定为 `refresh_token` |
| `refresh_token` | string | 是 | RefreshToken |

### 成功响应

```json
{
  "access_token": "XXXX",
  "token_type": "Bearer",
  "expires_in": 1800,
  "refresh_token": "XXXX",
  "scope": "read"
}
```

### 异常响应

```json
{
  "error": "invalid_grant",
  "error_description": "Token 刷新失败: invalid refresh token"
}
```

---

## 校验 Token 是否有效

```http
POST https://watcha.cn/oauth/api/introspect
```

请求体：

```json
{
    "token": "your_token",
    "token_type_hint": "access_token"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `token` | string | 是 | 要验证的 token |
| `token_type_hint` | string | 否 | `access_token` 或 `refresh_token` |

### 响应示例

#### Token 无效

```json
{
  "statusCode": 200,
  "data": {
    "active": false
  }
}
```

#### AccessToken 有效

```json
{
  "statusCode": 200,
  "data": {
    "active": true,
    "scope": "read",
    "client_id": "your_client_id",
    "token_type": "access_token",
    "expired_at": 1770054311
  }
}
```

#### RefreshToken 有效

```json
{
  "statusCode": 200,
  "data": {
    "active": true,
    "scope": "read",
    "client_id": "your_client_id",
    "token_type": "refresh_token",
    "expired_at": 1770054311
  }
}
```
