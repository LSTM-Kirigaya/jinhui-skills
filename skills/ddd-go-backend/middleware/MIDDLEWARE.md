---
name: ddd-go-backend-middleware
description: Gin middleware patterns for Go backend services. Covers the middleware stack order, JWT auth, admin role check, banned user check, OpenTelemetry tracing, and how to compose them into route groups.
---

# Middleware: Gin Middleware Stack

## Middleware Order

The order matters — early middleware runs first (pre-request) and last (post-response):

```
Request
  │
  ▼
1. gin.Logger()          — Logs every request start/end
2. gin.Recovery()        — Catches panics, returns 500
3. otelgin.Middleware()   — Creates OpenTelemetry span per request
4. Trace ID middleware    — Injects X-Trace-Id response header
5. JWT auth middleware    — Validates token, injects user claims
6. Banned user middleware — Blocks banned users
7. Admin middleware       — (per-route-group) Requires admin role
  │
  ▼
Handler
```

## Composition in main.go

```go
func NewApp(cfg *config.Config) *App {
    r := gin.New()

    // Global middleware (applies to all routes)
    r.Use(gin.Logger())
    r.Use(gin.Recovery())

    if cfg.OTel.Enabled {
        r.Use(otelgin.Middleware(cfg.App.Name))
        r.Use(traceIDResponseMiddleware())
    }

    // API group
    api := r.Group("/api/v1")

    // Auth middleware on the API group
    api.Use(auth.NewJWTAuthMiddleware(cfg.JWT.Secret, publicPaths))
    api.Use(auth.NewBannedUserMiddleware(userRepo))

    // Register public routes
    authHandler.RegisterRoutes(api.Group("/auth"))

    // Admin routes — add admin middleware on top
    adminGroup := api.Group("/admin")
    adminGroup.Use(auth.NewRequireAdminMiddleware(userRepo))
    adminHandler.RegisterRoutes(adminGroup)

    return &App{engine: r}
}
```

## JWT Auth Middleware

Constructor pattern: `NewJWTAuthMiddleware(secret, publicPaths)`

```go
func NewJWTAuthMiddleware(secret string, publicPaths []string) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 1. Skip public paths
        if isPublicPath(c.Request.URL.Path, publicPaths) {
            c.Next()
            return
        }

        // 2. Extract Bearer token
        tokenStr := extractBearerToken(c)

        // 3. Parse and validate JWT
        claims, err := parseJWT(tokenStr, secret)
        if err != nil {
            c.AbortWithStatusJSON(401, ...)
            return
        }

        // 4. Inject claims into context
        c.Set("user_id", claims.UserID)
        c.Set("email", claims.Email)
        c.Set("username", claims.Username)
        c.Set("role", claims.Role)
        c.Next()
    }
}
```

### Public Path Matching

Paths ending with `/` match by prefix:

```go
var publicPaths = []string{
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/oauth/",        // prefix match: all OAuth endpoints
    "/api/v1/auth/device/",       // prefix match: all device flow endpoints
    "/api/v1/billing/webhooks/",  // prefix match: all webhooks
}

func isPublicPath(path string, publicPaths []string) bool {
    for _, p := range publicPaths {
        if strings.HasSuffix(p, "/") {
            if strings.HasPrefix(path, p) {
                return true
            }
        } else {
            if path == p {
                return true
            }
        }
    }
    return false
}
```

## Banned User Middleware

Runs after JWT auth. Checks `banned_at` on the user record. Skips if no user ID in context (public endpoints).

```go
func NewBannedUserMiddleware(userRepo *UserRepository) gin.HandlerFunc {
    return func(c *gin.Context) {
        userID := GetUserIDFromContext(c)
        if userID == "" {
            c.Next()  // public endpoint, skip
            return
        }
        user, err := userRepo.FindByID(c.Request.Context(), userID)
        if err == nil && user.IsBanned() {
            c.AbortWithStatusJSON(403, gin.H{
                "code":    40002,
                "message": "user is banned",
            })
            return
        }
        c.Next()
    }
}
```

## Admin Middleware

Applied per-route-group. Validates role from DB (not just JWT claim) for security:

```go
func NewRequireAdminMiddleware(userRepo *UserRepository) gin.HandlerFunc {
    return func(c *gin.Context) {
        userID := GetUserIDFromContext(c)
        if userID == "" {
            c.AbortWithStatusJSON(401, ...)
            return
        }
        user, err := userRepo.FindByID(c.Request.Context(), userID)
        if err != nil || user.Role != "admin" {
            c.AbortWithStatusJSON(403, gin.H{
                "code":    40001,
                "message": "admin access required",
            })
            return
        }
        c.Next()
    }
}
```

## OpenTelemetry Middleware

```go
import "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"

// Creates a span per HTTP request with attributes: http.method, http.route, http.status_code
r.Use(otelgin.Middleware(serviceName))

// Custom middleware to expose trace ID to clients
func traceIDResponseMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        span := trace.SpanFromContext(c.Request.Context())
        if span.SpanContext().IsValid() {
            c.Header("X-Trace-Id", span.SpanContext().TraceID().String())
        }
    }
}
```

## Context Helper Functions

Define helpers to extract values injected by middleware:

```go
func GetUserIDFromContext(c *gin.Context) string {
    return c.GetString("user_id")
}

func GetUserEmailFromContext(c *gin.Context) string {
    return c.GetString("email")
}

func GetUsernameFromContext(c *gin.Context) string {
    return c.GetString("username")
}

func GetUserRoleFromContext(c *gin.Context) string {
    return c.GetString("role")
}
```

## Middleware Design Rules

1. **Constructor functions** — every middleware is returned by a `New*` function that takes dependencies
2. **Skip when possible** — don't abort for missing context if the route can work without it (e.g., banned check on public endpoints)
3. **Use `c.Set` / `c.Get`** — pass data between middlewares and handlers via Gin context
4. **DB re-check for sensitive operations** — admin middleware re-queries the DB rather than trusting the JWT role claim
5. **Group-level middleware** — use `group.Use()` for middleware that only applies to a subset of routes
