---
name: ddd-go-backend-api
description: HTTP API routing and handler patterns for Go backend services. Covers route registration, unified request/response format, error handling with AppError, handler implementation template, and routing structure.
---

# API: Routing & Handler Patterns

## Route Registration Pattern

Each handler defines a `RegisterRoutes(*gin.RouterGroup)` method. The caller decides the prefix:

```go
// internal/project/handler/project_handler.go
func (h *ProjectHandler) RegisterRoutes(r *gin.RouterGroup) {
    r.POST("", h.Create)
    r.GET("", h.List)
    r.GET("/:id", h.Get)
    r.PUT("/:id", h.Update)
    r.DELETE("/:id", h.Delete)
}
```

### Wiring in main.go

```go
api := r.Group("/api/v1")

projectHandler := projecthandler.NewProjectHandler(projectService)
projectHandler.RegisterRoutes(api.Group("/projects"))
// Results in: POST /api/v1/projects, GET /api/v1/projects, etc.
```

## Route Structure Example

```
Public (no JWT):
  POST   /api/v1/auth/register
  POST   /api/v1/auth/login
  POST   /api/v1/auth/refresh
  GET    /api/v1/auth/oauth/:provider
  GET    /api/v1/auth/oauth/:provider/callback
  POST   /api/v1/billing/webhooks/payment

Authenticated (JWT required):
  POST   /api/v1/projects
  GET    /api/v1/projects
  GET    /api/v1/projects/:id
  PUT    /api/v1/projects/:id
  DELETE /api/v1/projects/:id

Admin only (JWT + admin role):
  GET    /api/v1/admin/users
  POST   /api/v1/admin/users/:userId/ban
```

## Unified Response Format

All responses use the same envelope:

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

- `code: 0` — success
- `code: non-zero` — specific error (see error code ranges)

### Response Helpers (`internal/common/response/response.go`)

```go
package response

import (
    "errors"
    "net/http"

    "github.com/gin-gonic/gin"
    commonerrors "github.com/yourorg/yourproject/internal/common/errors"
)

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, gin.H{
        "code":    0,
        "message": "ok",
        "data":    data,
    })
}

func Created(c *gin.Context, data interface{}) {
    c.JSON(http.StatusCreated, gin.H{
        "code":    0,
        "message": "created",
        "data":    data,
    })
}

func Error(c *gin.Context, err error) {
    var appErr *commonerrors.AppError
    if errors.As(err, &appErr) {
        c.JSON(appErr.HTTPStatus, gin.H{
            "code":    appErr.Code,
            "message": appErr.Message,
        })
        return
    }
    // Unknown error → 500
    c.JSON(http.StatusInternalServerError, gin.H{
        "code":    10000,
        "message": "internal server error",
    })
}
```

## Error Handling (`internal/common/errors/errors.go`)

```go
package errors

import "net/http"

type AppError struct {
    Code       int
    Message    string
    HTTPStatus int
}

func (e *AppError) Error() string {
    return e.Message
}

// Generic errors (10xxx)
var (
    ErrInternal     = &AppError{10000, "internal server error", http.StatusInternalServerError}
    ErrNotFound     = &AppError{10001, "resource not found", http.StatusNotFound}
    ErrBadRequest   = &AppError{10002, "bad request", http.StatusBadRequest}
    ErrConflict     = &AppError{10003, "resource already exists", http.StatusConflict}
)

// Auth errors (20xxx)
var (
    ErrInvalidCredentials  = &AppError{20001, "invalid credentials", http.StatusUnauthorized}
    ErrTokenExpired        = &AppError{20002, "token expired", http.StatusUnauthorized}
    ErrInvalidRefreshToken = &AppError{20003, "invalid refresh token", http.StatusUnauthorized}
    ErrUserBanned          = &AppError{40002, "user is banned", http.StatusForbidden}
    ErrAdminRequired       = &AppError{40001, "admin access required", http.StatusForbidden}
)

// Subscription errors (30xxx)
var (
    ErrQuotaExceeded   = &AppError{30001, "quota exceeded", http.StatusForbidden}
    ErrPaymentRequired = &AppError{30002, "payment required", http.StatusPaymentRequired}
)
```

## Handler Template

```go
package handler

import (
    "github.com/gin-gonic/gin"
    "github.com/yourorg/yourproject/internal/common/response"
    "github.com/yourorg/yourproject/internal/<module>/service"
)

type Handler struct {
    service *service.Service
}

func NewHandler(svc *service.Service) *Handler {
    return &Handler{service: svc}
}

func (h *Handler) RegisterRoutes(r *gin.RouterGroup) {
    r.POST("", h.Create)
    r.GET("", h.List)
    r.GET("/:id", h.Get)
    r.PUT("/:id", h.Update)
    r.DELETE("/:id", h.Delete)
}

// Create
func (h *Handler) Create(c *gin.Context) {
    var input service.CreateInput
    if err := c.ShouldBindJSON(&input); err != nil {
        response.Error(c, commonerrors.ErrBadRequest)
        return
    }

    result, err := h.service.Create(c.Request.Context(), input)
    if err != nil {
        response.Error(c, err)
        return
    }
    response.Created(c, result)
}

// Get
func (h *Handler) Get(c *gin.Context) {
    id := c.Param("id")
    result, err := h.service.FindByID(c.Request.Context(), id)
    if err != nil {
        response.Error(c, err)
        return
    }
    response.Success(c, result)
}

// List
func (h *Handler) List(c *gin.Context) {
    // Parse pagination from query params
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

    results, total, err := h.service.List(c.Request.Context(), page, pageSize)
    if err != nil {
        response.Error(c, err)
        return
    }
    response.Success(c, gin.H{
        "items":     results,
        "total":     total,
        "page":      page,
        "page_size": pageSize,
    })
}

// Update
func (h *Handler) Update(c *gin.Context) {
    id := c.Param("id")
    var input service.UpdateInput
    if err := c.ShouldBindJSON(&input); err != nil {
        response.Error(c, commonerrors.ErrBadRequest)
        return
    }

    result, err := h.service.Update(c.Request.Context(), id, input)
    if err != nil {
        response.Error(c, err)
        return
    }
    response.Success(c, result)
}

// Delete
func (h *Handler) Delete(c *gin.Context) {
    id := c.Param("id")
    if err := h.service.Delete(c.Request.Context(), id); err != nil {
        response.Error(c, err)
        return
    }
    response.Success(c, nil)
}
```

## Handler Design Rules

1. **Thin handlers** — no business logic; only parse request, call service, format response
2. **Context propagation** — always pass `c.Request.Context()` to service methods
3. **Use response helpers** — `response.Success`, `response.Created`, `response.Error` for consistency
4. **Error type assertion** — services return `*AppError`, handlers pass them to `response.Error` which checks with `errors.As`
5. **Validation** — use Gin's `ShouldBindJSON` with struct tags; return `ErrBadRequest` on failure
6. **Route params** — use `c.Param("id")` for path params, `c.Query("key")` for query params, `c.DefaultQuery("key", "default")` for optional
7. **No context keys for business data** — the handler shouldn't directly read `c.Get("user_id")`; the service should receive the user ID as a parameter from the handler
