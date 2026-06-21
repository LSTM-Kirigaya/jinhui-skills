# Backend Architecture

## Admin Backend Boundary

The admin backend should be isolated by module and route group even when it lives inside the main service.

Recommended namespace:

```text
/api/admin/*
```

Recommended package boundary:

```text
internal/admin/
  domain/
  handler/
  service/
  repo/
```

## Layering

Use a clear flow:

```text
handler -> service -> repo -> database/external dependency
```

### Handler responsibilities

- bind params or JSON
- read auth context
- translate application errors to HTTP responses
- emit request-level logs

### Service responsibilities

- validation
- orchestration
- status transitions
- side effects such as notifications or cleanup
- coordinating multiple repos or shared services

### Repo responsibilities

- query building
- pagination
- persistence
- projection shaping for admin views

### Domain responsibilities

- admin-facing entities
- enumerations
- DTO-like structs that represent the module's business language

## Route Registration

Register admin modules in one backend composition point.

Typical flow:

1. instantiate module repos
2. instantiate module services
3. instantiate handlers
4. create `adminAPI := engine.Group("/api/admin", adminCORS(...))`
5. attach session routes
6. attach `AdminAuth` middleware to protected routes

This keeps admin wiring explicit and debuggable.

## Shared Endpoint Families

Most modules fit one of these endpoint families.

### Session family

- `POST /login`
- `POST /logout`
- `GET /session`

### CRUD family

- `GET /resources`
- `GET /resources/:id`
- `POST /resources`
- `PATCH /resources/:id`
- `DELETE /resources/:id`

### Review queue family

- `GET /reports`
- `GET /reports/stats`
- `GET /reports/:id`
- `PATCH /reports/:id/status`
- optional side-effect endpoints like delete-target, reward, or notify

### Benchmark family

- `GET /benchmark/datasets/*`
- `POST /benchmark/datasets/*`
- `GET /benchmark/runs`
- `GET /benchmark/runs/:id`
- `POST /benchmark/runs`
- `POST /benchmark/runs/:id/cancel`

## Query Contract

Standardize these query params where possible:

- `page`
- `limit`
- `q`
- `status`
- `type`
- module-specific filters

This makes frontend list pages more consistent and reduces bespoke code.

## Response Contract

A unified envelope keeps frontend error handling simple:

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

Guidelines:

- `code = 0` for success
- stable app error codes for business failures
- human-readable `message`
- module payload under `data`

## Shared Services And Reuse

One reason to keep admin APIs in the main backend repo is reuse.

Admin services often depend on:

- storage clients
- message or notification services
- existing domain repos
- benchmark or worker coordinators
- internal cleanup logic

Prefer composition over duplicating business logic in admin-only code.

## Example Module Wiring Pattern

```text
resourceRepo := adminrepo.NewResourceRepo(db)
resourceSvc := adminservice.NewResourceService(resourceRepo, sharedDependency)
resourceHandler := adminhandler.NewResourceHandler(resourceSvc)

adminAPI.GET("/resources", adminAuth, resourceHandler.List)
adminAPI.GET("/resources/:id", adminAuth, resourceHandler.Get)
adminAPI.POST("/resources", adminAuth, resourceHandler.Create)
adminAPI.PATCH("/resources/:id", adminAuth, resourceHandler.Update)
adminAPI.DELETE("/resources/:id", adminAuth, resourceHandler.Delete)
```

## Logging Guidance

Admin flows should log:

- who performed the action
- what resource was read or changed
- status transitions
- destructive side effects

Avoid logging:

- raw secrets
- full request bodies for sensitive forms
- large unbounded snapshots

## When To Split Further

Split admin code into more packages or services only when:

- modules become large enough to deserve separate internal packages
- admin traffic and worker orchestration need stronger isolation
- the admin system evolves into a separate product

Do not over-fragment too early; the value of this blueprint is the predictable module pattern.
