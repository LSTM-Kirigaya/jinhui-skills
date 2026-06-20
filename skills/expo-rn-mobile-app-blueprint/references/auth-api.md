# Auth And API Pattern

Use an adapter-based API client so shared code stays platform-neutral.

## Shared Types

Put these in `packages/core` or equivalent:

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

export type AuthSession = {
  token: string
  user: AppUser
}
```

## API Client Shape

The shared API client should accept adapters:

```ts
type RequestAdapter = (url: string, options?: {
  method?: string
  headers?: Record<string, string>
  body?: unknown
  timeoutMs?: number
}) => Promise<{ status: number; data: unknown; headers: Record<string, string> }>

type TokenStorage = {
  getAccessToken(): Promise<string | null>
  setSession(session: AuthSession): Promise<void>
  clearSession(): Promise<void>
}
```

Implement business calls in shared code, but inject React Native transport and storage from `apps/mobile/src/api.ts`.

## React Native Adapter

- Use global `fetch`.
- Serialize JSON bodies.
- Parse non-JSON responses into `{ message: text }`.
- Store access token and user summary in AsyncStorage.
- Use neutral storage keys such as:
  - `mobile_access_token`
  - `mobile_user`
  - `mobile_user_id`

## Auth Provider

Use a provider that:

1. Checks AsyncStorage during bootstrap.
2. Exposes `isBootstrapping` and `isAuthenticated`.
3. Provides `loginWithPassword`, `loginWithCode`, `register`, and `logout`.
4. Gates navigation with a root stack: unauthenticated users see login, authenticated users see tabs.

Never place real credentials, private tokens, or production hosts in examples.
