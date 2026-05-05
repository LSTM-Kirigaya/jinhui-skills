---
name: ddd-go-backend-config
description: Viper-based YAML configuration with environment variable override. Covers the Config struct, all sub-configs (App, Database, Redis, JWT, OAuth, OTel, Subscription), defaults, and the Load function.
---

# Config: Viper-based YAML Configuration

## Overview

Configuration is managed by [Viper](https://github.com/spf13/viper), loaded from a YAML file with automatic environment variable override.

## File: `pkg/config/config.go`

```go
package config

import (
    "github.com/spf13/viper"
)

type Config struct {
    App          AppConfig          `mapstructure:"app"`
    Database     DatabaseConfig     `mapstructure:"database"`
    Redis        RedisConfig        `mapstructure:"redis"`
    JWT          JWTConfig          `mapstructure:"jwt"`
    OAuth        OAuthConfig        `mapstructure:"oauth"`
    OTel         OTelConfig         `mapstructure:"otel"`
    Storage      StorageConfig      `mapstructure:"storage"`
    Subscription SubscriptionConfig `mapstructure:"subscription"`
}

// --- Sub-configs ---

type AppConfig struct {
    Name                string `mapstructure:"name"`
    Env                 string `mapstructure:"env"` // "development" | "production"
    Port                int    `mapstructure:"port"`
    BootstrapAdminEmail string `mapstructure:"bootstrap_admin_email"`
}

type DatabaseConfig struct {
    Driver   string `mapstructure:"driver"` // "mysql" | "postgres"
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Name     string `mapstructure:"name"`
    User     string `mapstructure:"user"`
    Password string `mapstructure:"password"`
}

type RedisConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Password string `mapstructure:"password"`
    DB       int    `mapstructure:"db"`
}

type JWTConfig struct {
    Secret          string `mapstructure:"secret"`
    AccessTokenTTL  int    `mapstructure:"access_token_ttl"`  // seconds
    RefreshTokenTTL int    `mapstructure:"refresh_token_ttl"` // seconds
}

type OAuthConfig struct {
    Github GithubOAuthConfig  `mapstructure:"github"`
    Watcha WatchaOAuthConfig  `mapstructure:"watcha"`
}

type GithubOAuthConfig struct {
    ClientID       string `mapstructure:"client_id"`
    ClientSecret   string `mapstructure:"client_secret"`
    RedirectURL    string `mapstructure:"redirect_url"`
    AppID          string `mapstructure:"app_id"`           // GitHub App ID (optional)
    PrivateKeyPath string `mapstructure:"private_key_path"` // GitHub App private key (optional)
}

type WatchaOAuthConfig struct {
    Clients []WatchaOAuthClient `mapstructure:"clients"`
}

type WatchaOAuthClient struct {
    ClientID     string `mapstructure:"client_id"`
    ClientSecret string `mapstructure:"client_secret"`
    RedirectURL  string `mapstructure:"redirect_url"`
    MatchHost    string `mapstructure:"match_host"` // route by request host
}

type OTelConfig struct {
    Enabled           bool   `mapstructure:"enabled"`
    CollectorEndpoint string `mapstructure:"collector_endpoint"`
    Token             string `mapstructure:"token"`
    HostName          string `mapstructure:"host_name"`
    Insecure          bool   `mapstructure:"insecure"`
}

type StorageConfig struct {
    Endpoint  string `mapstructure:"endpoint"`
    AccessKey string `mapstructure:"access_key"`
    SecretKey string `mapstructure:"secret_key"`
    Bucket    string `mapstructure:"bucket"`
    UseSSL    bool   `mapstructure:"use_ssl"`
    Region    string `mapstructure:"region"`
}

type SubscriptionConfig struct {
    AdminAPIKey   string       `mapstructure:"admin_api_key"`
    WebhookSecret string       `mapstructure:"webhook_secret"`
    Plans         []PlanConfig `mapstructure:"plans"`
}

type PlanConfig struct {
    Code            string  `mapstructure:"code"`
    Name            string  `mapstructure:"name"`
    Sort            int     `mapstructure:"sort"`
    ProjectLimit    int     `mapstructure:"project_limit"`
    SpecCaseLimit   int     `mapstructure:"spec_case_limit"`
    PriceMonthly    float64 `mapstructure:"price_monthly"`
    PriceYearly     float64 `mapstructure:"price_yearly"`
}
```

## Load Function

```go
func Load(configPath string) *Config {
    v := viper.New()
    v.SetConfigFile(configPath)
    v.SetConfigType("yaml")

    // Set defaults
    v.SetDefault("app.port", 8080)
    v.SetDefault("app.env", "development")
    v.SetDefault("otel.enabled", false)
    v.SetDefault("otel.insecure", true)
    v.SetDefault("database.driver", "mysql")
    v.SetDefault("database.port", 3306)
    v.SetDefault("redis.port", 6379)
    v.SetDefault("redis.db", 0)
    v.SetDefault("jwt.access_token_ttl", 3600)
    v.SetDefault("jwt.refresh_token_ttl", 604800)
    v.SetDefault("storage.use_ssl", true)

    // Environment variable override
    v.AutomaticEnv()

    if err := v.ReadInConfig(); err != nil {
        panic(fmt.Errorf("failed to read config: %w", err))
    }

    var cfg Config
    if err := v.Unmarshal(&cfg); err != nil {
        panic(fmt.Errorf("failed to unmarshal config: %w", err))
    }

    return &cfg
}
```

## Example YAML (`config-example.yaml`)

This file is committed to the repo. The active `config.yaml` is gitignored.

```yaml
app:
  name: "my-service"
  env: "development"       # "development" | "production"
  port: 8080
  bootstrap_admin_email: "admin@example.com"

database:
  driver: "mysql"
  host: "127.0.0.1"
  port: 3306
  name: "myapp"
  user: "root"
  password: ""

redis:
  host: "127.0.0.1"
  port: 6379
  password: ""
  db: 0

jwt:
  secret: "your-secret-key-change-in-production"
  access_token_ttl: 3600       # 1 hour
  refresh_token_ttl: 604800    # 7 days

oauth:
  github:
    client_id: ""
    client_secret: ""
    redirect_url: "https://example.com/api/v1/auth/oauth/github/callback"

otel:
  enabled: false
  collector_endpoint: "localhost:4317"
  token: ""
  host_name: "my-service-1"
  insecure: true

storage:
  endpoint: "s3.amazonaws.com"
  access_key: ""
  secret_key: ""
  bucket: "myapp-uploads"
  use_ssl: true
  region: "us-east-1"

subscription:
  admin_api_key: ""
  webhook_secret: ""
  plans:
    - code: "free"
      name: "Free"
      sort: 0
      project_limit: 3
      spec_case_limit: 10
      price_monthly: 0
      price_yearly: 0
    - code: "pro"
      name: "Pro"
      sort: 1
      project_limit: 20
      spec_case_limit: 100
      price_monthly: 9.99
      price_yearly: 99.99
```

## Environment Variable Override

Any config key can be overridden via environment variables. Viper's `AutomaticEnv()` maps them automatically:

```bash
export APP_PORT=9090
export DATABASE_HOST=prod-db.example.com
export JWT_SECRET=super-secret-key
export OTEL_ENABLED=true
export OTEL_COLLECTOR_ENDPOINT=otel-collector:4317
```

Nested keys use underscores (not dots) when set via env vars, depending on your Viper configuration. For explicit mapping, use `v.BindEnv()` or set `v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))`.

## Usage in main.go

```go
func NewApp(configPath string) *App {
    cfg := config.Load(configPath)

    // Set Gin mode from config
    if cfg.App.Env == "production" {
        gin.SetMode(gin.ReleaseMode)
    }

    // Use config values
    db := database.InitMySQL(cfg.Database, cfg.App.Env)
    otelShutdown := trace.InitOTel(cfg.OTel, cfg.App.Name)
    defer otelShutdown()

    // ...
}
```
