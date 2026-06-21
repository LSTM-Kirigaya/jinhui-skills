# Auth And Security

## Session Model

This blueprint uses Cookie session auth for admin pages.

Recommended properties:

- HttpOnly Cookie
- `Secure=true` when served over HTTPS
- `SameSite=Lax` or `SameSite=None` depending on cross-site deployment needs
- cookie validated on every protected admin request

Use Cookie auth instead of storing admin tokens in local storage.

## Public Session Endpoints

Frontend and backend should agree on:

- `POST /api/admin/login`
- `POST /api/admin/logout`
- `GET /api/admin/session`

Typical behavior:

- login validates username/password and sets session Cookie
- logout clears Cookie
- session checks Cookie and returns authenticated account summary

## Middleware Pattern

Protected routes should use one admin middleware such as `AdminAuth`.

Middleware responsibilities:

- read session Cookie
- validate the account is still active
- inject `admin_account_id` and optional `admin_username` into request context
- reject unauthorized requests with stable app error shape

Keep auth checks centralized instead of repeating them inside handlers.

## Administrator Provisioning

This blueprint assumes admin accounts are created outside the web UI.

Recommended rule:

- no self-service admin signup
- no public "create admin" API
- use a CLI command or bootstrap tool to create or reset admins

Typical sequence:

1. run database migrations
2. run `create-admin` style command
3. log into the admin UI

This is safer than exposing account creation through the console itself.

## Password Handling

Recommended rules:

- store password hashes only
- use a modern password hashing function
- compare passwords via service-layer helper
- allow password reset through secure operational workflow, not public endpoints

Do not document real hash formats, salts, or internal account inventory in a sanitized skill.

## CORS Model

If admin frontend and API are not same-origin:

- allow only explicit admin origins
- send `Access-Control-Allow-Credentials: true`
- allow JSON headers and expected methods

Recommended environment shape:

```text
ADMIN_CORS_ALLOWED_ORIGINS=https://admin.example.com,https://preview-admin.example.com
```

Avoid wildcard CORS in production for admin routes.

## Frontend Secret Rules

Do not place these in frontend code:

- admin API keys
- webhook secrets
- service credentials
- bootstrap passwords

Frontend may know:

- API base URL
- user-facing route paths
- non-sensitive feature toggles

## Backend Secret Rules

Keep sensitive values only in backend environment or secret stores:

- session secrets if used
- database credentials
- webhook credentials
- privileged service tokens

The sanitized blueprint should mention the need for these, but never hardcode real values.

## Sanitization Rules For Documentation

When extracting an existing admin console into a reusable skill:

- replace real domains with `admin.example.com` and `api.example.com`
- replace real Cookie names with `admin_session`
- replace real env values with generic placeholders
- replace real table names with role-based descriptions where possible
- avoid enumerating sensitive columns that are irrelevant to architecture

Medium sanitization keeps:

- module categories
- architectural layering
- deployment shape
- generic endpoint families

Medium sanitization removes:

- project identity
- infrastructure identity
- secrets
- operator identifiers

## Review Checklist

Before publishing a sanitized admin skill, verify:

- no real account names remain
- no real Cookie names remain
- no real domains remain
- no real secret values remain
- no internal chat, webhook, or server URLs remain
