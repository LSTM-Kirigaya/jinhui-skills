# 授权流程详解

## 1. 引导用户到授权页面

通过浏览器将用户引导到授权页面：

```
GET https://openapi.zhihu.com/authorize?
  redirect_uri=https://yourdomain.com/callback&
  app_id=YOUR_APP_ID&
  response_type=code&
  state=RANDOM_STATE
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `redirect_uri` | string | 是 | 授权回调地址，需与申请时一致 |
| `app_id` | string | 是 | 第三方应用 ID |
| `response_type` | string | 是 | 固定值：`code` |
| `state` | string | 否，强烈推荐 | 随机字符串，用于防止 CSRF 攻击 |

> URL 参数需要进行 URL 编码，尤其是 `redirect_uri` 中的特殊字符。

## 2. 处理回调

### 用户同意授权

重定向到 `redirect_uri` 并附带授权码：

```
https://yourdomain.com/callback?code=AUTH_CODE&state=RANDOM_STATE
```

### 用户拒绝或异常

```
https://yourdomain.com/callback?error=access_denied&error_description=用户拒绝授权&state=RANDOM_STATE
```

### 后端处理回调建议

1. 验证 `state` 是否与会话/Redis 中存储的一致
2. 使用 `code` 调用 `POST https://openapi.zhihu.com/access_token` 换取 token
3. 使用 `access_token` 调用 `GET https://openapi.zhihu.com/user` 获取用户信息
4. 将 token 和用户信息返回给前端

## 3. 使用授权码换取 Token

```http
POST https://openapi.zhihu.com/access_token
Content-Type: application/json
```

请求体：

```json
{
  "app_id": "YOUR_APP_ID",
  "app_key": "YOUR_APP_KEY",
  "grant_type": "authorization_code",
  "redirect_uri": "https://yourdomain.com/callback",
  "code": "AUTH_CODE"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_id` | string | 是 | 第三方应用 ID |
| `app_key` | string | 是 | 第三方应用密钥 |
| `grant_type` | string | 是 | 固定值：`authorization_code` |
| `redirect_uri` | string | 是 | 授权回调地址，需与授权请求一致 |
| `code` | string | 是 | 授权码 |

### 成功响应

```json
{
  "access_token": "fc42fc30390c455184ddbd7e710d05ad",
  "token_type": "bearer",
  "expires_in": 2592000
}
```

## 4. 社交关系接口通用说明

所有社交关系接口均需在请求头中携带 `access_token`：

```
Authorization: Bearer {access_token}
```

### 通用分页参数

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `page` | int | 否 | 页码，从 0 开始 | 0 |
| `per_page` | int | 否 | 每页数量 | 10 |

## 5. 错误处理

所有接口错误均返回 HTTP 200，通过响应体中的 `code` 字段判断错误类型：

| 场景 | code | data |
|------|------|------|
| 缺少 Authorization | 401 | `Missing Authorization in request headers` |
| Authorization 格式错误 | 401 | `Token type is error` |
| access_token 无效或过期 | 401 | `Access token is not valid` |
| 应用权限不足 | 403 | `API Access Deny` |
| 用户不存在 | 404 | `User don't exist` |

错误响应示例：

```json
{
  "code": 401,
  "data": "Access token is not valid"
}
```
