---
name: ddd-go-backend-storage
description: S3-compatible object storage setup using the AWS SDK for Go. Covers MinIO client init, presigned URL generation, and integration with the config system.
---

# Object Storage: S3 / MinIO

## Overview

Use the AWS SDK for Go v2 to interact with S3-compatible object storage (AWS S3, Cloudflare R2, MinIO, etc.).

## Dependencies

```bash
go get github.com/aws/aws-sdk-go-v2
go get github.com/aws/aws-sdk-go-v2/config
go get github.com/aws/aws-sdk-go-v2/credentials
go get github.com/aws/aws-sdk-go-v2/service/s3
```

## Config

```yaml
storage:
  endpoint: "s3.amazonaws.com"      # or "minio.example.com", "https://<account>.r2.cloudflarestorage.com"
  access_key: "${STORAGE_ACCESS_KEY}"
  secret_key: "${STORAGE_SECRET_KEY}"
  bucket: "myapp-uploads"
  use_ssl: true
  region: "us-east-1"
```

## Client Initialization (`pkg/storage/storage.go`)

```go
package storage

import (
    "context"
    "fmt"
    "net/url"
    "time"

    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/credentials"
    "github.com/aws/aws-sdk-go-v2/service/s3"
)

type Client struct {
    client *s3.Client
    bucket string
    cfg    StorageConfig
}

func NewClient(cfg StorageConfig) *Client {
    endpointURL, err := url.Parse(cfg.Endpoint)
    if err != nil {
        panic(fmt.Errorf("invalid storage endpoint: %w", err))
    }

    // Ensure endpoint has scheme for MinIO-style endpoints
    if endpointURL.Scheme == "" {
        if cfg.UseSSL {
            endpointURL.Scheme = "https"
        } else {
            endpointURL.Scheme = "http"
        }
    }

    awsCfg, err := config.LoadDefaultConfig(context.Background(),
        config.WithRegion(cfg.Region),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
            cfg.AccessKey, cfg.SecretKey, "",
        )),
    )
    if err != nil {
        panic(fmt.Errorf("failed to load AWS config: %w", err))
    }

    client := s3.NewFromConfig(awsCfg, func(o *s3.Options) {
        o.BaseEndpoint = aws.String(endpointURL.String())
        o.UsePathStyle = endpointURL.Host != "s3.amazonaws.com" // path-style for MinIO/R2
    })

    return &Client{client: client, bucket: cfg.Bucket, cfg: cfg}
}
```

## Core Operations

### Upload

```go
func (c *Client) Upload(ctx context.Context, key string, body io.Reader, contentType string) error {
    _, err := c.client.PutObject(ctx, &s3.PutObjectInput{
        Bucket:      aws.String(c.bucket),
        Key:         aws.String(key),
        Body:        body,
        ContentType: aws.String(contentType),
    })
    return err
}
```

### Download

```go
func (c *Client) Download(ctx context.Context, key string) (io.ReadCloser, error) {
    output, err := c.client.GetObject(ctx, &s3.GetObjectInput{
        Bucket: aws.String(c.bucket),
        Key:    aws.String(key),
    })
    if err != nil {
        return nil, err
    }
    return output.Body, nil
}
```

### Delete

```go
func (c *Client) Delete(ctx context.Context, key string) error {
    _, err := c.client.DeleteObject(ctx, &s3.DeleteObjectInput{
        Bucket: aws.String(c.bucket),
        Key:    aws.String(key),
    })
    return err
}
```

### Presigned URL (for direct upload/download)

```go
func (c *Client) PresignedUploadURL(ctx context.Context, key string, ttl time.Duration) (string, error) {
    presignClient := s3.NewPresignClient(c.client)
    req, err := presignClient.PresignPutObject(ctx, &s3.PutObjectInput{
        Bucket: aws.String(c.bucket),
        Key:    aws.String(key),
    }, func(opts *s3.PresignOptions) {
        opts.Expires = ttl
    })
    if err != nil {
        return "", err
    }
    return req.URL, nil
}

func (c *Client) PresignedDownloadURL(ctx context.Context, key string, ttl time.Duration) (string, error) {
    presignClient := s3.NewPresignClient(c.client)
    req, err := presignClient.PresignGetObject(ctx, &s3.GetObjectInput{
        Bucket: aws.String(c.bucket),
        Key:    aws.String(key),
    }, func(opts *s3.PresignOptions) {
        opts.Expires = ttl
    })
    if err != nil {
        return "", err
    }
    return req.URL, nil
}
```

## Usage in a Service

```go
type FileService struct {
    storage *storage.Client
}

func (s *FileService) GetUploadURL(ctx context.Context, userID, filename string) (string, error) {
    key := fmt.Sprintf("uploads/%s/%s-%s", userID, uuid.New().String(), filename)
    return s.storage.PresignedUploadURL(ctx, key, 15*time.Minute)
}
```

## Wiring in main.go

```go
storageClient := storage.NewClient(cfg.Storage)
fileService := filesvc.NewFileService(storageClient)
```

## Provider-Specific Notes

| Provider | endpoint | use_ssl | Notes |
|----------|----------|---------|-------|
| AWS S3 | (empty, use default) | true | Set `region` to bucket region |
| Cloudflare R2 | `https://<account>.r2.cloudflarestorage.com` | true | Region can be `auto` |
| MinIO | `localhost:9000` | false | Use path-style addressing |
