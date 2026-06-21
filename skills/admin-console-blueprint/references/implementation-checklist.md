# Implementation Checklist

## 1. Create The Skeleton

- create a standalone admin frontend directory
- add React, Vite, Router, Tailwind, and shared UI primitives
- create `main.tsx`, `App.tsx`, `config.ts`, and `lib/api.ts`
- add sidebar and overview shell

## 2. Add Session Flow

- implement login page
- implement `/api/admin/login`, `/logout`, `/session`
- ensure frontend uses `credentials: "include"`
- gate protected routes on session bootstrap

## 3. Add Backend Admin Boundary

- create `internal/admin/domain`
- create `internal/admin/handler`
- create `internal/admin/service`
- create `internal/admin/repo`
- wire admin modules in one backend composition point

## 4. Standardize API Contracts

- use one response envelope
- standardize pagination params
- standardize list filters where reasonable
- use stable app error codes and readable messages

## 5. Build Shared UI Patterns

- table shell
- filter toolbar
- status cards
- dialog and confirm dialog
- loading skeleton
- toast feedback

## 6. Add First Real Modules

Recommended order:

1. feedback work orders
2. content reports or moderation queue
3. one resource catalog
4. benchmark or batch execution module
5. rule library or settings

This sequence gives quick proof that the shell and auth model are working.

## 7. Provision Admin Accounts

- add a CLI bootstrap command if it does not exist
- make sure the command reads the same backend config as the server
- verify the command creates or resets admins without exposing a public API

## 8. Configure Deployment

- add Vite proxy for local development
- configure SPA fallback on static host
- set preview and production API bases
- configure backend admin CORS allowed origins if cross-origin

## 9. Validate Before Handoff

- login works
- logout works
- session bootstrap works after refresh
- protected routes reject unauthenticated access
- one CRUD module works end-to-end
- one status-update module works end-to-end
- one complex module like benchmark can load, mutate, and refresh

## 10. Sanitized Documentation Check

If publishing the architecture as a reusable skill or internal blueprint:

- replace real domains
- replace real Cookie names
- replace real account names
- remove secret examples
- keep module behavior and architecture intact
