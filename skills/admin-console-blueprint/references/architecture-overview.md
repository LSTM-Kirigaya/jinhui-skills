# Architecture Overview

## Goal

This blueprint describes a reusable admin console with these characteristics:

- an independent SPA admin frontend
- a Go backend that exposes `/api/admin/*`
- shared repository with the main product codebase
- separate deployment surfaces for static frontend and API service

It is a good fit when the admin system is bigger than a single CRUD page and needs consistent shell, auth, and module boundaries.

## High-Level Topology

```text
Browser
  -> Admin SPA
     -> fetch(..., credentials: include)
        -> Go service
           -> /api/admin/session
           -> /api/admin/login
           -> /api/admin/logout
           -> /api/admin/<module>/*
              -> service layer
                 -> repo layer
                    -> database / storage / internal services
```

## Core Design Choices

### Independent admin frontend

Use a standalone SPA when:

- admin release cadence differs from the main app
- the admin surface has many list/detail/editor flows
- desktop-oriented layouts are acceptable
- a static host is desirable

This avoids mixing admin-only pages into the public product frontend.

### Same-repo backend integration

Keep admin APIs in the same backend repository when:

- admin flows depend on internal domain services
- reuse of repos, storage clients, message services, or worker services matters
- auth, logging, and database access should follow one backend standard

The admin surface is separate at the route and module level, not necessarily as a separate server binary.

### Shared admin shell

The frontend should expose one consistent shell:

- left sidebar or top-level navigation
- shared page container
- shared request client
- shared table, form, dialog, toast, and skeleton primitives

This is what turns multiple tools into a single console.

## Recommended Frontend Shape

```text
admin/
  src/
    App.tsx
    main.tsx
    config.ts
    lib/
      api.ts
    components/
      admin-sidebar.tsx
      ui/*
    pages/
      login-page.tsx
      overview-page.tsx
      <module>-page.tsx
      <module>-detail-page.tsx
```

The UI shell should support:

- login gate
- session bootstrap
- overview entry page
- module list pages
- module detail or review pages

## Recommended Backend Shape

```text
backend/internal/admin/
  domain/
  handler/
  service/
  repo/
```

This is a clean boundary for internal admin code without forcing a separate backend repository.

## Generic Module Families

This blueprint is intended for consoles that mix several module types:

- work-order queues
- report or moderation queues
- resource catalogs
- rule libraries
- benchmark dataset and run management
- system settings or reserved future modules

These modules can share shell and auth while keeping their own handler/service/repo wiring.

## Typical User Flows

### Session bootstrap

1. App loads.
2. Frontend calls `/api/admin/session`.
3. If authenticated, render routes.
4. If not authenticated, show login page.

### CRUD module

1. List page loads filterable records.
2. User opens detail or inline editor.
3. Frontend submits `POST`, `PATCH`, or `DELETE`.
4. Backend validates admin session and performs service-layer logic.
5. UI refreshes list or local detail state.

### Review or moderation module

1. Admin opens queue page.
2. Admin drills into detail page.
3. Admin updates status, resolution notes, or side effects.
4. Backend may trigger notification, cleanup, or reward logic.

### Benchmark module

1. Admin manages samples or batches.
2. Admin launches a run.
3. Backend records the run and coordinates execution.
4. Admin inspects run detail, per-sample results, and status.

## Sanitized Prototype-To-Generic Mapping

Use this abstract mapping when rewriting an existing console into a reusable blueprint:

| Source pattern | Generic replacement |
|---|---|
| brand-specific admin site | `Product Admin Console` |
| product-specific feedback page | feedback work-order module |
| product-specific report page | content report/review module |
| product-specific benchmark page | dataset benchmark module |
| product-specific library editor | resource catalog module |
| product-specific rules table | rule library module |

Do not preserve real product names or internal vocabulary unless the new consumer explicitly wants them.
