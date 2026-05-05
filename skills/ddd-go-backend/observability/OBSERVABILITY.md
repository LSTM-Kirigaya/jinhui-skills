---
name: ddd-go-backend-observability
description: OpenTelemetry tracing with OTLP gRPC exporter and Jaeger visualization. Covers OTel SDK init, Gin middleware integration, trace ID injection in response headers, Zap logger trace context enrichment, and Kubernetes deployment of Jaeger + OTel Collector.
---

# Observability: OpenTelemetry + Jaeger + Zap

## Architecture

```
Application (OTLP gRPC exporter)
    │
    ▼
OTel Collector (receives OTLP, batches, exports)
    │
    ▼
Jaeger (stores traces, serves UI on :16686)
```

- **OpenTelemetry SDK** — instrumentation inside the Go application (creates spans, exports via OTLP)
- **OpenTelemetry Collector** — middleware pipeline that receives, processes, and exports telemetry data
- **Jaeger** — trace storage and visualization UI

## OpenTelemetry Initialization (`pkg/trace/otel.go`)

```go
package trace

import (
    "context"
    "fmt"
    "log"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func InitOTel(cfg OTelConfig, serviceName string) func() {
    if !cfg.Enabled {
        log.Println("OpenTelemetry is disabled")
        return func() {}
    }

    ctx := context.Background()

    // Create OTLP gRPC exporter
    opts := []otlptracegrpc.Option{
        otlptracegrpc.WithEndpoint(cfg.CollectorEndpoint),
    }
    if cfg.Insecure {
        opts = append(opts, otlptracegrpc.WithInsecure())
    }

    exporter, err := otlptrace.New(ctx, otlptracegrpc.NewClient(opts...))
    if err != nil {
        panic(fmt.Errorf("failed to create OTLP exporter: %w", err))
    }

    // Build resource with service metadata
    attrs := []attribute.KeyValue{
        semconv.ServiceName(serviceName),
    }
    if cfg.HostName != "" {
        attrs = append(attrs, semconv.HostName(cfg.HostName))
    }
    if cfg.Token != "" {
        attrs = append(attrs, attribute.String("token", cfg.Token))
    }

    res, err := resource.New(ctx, resource.WithAttributes(attrs...))
    if err != nil {
        panic(fmt.Errorf("failed to create OTel resource: %w", err))
    }

    // Create TracerProvider with batch span processor
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()), // adjust for production
    )

    // Set global provider and propagator
    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.TraceContext{})

    log.Printf("OpenTelemetry initialized: endpoint=%s service=%s", cfg.CollectorEndpoint, serviceName)

    // Return shutdown function
    return func() {
        if err := tp.Shutdown(ctx); err != nil {
            log.Printf("OTel shutdown error: %v", err)
        }
    }
}
```

## Gin Middleware Integration

Use `otelgin` to automatically create spans for every HTTP request:

```go
import "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"

func NewApp(cfg *config.Config) *App {
    r := gin.New()

    if cfg.OTel.Enabled {
        r.Use(otelgin.Middleware(cfg.App.Name))
        // Inject X-Trace-Id response header
        r.Use(traceIDResponseMiddleware())
    }
    // ...
}
```

### Inject Trace ID in Response Headers

```go
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

## Zap Logger with Trace Context (`pkg/logger/logger.go`)

Enrich log entries with `trace_id` and `span_id` from the OpenTelemetry span context:

```go
package logger

import (
    "context"

    "go.opentelemetry.io/otel/trace"
    "go.uber.org/zap"
)

var logger *zap.Logger

func Init(env string) {
    var err error
    if env == "production" {
        logger, err = zap.NewProduction()
    } else {
        logger, err = zap.NewDevelopment()
    }
    if err != nil {
        panic(err)
    }
}

func L() *zap.Logger {
    return logger
}

// WithTrace adds trace_id and span_id from the context's current span.
func WithTrace(ctx context.Context) *zap.Logger {
    span := trace.SpanFromContext(ctx)
    if !span.SpanContext().IsValid() {
        return logger
    }
    return logger.With(
        zap.String("trace_id", span.SpanContext().TraceID().String()),
        zap.String("span_id", span.SpanContext().SpanID().String()),
    )
}
```

### Usage in a service:

```go
func (s *ProjectService) Create(ctx context.Context, input CreateInput) (*domain.Project, error) {
    logger.WithTrace(ctx).Info("creating project",
        zap.String("name", input.Name),
        zap.String("owner_id", input.OwnerID),
    )
    // ...
}
```

## Creating Custom Spans

```go
import "go.opentelemetry.io/otel"

func (s *ProjectService) Create(ctx context.Context, input CreateInput) (*domain.Project, error) {
    tracer := otel.Tracer("project-service")
    ctx, span := tracer.Start(ctx, "ProjectService.Create")
    defer span.End()

    span.SetAttributes(
        attribute.String("project.name", input.Name),
    )
    // ...
}
```

## Kubernetes Deployment

### Jaeger All-in-One (`deployment/k8s/opentelemetry/observability.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.62.0
          ports:
            - containerPort: 16686  # UI
            - containerPort: 4317   # OTLP gRPC (if direct)
            - containerPort: 4318   # OTLP HTTP (if direct)
          env:
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
spec:
  selector:
    app: jaeger
  ports:
    - name: ui
      port: 16686
      targetPort: 16686
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
```

### OpenTelemetry Collector

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
spec:
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:0.108.0
          args:
            - --config=/etc/otel/config.yaml
          volumeMounts:
            - name: config
              mountPath: /etc/otel
          ports:
            - containerPort: 4317  # OTLP gRPC
            - containerPort: 4318  # OTLP HTTP
      volumes:
        - name: config
          configMap:
            name: otel-collector-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    processors:
      batch:
        timeout: 5s
        send_batch_size: 512
    exporters:
      otlp/jaeger:
        endpoint: jaeger:4317
        tls:
          insecure: true
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [otlp/jaeger]
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
spec:
  selector:
    app: otel-collector
  ports:
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
```

## Application Config for OTel

```yaml
otel:
  enabled: true
  collector_endpoint: "otel-collector:4317"
  token: ""
  host_name: "my-service-1"
  insecure: true
```

## Wiring in main.go

```go
func main() {
    cfg := config.Load("config.yaml")

    // Must be called before server start, deferred after server shutdown
    otelShutdown := trace.InitOTel(cfg.OTel, cfg.App.Name)
    defer otelShutdown()

    app := NewApp(cfg)
    app.Run()
}

func NewApp(cfg *config.Config) *App {
    r := gin.New()

    if cfg.OTel.Enabled {
        r.Use(otelgin.Middleware(cfg.App.Name))
        r.Use(traceIDResponseMiddleware())
    }
    // ...
}
```
