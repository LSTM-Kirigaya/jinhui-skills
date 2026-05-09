---
name: 3d-shape-captcha
description: 基于 Three.js 实时渲染的 3D 几何体验证码系统，支持软阴影和 Raycaster 点击交互。后端生成 6 个大小严格互不相同的 3D 几何体元数据（位置、旋转、缩放、颜色、类型），前端使用多光源布光和正交相机实现公平大小比较。适用于实现或修改基于点击的 3D 几何体验证码，或将图形验证码集成到邮件验证码发送等敏感操作中。
---

# 3D Shape CAPTCHA

A click-based geometric CAPTCHA system with real-time 3D rendering, multi-light shadows, and proportional scale generation guaranteeing 6 unique sizes.

## Architecture

```
Backend (Go)          Frontend (Vue3 + Three.js)
    |                         |
Generate 6 shape         Render WebGL scene
metadata (no PNG)        with shadows
    |                         |
Store in Redis  <---  Raycaster click
    |               detects object
Validate shapeIndex       |
    |                         |
Issue token  --------->  Success
```

Backend generates scene metadata only. Frontend renders the actual 3D scene with Three.js. User clicks are validated by object index, not pixel coordinates.

## Backend Implementation

### Core Files

- `assets/backend-captcha.go` — Complete Go implementation (captcha generation + verification)
- `references/backend-api.md` — API specification, data models, Redis schema, scale algorithm

### Key Design Decisions

1. **No PNG rendering** — Backend returns JSON metadata; frontend handles all visuals
2. **Proportional scale** — 6 shapes generated from a scale `[0.55, 1.30]` with equal-interval base values plus ±0.03 jitter. Base interval (0.15) > 2× jitter range (0.06) mathematically guarantees all 6 scales are unique
3. **Grid layout** — 2×3 grid with ±0.4 random offset within each cell prevents overlap
4. **Volume comparison** — Uses `scale³` as uniform metric regardless of shape type

### Redis Schema

| Key | Value | TTL |
|---|---|---|
| `captcha:{id}` | JSON: `{targetIndex, shapes[], prompt, targetShape}` | 5 min |
| `captcha_token:{token}` | `"1"` | 5 min |

### Integration Points

- `POST /api/captcha/generate` — Returns 6 shape metadata
- `POST /api/captcha/verify` — Receives `{captchaId, shapeIndex}`, returns token on success
- `ValidateCaptchaToken(redis, token)` — Utility for other controllers (e.g. email verification)

## Frontend Implementation

### Core Files

- `assets/CaptchaDialog.vue` — Complete Vue3 component with Three.js scene
- `assets/api-index.js` — API client functions
- `references/frontend-integration.md` — Scene setup, lighting config, raycaster, responsive CSS

### Three.js Scene Setup

| Component | Configuration |
|---|---|
| Renderer | WebGLRenderer, antialias, shadowMap enabled, PCFSoftShadowMap |
| Camera | OrthographicCamera (frustumSize=7.5), position (8,8,8), lookAt (0,0.5,0) |
| Lights | Ambient(0.35) + Hemisphere(0.4) + Directional(1.4, casts shadow) + Fill(0.25) + Rim Point(0.4) |
| Ground | PlaneGeometry(20,20), MeshStandardMaterial, receiveShadow |
| Material | MeshStandardMaterial, roughness=0.35, metalness=0.08 |

### Shape Geometry Mapping

| `type` | Shape | Three.js Geometry |
|---|---|---|
| 0 | Cube | `BoxGeometry(1,1,1)` |
| 1 | Cylinder | `CylinderGeometry(0.5,0.5,1,32)` |
| 2 | Triangular prism | `CylinderGeometry(0.5,0.5,1.25,3)` |

Triangular prism uses height 1.25 (vs 1.0 for others) for better visual distinction.

### Click Interaction

Use `THREE.Raycaster` to detect clicked mesh. Each mesh stores its index in `userData.index`. Send this index to backend for verification.

### Responsive Design

- Desktop: dialog max-width 520px, canvas height 360px
- Mobile (<480px): canvas height 260px
- Mobile (<360px): canvas height 220px

## Workflow: Adding CAPTCHA to Email Verification

1. **Backend**: Add `captchaToken` field to email send request
2. **Backend**: Call `captcha.ValidateCaptchaToken(redis, token)` before sending email
3. **Frontend**: Open `CaptchaDialog` before requesting email code
4. **Frontend**: On `success` event, receive token and include it in email API call

## Complete Code References

- Backend implementation: `assets/backend-captcha.go`
- Frontend dialog component: `assets/CaptchaDialog.vue`
- API functions: `assets/api-index.js`
- Backend API details: `references/backend-api.md`
- Frontend integration guide: `references/frontend-integration.md`
