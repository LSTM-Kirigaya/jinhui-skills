# Deployment And Environment

## Deployment Shape

This blueprint assumes:

- frontend is a static SPA build
- backend is a Go service exposing `/api/admin/*`
- the two can be deployed independently

Typical targets:

- static host for the admin SPA
- API host or cluster for the Go backend

## Environment Variables

Frontend should use one admin API base variable, for example:

```text
VITE_ADMIN_API_BASE_URL
```

Recommended values:

- local development: empty string
- preview: `https://api-preview.example.com`
- production: `https://api.example.com`

Keep domains out of source code.

## Local Development

Recommended local setup:

- run frontend with Vite dev server
- leave `VITE_ADMIN_API_BASE_URL` empty
- proxy `/api` to local backend in `vite.config.ts`

This gives same-origin behavior in the browser without hardcoding localhost API bases into app code.

## Static Hosting

Because admin consoles often use `BrowserRouter`, direct deep links need SPA fallback.

For static hosts, configure a fallback like:

```text
/*    /index.html   200
```

Equivalent mechanisms on other hosts are also fine.

## Cross-Origin Admin

If frontend and backend are not same-origin:

- backend must allow the admin origin
- credentials must be enabled
- frontend fetch calls must use `credentials: "include"`

Example backend environment:

```text
ADMIN_CORS_ALLOWED_ORIGINS=https://admin.example.com,https://preview-admin.example.com
```

## Admin Bootstrap Flow

Recommended operational flow:

1. deploy backend with admin routes enabled
2. run database migrations
3. run a CLI command that creates or resets an admin user
4. open the admin frontend and log in

Generic example:

```bash
cd backend
go run ./cmd/migration -config-dir .
go run ./cmd/create-admin -username admin -display-name "Operations Admin" -config-dir .
```

The exact flags can vary, but the principle stays the same:

- migrations first
- admin bootstrap second
- no web-based admin registration

## Preview And Production

Keep preview and production separate at least by:

- frontend environment variable values
- backend allowed origins
- data source or database

Do not let preview builds silently fall back to same-origin unless that is explicitly intended.

## Deployment Checklist

- static bundle builds successfully
- SPA fallback configured
- API base configured per environment
- admin CORS origins configured if needed
- admin account created
- login, session check, and logout verified
- at least one protected module route verified end-to-end
