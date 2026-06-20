# Auth And API Pattern

使用适配器式 API 客户端，让共享代码保持平台无关。

## Shared Types

放在 `packages/core` 或等价位置：

```ts
export type ApiResponse<T> = {
  success?: boolean
  data?: T
  error?: string
  message?: string
}

export type AppUser = {
  id: string
  phone?: string | null
  email?: string | null
  nickname?: string | null
  avatarUrl?: string | null
}

export type AuthTokens = {
  accessToken: string
  refreshToken: string
  userId: string
}
```

## API Client Shape

`packages/api-client` 定义适配器接口：

```ts
export interface ApiClientRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  headers?: Record<string, string>
  body?: unknown
  timeoutMs?: number
}

export interface UploadFileInput {
  url: string
  fileUri: string
  fieldName: string
  fileName?: string
  mimeType?: string
  headers?: Record<string, string>
  timeoutMs?: number
}

export interface TokenStorage {
  getAccessToken(): Promise<string | null>
  setTokens(tokens: AuthTokens): Promise<void>
  clearTokens(): Promise<void>
}

export interface ApiClientAdapters {
  request(url: string, options?: ApiClientRequestOptions): Promise<{ status: number; data: unknown; headers: Record<string, string> }>
  uploadFile(input: UploadFileInput): Promise<{ status: number; data: unknown; headers: Record<string, string> }>
  tokenStorage: TokenStorage
}
```

业务请求方法写在 `packages/api-client`，通过构造函数或工厂接收 `baseUrl` 与 `adapters`。

## React Native Adapter

`apps/mobile/src/api.ts` 注入：

- 全局 `fetch` 做 HTTP 请求
- JSON body 序列化，非 JSON 响应降级为 `{ message: text }`
- `AsyncStorage` 存取 accessToken / refreshToken / userId
- `XMLHttpRequest` 做带超时的 multipart 文件上传
- 请求追踪（可选）：记录最近 N 条请求用于调试

示例存储 key（保持前缀一致）：

```ts
const ACCESS_TOKEN_KEY = 'myapp_mobile_access_token'
const REFRESH_TOKEN_KEY = 'myapp_mobile_refresh_token'
const USER_ID_KEY = 'myapp_mobile_user_id'
```

## Auth Provider

职责：

1. 启动时调用 `tokenStorage.getAccessToken()` 判断登录状态。
2. 暴露 `isBootstrapping` 与 `isAuthenticated`。
3. 提供登录方法（根据业务选择）：
   - `loginWithPassword(phone, password)`
   - `loginWithSMSCode(phone, code)`
   - `loginWithWechat(...)`
   - `loginWithDebugAccount()`（仅开发环境）
4. 提供 `logout()` 清除 token 并切换状态。
5. 用 Root Stack gate：未登录显示 Login，已登录显示 MainTabs。

## Deep Link（可选）

`RootNavigator` 中可监听 `Linking.getInitialURL()` 与 `Linking.addEventListener('url')`，解析 scheme 后导航到对应页面。注意pending路由需要在 `isAuthenticated` 与 `navigationRef.isReady()` 都满足后再执行。

## 安全注意

- 不要把真实凭证、生产 token、生产 API 域名写到示例或 skill 中。
- 敏感配置通过 `app.json extra` + `expo-constants` + 环境变量注入。
