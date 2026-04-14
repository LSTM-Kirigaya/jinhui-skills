# 授权流程详解

## 1. 引导用户到授权页面

通过浏览器或 WebView 将用户引导到授权页面：

```
GET https://watcha.cn/oauth/authorize?
  response_type=code&
  client_id=your_client_id&
  redirect_uri=https://myapp.com/callback&
  scope=read&
  state=random_string&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
  code_challenge_method=S256
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `response_type` | string | 是 | 固定为 `code` |
| `client_id` | string | 是 | 客户端 ID |
| `redirect_uri` | string | 是 | 回调地址，需与注册时的 `domain` 匹配 |
| `scope` | string | 否 | 权限范围，多个值用空格分隔 |
| `state` | string | 否，推荐 | 随机字符串，用于防止 CSRF 攻击 |
| `code_challenge` | string | 公开客户端必填 | PKCE `code_challenge`，私密客户端也可填写以加强安全性 |
| `code_challenge_method` | string | 公开客户端必填 | `S256` 或 `plain`（推荐 `S256`） |

> **注意**：`client_id` 中可能包含 `+`、`/`、`=` 等特殊字符，在 URL 中传递时需要进行 URL 编码。例如 `1p9Mcr+CNLPAMFC0` 编码后应为 `1p9Mcr%2BCNLPAMFC0`。

## 2. 处理回调

### 用户同意授权

重定向到 `redirect_uri` 并附带授权码：

```
https://myapp.com/callback?code=AUTH_CODE&state=random_string
```

### 用户拒绝或异常

```
https://myapp.com/callback?error=access_denied&error_description=用户拒绝授权&state=random_string
```

## Scope 说明

Scope 用于控制第三方应用可获取的用户信息范围。用户在授权页面上会看到应用请求的具体权限，并可选择是否同意。

### 可用 Scope

| Scope | 说明 | 返回字段 |
|-------|------|----------|
| `read` | 基础用户信息（默认） | `user_id`、`nickname`、`avatar_url` |
| `email` | 用户邮箱 | `email` |
| `phone` | 用户手机号 | `phone` |

- `read` 为基础权限，始终建议包含
- 多个 scope 之间用**空格**分隔，例如 `scope=read email phone`
- scope 值在 URL 中传递时，空格会被编码为 `%20` 或 `+`

### 示例

仅获取基础信息：

```
scope=read
```

获取基础信息 + 邮箱 + 手机号：

```
scope=read email phone
```

### 授权页面行为

用户在授权页面上会看到应用请求的权限列表。如果请求了 `email` 或 `phone`，用户需要明确同意后，应用才能获取对应信息。

## 3. 使用授权码换取 Token

```http
POST https://watcha.cn/oauth/api/token
Content-Type: application/x-www-form-urlencoded
```

请求体：

```json
{
    "grant_type": "authorization_code",
    "code": "AUTH_CODE",
    "redirect_uri": "https://myapp.com/callback",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "code_verifier": "your_code_verifier"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `grant_type` | string | 是 | 固定为 `authorization_code` |
| `code` | string | 是 | 授权码 |
| `redirect_uri` | string | 是 | 回调地址（需与授权请求一致） |
| `client_id` | string | 是 | 客户端 ID |
| `client_secret` | string | 机密客户端必填 | 公开客户端无需填写 |
| `code_verifier` | string | 使用 PKCE 时必填 | PKCE `code_verifier` |

### 成功响应

```json
{
  "access_token": "XXXX",
  "token_type": "Bearer",
  "expires_in": 1800,
  "refresh_token": "XXXXX",
  "scope": "read"
}
```

### 异常响应

```json
{
  "error": "invalid_grant",
  "error_description": "Token 生成失败: invalid authorize code"
}
```
