---
name: admin-console-blueprint
description: Use when you need to design, scaffold, refactor, or document a medium-sized admin console built as an independent Vite/React SPA backed by modular Go admin APIs, Cookie session auth, and CLI-provisioned administrator accounts. Helpful for tasks like planning a new admin console, extracting reusable architecture from an existing console, adding `/api/admin/*` modules, or converting a one-off internal page into a structured admin system.
rootUrl: https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/admin-console-blueprint/SKILL.md
tags:
  - admin
  - console
  - react
  - vite
  - go
  - blueprint
model: gpt-5
---

# Admin Console Blueprint

## Overview

This skill is a sanitized blueprint for a production-style admin console:

- frontend: independent SPA admin site
- backend: modular Go admin APIs under `/api/admin/*`
- auth: HttpOnly Cookie session
- ops: administrator accounts created by CLI, not public registration

Use it when the goal is to build or restructure a similar console, not when you only need a tiny single-page internal tool.

## When To Use This Skill

Trigger this skill for requests such as:

- "Build a Vite + Go admin console"
- "Add a real admin backend to this internal dashboard"
- "Refactor our ad hoc admin pages into a proper console"
- "Design `/api/admin/*` routes with Cookie auth"
- "Document the architecture of this admin system so another engineer can recreate it"

Do not use this skill for:

- public end-user websites
- mini program UI work
- mobile app-only admin tooling
- one-off scripts with no admin shell, auth, or module system

## What This Skill Provides

- a reusable architecture for SPA admin frontend + same-repo Go backend
- a module playbook for list/detail/CRUD/status-review/benchmark style pages
- a security model centered on Cookie sessions and CLI-provisioned admins
- deployment guidance for static hosting plus API service separation
- a replication checklist for building a similar console from scratch

## Workflow

### 1. Start with system shape

Read [references/architecture-overview.md](./references/architecture-overview.md) first to decide:

- whether the admin site is an independent SPA
- whether admin APIs live inside the main Go service
- how modules share a sidebar, shell, and request client

### 2. Choose frontend implementation

Read [references/frontend-architecture.md](./references/frontend-architecture.md) when you need:

- route structure
- shared page shell
- request client patterns
- list/detail/editor page composition
- environment variable and local proxy setup

### 3. Define backend boundaries

Read [references/backend-architecture.md](./references/backend-architecture.md) when you need:

- `handler -> service -> repo -> domain` layering
- admin route registration
- module bootstrap wiring
- common endpoint families for CRUD, review, and batch execution

### 4. Lock auth and security rules

Read [references/auth-and-security.md](./references/auth-and-security.md) before implementing:

- Cookie session auth
- admin middleware
- CORS behavior
- CLI-only admin bootstrap
- sanitization and secret-handling rules

### 5. Pick and extend modules

Read [references/module-playbook.md](./references/module-playbook.md) when mapping business needs into reusable admin modules such as:

- feedback work orders
- content reports and review queues
- benchmark datasets and runs
- resource catalogs
- rule or energy libraries

### 6. Prepare rollout and validation

Read [references/deployment-and-env.md](./references/deployment-and-env.md) and [references/implementation-checklist.md](./references/implementation-checklist.md) before implementation or handoff.

## Output Expectations

When using this skill, prefer outputs that are:

- architecture-first
- module-oriented
- implementation-ready
- sanitized and portable

Avoid copying project-specific names, secrets, domains, Cookie names, table names, or operational identifiers into the final result.
