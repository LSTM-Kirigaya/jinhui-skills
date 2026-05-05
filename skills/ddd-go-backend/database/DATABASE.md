---
name: ddd-go-backend-database
description: GORM-based database setup for MySQL and PostgreSQL. Covers connection init, auto-migration for dev, raw SQL migrations for production, repo patterns, and Redis client init.
---

# Database: GORM + MySQL/PostgreSQL

## MySQL Initialization (`pkg/database/mysql.go`)

```go
package database

import (
    "fmt"
    "log"
    "time"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

func InitMySQL(cfg DatabaseConfig, env string) *gorm.DB {
    dsn := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=utf8mb4&parseTime=True&loc=Local",
        cfg.User, cfg.Password, cfg.Host, cfg.Port, cfg.Name,
    )

    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Warn),
    })
    if err != nil {
        panic(fmt.Errorf("failed to connect to MySQL: %w", err))
    }

    // Auto-migrate for development only
    if env != "production" {
        autoMigrate(db)
    }

    return db
}
```

## PostgreSQL Alternative (`pkg/database/postgres.go`)

Same pattern, different driver:

```go
import "gorm.io/driver/postgres"

func InitPostgres(cfg DatabaseConfig, env string) *gorm.DB {
    dsn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
        cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.Name,
    )

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Warn),
    })
    if err != nil {
        panic(fmt.Errorf("failed to connect to PostgreSQL: %w", err))
    }

    if env != "production" {
        autoMigrate(db)
    }

    return db
}
```

## Auto-Migration (Development Only)

In production, use explicit SQL migrations. In development, use GORM AutoMigrate:

```go
func autoMigrate(db *gorm.DB) {
    models := []interface{}{
        &domain.User{},
        &domain.RefreshToken{},
        &domain.OAuthAccount{},
        &domain.OAuthNonce{},
        &domain.Project{},
        &domain.ProjectMember{},
        &domain.ProjectInvite{},
        &domain.SpecCase{},
        &domain.BatchValidationCase{},
        &domain.Plan{},
        &domain.UserSubscription{},
        &domain.PaymentOrder{},
        &domain.Announcement{},
    }

    for _, model := range models {
        log.Printf("Migrating %T...", model)
        err := migrateWithRetry(db, model, 3, 120*time.Second)
        if err != nil {
            log.Printf("WARNING: failed to migrate %T: %v", model, err)
        }
    }
}

func migrateWithRetry(db *gorm.DB, model interface{}, retries int, timeout time.Duration) error {
    for i := 0; i < retries; i++ {
        ctx, cancel := context.WithTimeout(context.Background(), timeout)
        err := db.WithContext(ctx).AutoMigrate(model)
        cancel()
        if err == nil {
            return nil
        }
        if errors.Is(err, context.DeadlineExceeded) {
            log.Printf("Timeout migrating %T, retry %d/%d", model, i+1, retries)
            continue
        }
        return err
    }
    return fmt.Errorf("failed after %d retries", retries)
}
```

## Base Entity

Embed `Base` in every domain entity for consistent ID, timestamps, and soft delete:

```go
// internal/common/domain/base.go
type Base struct {
    ID        string         `gorm:"primaryKey;size:36"`
    CreatedAt time.Time      `gorm:"autoCreateTime"`
    UpdatedAt time.Time      `gorm:"autoUpdateTime"`
    DeletedAt gorm.DeletedAt `gorm:"index"`
}
```

Generate UUID before create:

```go
func (b *Base) BeforeCreate(tx *gorm.DB) error {
    if b.ID == "" {
        b.ID = uuid.New().String()
    }
    return nil
}
```

## Repository Pattern

Every repo wraps `*gorm.DB` and always uses `db.WithContext(ctx)`:

```go
type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) FindByEmail(ctx context.Context, email string) (*domain.User, error) {
    var user domain.User
    err := r.db.WithContext(ctx).
        Where("email = ?", email).
        First(&user).Error
    if errors.Is(err, gorm.ErrRecordNotFound) {
        return nil, commonerrors.ErrNotFound
    }
    return &user, err
}

func (r *UserRepository) Create(ctx context.Context, user *domain.User) error {
    return r.db.WithContext(ctx).Create(user).Error
}

func (r *UserRepository) Update(ctx context.Context, user *domain.User) error {
    return r.db.WithContext(ctx).Save(user).Error
}

func (r *UserRepository) SoftDelete(ctx context.Context, id string) error {
    return r.db.WithContext(ctx).Delete(&domain.User{}, "id = ?", id).Error
}
```

## Production Migrations

Raw SQL files in `migrations/`, named `YYYYMMDD_description.sql`:

```sql
-- migrations/20260505_create_announcements.sql
CREATE TABLE IF NOT EXISTS announcements (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME DEFAULT NULL,
    INDEX idx_slug (slug),
    INDEX idx_deleted_at (deleted_at)
);
```

## Redis Client (`pkg/redis/redis.go`)

```go
package redis

import (
    "context"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
)

func InitRedis(cfg RedisConfig) *redis.Client {
    client := redis.NewClient(&redis.Options{
        Addr:     fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
        Password: cfg.Password,
        DB:       cfg.DB,
    })

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := client.Ping(ctx).Err(); err != nil {
        panic(fmt.Errorf("failed to connect to Redis: %w", err))
    }

    return client
}
```

## Database Driver Selection

In `main.go`, select the driver based on config:

```go
var db *gorm.DB
switch cfg.Database.Driver {
case "postgres":
    db = database.InitPostgres(cfg.Database, cfg.App.Env)
default:
    db = database.InitMySQL(cfg.Database, cfg.App.Env)
}
```
