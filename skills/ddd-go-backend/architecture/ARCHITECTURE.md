---
name: ddd-go-backend-architecture
description: DDD-layered architecture for Go backend services: domain, repo, service, handler layers with manual DI. Covers the composition root pattern, cross-module dependencies, and the common module.
---

# Architecture: DDD Layered Design

## Layer Overview

```
┌──────────────────────────────────────────────────┐
│  cmd/server/main.go                              │
│  Composition root — manual dependency injection   │
├──────────────────────────────────────────────────┤
│  internal/<module>/handler/                       │
│  HTTP layer — parse request, call service,        │
│  format JSON response                             │
├──────────────────────────────────────────────────┤
│  internal/<module>/service/                       │
│  Business logic layer — orchestrates repos,       │
│  enforces invariants, returns domain objects      │
├──────────────────────────────────────────────────┤
│  internal/<module>/repo/                          │
│  Data access layer — GORM queries, wraps *gorm.DB │
├──────────────────────────────────────────────────┤
│  internal/<module>/domain/                        │
│  Entity structs, value objects, business methods  │
├──────────────────────────────────────────────────┤
│  pkg/                                             │
│  Shared infrastructure — config, database, trace, │
│  logger, redis, storage                           │
└──────────────────────────────────────────────────┘
```

## Layer Responsibilities

### domain/

Entity structs with **business methods**, not anemic models. Use plain Go structs — no GORM tags here.

```go
// internal/project/domain/project.go
type Project struct {
    common.Base              // UUID, CreatedAt, UpdatedAt, DeletedAt
    Name        string
    Description string
    OwnerID     string
}

// Business method on the entity
func (p *Project) IsOwner(userID string) bool {
    return p.OwnerID == userID
}
```

### repo/

Wraps `*gorm.DB`. Every query uses `db.WithContext(ctx)` for trace propagation. Returns domain entities.

```go
// internal/project/repo/project_repo.go
type ProjectRepository struct {
    db *gorm.DB
}

func NewProjectRepository(db *gorm.DB) *ProjectRepository {
    return &ProjectRepository{db: db}
}

func (r *ProjectRepository) FindByID(ctx context.Context, id string) (*domain.Project, error) {
    var project domain.Project
    err := r.db.WithContext(ctx).Where("id = ?", id).First(&project).Error
    if errors.Is(err, gorm.ErrRecordNotFound) {
        return nil, commonerrors.ErrNotFound
    }
    return &project, err
}
```

### service/

Holds references to repos (and other services) via struct fields. Contains all business logic.

```go
// internal/project/service/project_service.go
type ProjectService struct {
    projectRepo *repo.ProjectRepository
    memberRepo  *repo.ProjectMemberRepository
    subService  *subscription.Service  // cross-module dependency
}

func NewProjectService(
    projectRepo *repo.ProjectRepository,
    memberRepo *repo.ProjectMemberRepository,
    subService *subscription.Service,
) *ProjectService {
    return &ProjectService{
        projectRepo: projectRepo,
        memberRepo:  memberRepo,
        subService:  subService,
    }
}
```

### handler/

Receives HTTP requests, calls the service, formats the unified response. Also defines route registration.

```go
// internal/project/handler/project_handler.go
type ProjectHandler struct {
    service *service.ProjectService
}

func NewProjectHandler(service *service.ProjectService) *ProjectHandler {
    return &ProjectHandler{service: service}
}

func (h *ProjectHandler) RegisterRoutes(r *gin.RouterGroup) {
    r.POST("", h.Create)
    r.GET("", h.List)
    r.GET("/:id", h.Get)
    r.PUT("/:id", h.Update)
    r.DELETE("/:id", h.Delete)
}
```

## Composition Root (main.go)

All wiring is manual — no DI framework. The pattern:

```go
func NewApp(configPath string) *App {
    cfg := config.Load(configPath)

    // 1. Infrastructure
    db := database.InitMySQL(cfg.Database, cfg.App.Env)
    redisClient := redis.InitRedis(cfg.Redis)

    // 2. Repos
    userRepo := authrepo.NewUserRepository(db)
    tokenRepo := authrepo.NewTokenRepository(db)

    // 3. Services
    authService := authsvc.NewAuthService(userRepo, tokenRepo, cfg.JWT)
    projectService := projectsvc.NewProjectService(projectRepo, memberRepo, subService)

    // 4. Handlers
    authHandler := authhandler.NewAuthHandler(authService)
    projectHandler := projecthandler.NewProjectHandler(projectService)

    // 5. Router + middleware
    r := gin.New()
    r.Use(gin.Logger(), gin.Recovery())
    api := r.Group("/api/v1")
    api.Use(middleware.NewJWTAuthMiddleware(cfg.JWT.Secret, publicPaths))

    // 6. Register routes
    authHandler.RegisterRoutes(api.Group("/auth"))
    projectHandler.RegisterRoutes(api.Group("/projects"))

    return &App{engine: r, db: db}
}
```

## Common Module (`internal/common/`)

Shared across all modules:

```go
// domain/base.go — embedded in every entity
type Base struct {
    ID        string         `gorm:"primaryKey;size:36"`
    CreatedAt time.Time      `gorm:"autoCreateTime"`
    UpdatedAt time.Time      `gorm:"autoUpdateTime"`
    DeletedAt gorm.DeletedAt `gorm:"index"`  // soft delete
}

// errors/errors.go
type AppError struct {
    Code       int
    Message    string
    HTTPStatus int
}

func (e *AppError) Error() string { return e.Message }

// response/response.go
func Success(c *gin.Context, data interface{}) {
    c.JSON(200, gin.H{"code": 0, "message": "ok", "data": data})
}

func Error(c *gin.Context, err error) {
    var appErr *AppError
    if errors.As(err, &appErr) {
        c.JSON(appErr.HTTPStatus, gin.H{"code": appErr.Code, "message": appErr.Message})
        return
    }
    c.JSON(500, gin.H{"code": 10000, "message": "internal server error"})
}
```

## Error Code Ranges

| Range | Domain |
|-------|--------|
| 0 | Success |
| 10000–19999 | Generic / internal |
| 20000–29999 | Auth (bad credentials, token expired, banned) |
| 30000–39999 | Subscription / billing |
| 40000–49999 | Admin / user status |

## Key Design Decisions

1. **Concrete types over interfaces** — Simpler wiring, no mock generation needed for tests (use real DB in test containers or SQLite in-memory)
2. **Manual DI** — All dependencies visible in one place (`main.go`); easy to trace initialization order
3. **No ORM in domain** — Domain types are plain structs; DB mapping via GORM tags on repo-layer models (or use separate DB models if mapping differs)
4. **Service references services** — Cross-module calls go through service structs, not repos directly
