---
name: ddd-go-backend
description: |
  Build production-ready Go backend services following DDD-layered architecture.
  Covers project scaffolding, config (Viper), database (GORM + MySQL/PostgreSQL),
  object storage (S3/MinIO), OAuth2 + JWT auth, OpenTelemetry tracing + Jaeger
  visualization, Zap logging, middleware patterns, and API routing. Use when
  creating a new Go backend service or adding features to an existing one that
  follows this architecture.
tags: ["go", "backend", "ddd", "gorm", "gin", "opentelemetry", "jwt", "oauth2"]
model: deepseek-chat
rootUrl: file:///Users/kirigaya/project/jinhui-skills/skills/ddd-go-backend/SKILL.md
examples:
  - 帮我通过重构文档和 ddd-go-backend 这个 skill 重新搭建一个新的 go 项目
  - 用这个 skill 给我的项目加一个用户管理模块，需要注册、登录、个人信息 CRUD
  - 给现有 Go 服务加上 OpenTelemetry 链路追踪和 Jaeger 可视化
---

# DDD Go Backend Service

Build production-ready Go backend services following a DDD-layered architecture with OpenTelemetry observability, OAuth2 authentication, and GORM-based persistence.

## Quick Start

### 1. Scaffold the project

Follow the [project structure](./project-structure/PROJECT_STRUCTURE.md) to create the directory layout.

### 2. Initialize Go module

```bash
go mod init github.com/yourorg/yourproject
```

### 3. Wire up the core infrastructure

See the individual guides below, in order:

1. [Config](./config/CONFIG.md) — Viper-based YAML configuration
2. [Database](./database/DATABASE.md) — GORM with MySQL/PostgreSQL
3. [Storage](./storage/STORAGE.md) — S3/MinIO object storage
4. [Auth](./auth/AUTH.md) — JWT + OAuth2 multi-provider auth
5. [Observability](./observability/OBSERVABILITY.md) — OTel tracing + Jaeger + Zap
6. [Architecture](./architecture/ARCHITECTURE.md) — DDD layering (domain → repo → service → handler)
7. [Middleware](./middleware/MIDDLEWARE.md) — Gin middleware stack
8. [API](./api/API.md) — Route registration, request/response format, error handling

---

## Directory Map

```
project/
├── cmd/server/main.go          # Entry point + manual DI wiring
├── internal/
│   ├── common/                 # Base entity, errors, response helpers
│   ├── <module>/
│   │   ├── domain/             # Entity structs + business methods
│   │   ├── repo/               # Data access (GORM queries)
│   │   ├── service/            # Business logic
│   │   └── handler/            # HTTP handlers + route registration
│   └── ...
├── pkg/
│   ├── config/                 # Viper config loader
│   ├── database/               # GORM MySQL/PostgreSQL init
│   ├── logger/                 # Zap structured logger
│   ├── redis/                  # Redis client init
│   ├── storage/                # S3/MinIO client init
│   └── trace/                  # OpenTelemetry OTLP init
├── migrations/                 # Raw SQL migrations for production
├── deployment/                 # K8s manifests, observability stack
└── config.yaml                 # Runtime config (gitignored)
```

## Typical Workflow: Adding a New Module

1. Define domain entities in `internal/<module>/domain/`
2. Write repo in `internal/<module>/repo/` (GORM queries)
3. Write service in `internal/<module>/service/` (business logic, calls repo)
4. Write handler in `internal/<module>/handler/` (parse request → call service → respond)
5. Register routes in handler's `RegisterRoutes(r *gin.RouterGroup)` method
6. Wire everything in `cmd/server/main.go`: create repo → create service → create handler → register routes

## Usage Examples

See the `examples` field in the frontmatter above.

## Key Conventions

- **Concrete types**, not interfaces — repos and services are structs
- **Manual DI** — all wiring in `main.go`, no wire/dig framework
- **Unified response format**: `{ "code": 0, "message": "ok", "data": {...} }` — code 0 = success
- **AppError**: custom error type with numeric Code, Message, HTTPStatus
- **Error code ranges**: 10000=generic, 20000=auth, 30000=subscription, 40000=admin
- **GORM AutoMigrate** for dev, **raw SQL migrations** in `migrations/` for production
- **No ORM in domain** — domain entities use plain structs; DB mapping lives in repo layer
