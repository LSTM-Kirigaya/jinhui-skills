# Frontend Architecture

## Recommended Stack

This blueprint assumes a frontend like:

- React
- Vite
- React Router
- Tailwind CSS
- a reusable UI primitive layer such as shadcn/ui or equivalent
- toast and skeleton primitives for async feedback

The exact component library can change, but the architecture works best when the console has:

- shared page shell
- consistent table and form primitives
- consistent loading, empty, and error states

## Entry And Composition

Recommended bootstrap:

```text
main.tsx
  -> BrowserRouter
  -> ThemeProvider (optional)
  -> App
```

`App` should own:

- session bootstrap
- authenticated vs unauthenticated split
- top-level route declarations
- logout wiring

## Routing Model

Recommended routes:

- `/` or `/overview`
- `/login` only if login is route-based
- `/<module>`
- `/<module>/:id` for detail or review flows
- nested sections for complex modules like benchmark or settings

For an admin console, `BrowserRouter` is usually fine as long as hosting supports SPA fallback.

## Shared Shell

The authenticated experience should share:

- sidebar navigation
- page header pattern
- page width and spacing rules
- route-to-menu mapping
- global toasts

This keeps new modules cheap to add.

## Request Client

Create a shared `adminRequest()` helper with these traits:

- prefixes requests with the configured API base
- sends `credentials: "include"` so Cookie session auth works
- applies default JSON headers
- decodes a shared envelope such as:

```ts
type ApiEnvelope<T> = {
  code?: number
  message?: string
  data?: T
}
```

- throws normalized errors when `res.ok` is false or `code !== 0`

Recommended public frontend contract:

- `POST /api/admin/login`
- `POST /api/admin/logout`
- `GET /api/admin/session`

## Session Bootstrap Pattern

Use a boot flow like:

1. app mounts
2. call `/api/admin/session`
3. if success, render protected routes
4. if failure, render login page

This keeps route guards simple and avoids pushing auth state through every page manually.

## Page Patterns

### Login page

Needs:

- username/password form
- API base display or environment hint
- clear message that admin accounts are provisioned externally

### Overview page

Good place for:

- module entry cards
- queue stats
- counts by status
- reserved entry points for not-yet-built modules

### List page

Use this shape for catalogs, queues, and reports:

- search box
- status filters
- pagination
- summary counts
- row actions or row click

### Detail page

Use this shape when a record has review or side effects:

- metadata panel
- snapshot/content panel
- resolution form
- destructive actions behind confirm dialog

### Editor modal or editor pane

Use when:

- resource schema is moderate
- inline edit is faster than route change
- a record belongs to a list workflow

## Async UX Rules

- show skeletons for first load
- use toasts for save/delete/update feedback
- do not hide failures silently
- prefer optimistic local refresh only when the failure path is easy to recover

## Environment Strategy

Frontend config should come from environment variables, not hardcoded domains.

Recommended rule:

- local dev: API base empty, Vite proxy handles `/api`
- preview: `VITE_ADMIN_API_BASE_URL=https://api-preview.example.com`
- production: `VITE_ADMIN_API_BASE_URL=https://api.example.com`

`config.ts` should trim trailing slashes and export a single accessor.

## Local Dev Proxy

In `vite.config.ts`, proxy:

- `/api`
- any extra backend-owned admin static or debug endpoints that the console links to

This avoids browser-side CORS problems during local development.

## Files Worth Standardizing

```text
src/config.ts
src/lib/api.ts
src/components/admin-sidebar.tsx
src/components/ui/*
src/pages/login-page.tsx
src/pages/overview-page.tsx
```

These files form the stable backbone of the console; module pages can then be added incrementally.
