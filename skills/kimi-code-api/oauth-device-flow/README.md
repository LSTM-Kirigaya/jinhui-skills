# OAuth 设备码流程（RFC 8628）

与 Kimi CLI / 常见 Coding Agent 插件同源：`https://auth.kimi.com`。

## 常量（以官方/CLI 为准）

- **Client ID**（公开、固定）：`17e5f671-d194-4dfb-9706-5516cb48c098`  
- **Token / 设备授权 Host**：`https://auth.kimi.com`

## 步骤

### 1. 申请设备码

- `POST /api/oauth/device_authorization`  
- `Content-Type: application/x-www-form-urlencoded`  
- Body：`client_id=<Client ID>`  
- 响应 JSON：`device_code`、`user_code`、`verification_uri` / `verification_uri_complete`、`interval`、`expires_in` 等  

请求建议带与下文一致的 **User-Agent**（见 OpenAI 兼容文档中的 KimiCLI 约定）。

### 2. 用户授权

在系统浏览器打开 `verification_uri_complete`（或 `verification_uri`），用户登录并确认。

### 3. 轮询换 token

- `POST /api/oauth/token`  
- Body：`client_id`、`device_code`、`grant_type=urn:ietf:params:oauth:grant-type:device_code`  

成功（HTTP 200）时 body 含：`access_token`、`refresh_token`、`expires_in`、`token_type` 等。  
未就绪时 body 可能含 `error`：`authorization_pending`、`slow_down`；按响应里的 `interval`（秒）退避重试。`expired_token` 等需重新开始设备码流程。

桌面应用里，设备码与轮询常放在**原生层**（无浏览器 CORS），前端通过 IPC/invoke 调用。

### 4. 持久化

- 将令牌写入**应用私有存储**（与「通用设置 JSON」分离可减少误提交密钥）。  
- 建议保存：`access_token`、`refresh_token`、`expires_in`、`token_type`，以及本地写入时间戳，供过期判断。

### 5. Access 续期（必做）

Access token **有效期较短**（常见约 15 分钟）。应用启动或发请求前应：

- `POST /api/oauth/token`  
- `grant_type=refresh_token`、`refresh_token=…`、`client_id=…`  
- 同样使用 `application/x-www-form-urlencoded`，并带 **KimiCLI 族 User-Agent**（与设备码阶段一致）。  

成功后更新存盘；并发请求时应对 **单次刷新** 加锁，避免重复 refresh。

### 6. 登出

删除本地 OAuth 文件或等价存储即可；若需服务端撤销，以 Kimi 文档为准（多数桌面集成仅清本地）。
