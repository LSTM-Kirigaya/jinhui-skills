---
name: ddd-go-backend-project-structure
description: Standard directory layout for DDD Go backend projects. Covers cmd/, internal/, pkg/, migrations/, deployment/, and the purpose of each directory.
---

# Project Structure

## Full Directory Tree

```
project/
├── .air.toml                     # Air live-reload config
├── .github/workflows/
│   ├── build-binaries.yml
│   ├── build-docker-and-push.yml
│   └── test.yml
├── Dockerfile
├── go.mod
├── go.sum
├── config-example.yaml           # Annotated example config (committed)
├── config.yaml                   # Active config (gitignored)
├── cmd/
│   ├── server/main.go            # HTTP server entry point
│   └── <cli-tool>/main.go        # CLI tools (e.g., create-admin)
├── internal/
│   ├── common/
│   │   ├── domain/base.go        # Base entity (UUID, timestamps, soft delete)
│   │   ├── errors/errors.go      # AppError type + error code constants
│   │   └── response/response.go  # Unified JSON response helpers
│   ├── auth/                     # Authentication & user management
│   │   ├── bootstrap.go          # Startup logic (e.g., promote admin)
│   │   ├── middleware.go         # JWT, admin, banned-user middlewares
│   │   ├── domain/               # User, UserRole, OAuthAccount, RefreshToken
│   │   ├── handler/              # Auth HTTP handlers
│   │   ├── repo/                 # User, token, OAuth repos
│   │   └── service/              # Auth + OAuth services
│   ├── <module>/
│   │   ├── domain/               # Entity structs + business methods
│   │   ├── handler/              # HTTP handlers + RegisterRoutes
│   │   ├── repo/                 # GORM data access
│   │   └── service/              # Business logic
│   └── ...
├── pkg/
│   ├── config/config.go          # Viper config loading
│   ├── database/
│   │   ├── mysql.go              # GORM MySQL init + auto-migrate
│   │   └── postgres.go           # GORM PostgreSQL init (alternative)
│   ├── logger/logger.go          # Zap structured logger
│   ├── redis/redis.go            # Redis client init
│   ├── storage/storage.go        # S3/MinIO client init
│   └── trace/otel.go             # OpenTelemetry OTLP tracing init
├── migrations/                   # Raw SQL migrations for production
│   └── YYYYMMDD_description.sql
├── deployment/
│   ├── k8s/base/                 # K8s deployment + service + kustomization
│   ├── k8s/opentelemetry/        # Jaeger + OTel Collector manifests
│   └── nginx/                    # Reverse proxy config
└── docs/                         # API docs, auth flow, deployment guides
```

## Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `cmd/` | Entry points. One subdirectory per binary. `server/` is the main HTTP server. |
| `internal/` | Application code. Not importable by external modules. |
| `internal/common/` | Shared domain primitives, error types, response helpers. No business logic. |
| `internal/<module>/domain/` | Entity definitions with business methods. Pure Go structs. |
| `internal/<module>/repo/` | Data access. Wraps `*gorm.DB`. Returns domain entities. |
| `internal/<module>/service/` | Business logic. Depends on repos and other services. |
| `internal/<module>/handler/` | HTTP layer. Parses requests, calls service, formats responses. |
| `pkg/` | Shared infrastructure. Importable by external modules (though rarely needed). |
| `migrations/` | Raw SQL files for production schema changes. Named `YYYYMMDD_description.sql`. |
| `deployment/` | Kubernetes manifests, observability stack, reverse proxy configs. |
| `docs/` | Project documentation. |

## Internal Module Checklist

When creating a new module `<name>`, create these files:

```
internal/<name>/
├── domain/<name>.go           # Primary entity + related value objects
├── handler/<name>_handler.go  # HTTP handlers + RegisterRoutes method
├── repo/<name>_repo.go        # GORM repository
└── service/<name>_service.go  # Business logic service
```

## go.mod Dependencies

Core dependencies for a new project:

```
go mod init github.com/yourorg/yourproject

# HTTP framework
go get github.com/gin-gonic/gin

# ORM + drivers
go get gorm.io/gorm
go get gorm.io/driver/mysql
go get gorm.io/driver/postgres

# Config
go get github.com/spf13/viper

# Auth
go get github.com/golang-jwt/jwt/v5
go get golang.org/x/oauth2
go get golang.org/x/crypto

# Redis
go get github.com/redis/go-redis/v9

# Observability
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc
go get go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin
go get go.uber.org/zap

# Utilities
go get github.com/google/uuid
```
