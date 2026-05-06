---
name: tencent-ses-service
version: 1.0.0
description: |
  腾讯云官方的邮件推送 SES 服务使用 skill。
  涵盖：SMTP 发送邮件所需的全部环境变量、API 接口设计规范、验证码邮件的完整发送流程（含人机验证、频率控制、Redis 存储）。
  本 skill 以网络协议 / HTTP API 接口级别描述，不绑定具体编程语言。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# 腾讯云邮件推送 SES 服务

本 skill 描述如何通过腾讯云 SES（Simple Email Service）的 **SMTP 协议** 发送邮件。腾讯云 SES 提供两种接入方式：**API SDK 方式**（`SendEmail` 接口）和 **SMTP 方式**。本文档基于 SMTP 方式，因为它不依赖腾讯云 SDK，通用性更强。

---

## 一、前置条件

### 1.1 开通腾讯云 SES 服务

在腾讯云控制台开通 SES 服务，完成发件域名配置和 DKIM/SPF 验证。

- 控制台地址：`https://console.cloud.tencentcloud.com/ses`
- 发件域名需要已备案且通过 DNS 验证
- 配置完成后获取 SMTP 凭据（见下方环境变量）

### 1.2 依赖的外部服务

| 服务 | 用途 |
|---|---|
| Redis | 存储验证码（含过期时间）、滑块验证 token、频率控制标记 |
| 滑块验证服务 | 生成并校验人机验证 token（本项目使用腾讯云验证码服务） |

---

## 二、环境变量

以下环境变量为必填项，缺一不可：

| 变量名 | 示例值 | 说明 |
|---|---|---|
| `TENCENTCLOUD_SMTP_HOST` | `smtp.qcloudmail.com` | 腾讯云 SES SMTP 服务器地址 |
| `TENCENTCLOUD_SMTP_PORT` | `465` | SMTP 端口。`465` 为 SSL 直连，`587` 为 STARTTLS |
| `TENCENTCLOUD_SMTP_USER` | `noreply@healthymax.cn` | SMTP 认证用户名（即发件邮箱地址） |
| `TENCENTCLOUD_SMTP_PASSWORD` | `WDWOPKOPkop12312dko` | SMTP 认证密码（在腾讯云 SES 控制台生成，非邮箱登录密码） |

### SMTP 密码获取方式

1. 登录腾讯云 SES 控制台
2. 进入「发件域名」→ 选择已配置的域名
3. 点击「SMTP 密码」→「生成密码」
4. 记录生成的密码（只显示一次）

---

## 三、API 接口设计

### 3.1 发送验证码邮件

**端点：** `POST /api/ses/send-verification-code`

**认证要求：** 无需登录态（公开接口），但需要滑块验证 token。

#### 请求体（JSON）

```
字段            类型      必填    说明
────────────────────────────────────────────────
email          string    是     收件人邮箱地址
captchaToken   string    是     滑块验证通过后获得的 token
```

请求示例（仅供参考，非特定语言）：

```json
{
  "email": "user@example.com",
  "captchaToken": "abc123def456..."
}
```

#### 响应体（JSON）

成功时 HTTP 200：

```json
{
  "success": true,
  "message": "验证码发送成功",
  "data": {
    "requestId": "<messageId from SMTP server>"
  }
}
```

失败时返回对应 HTTP 状态码（400/429/500）：

```json
{
  "success": false,
  "message": "错误描述",
  "data": null
}
```

#### 错误码一览

| HTTP 状态码 | message | 触发条件 |
|---|---|---|
| 400 | `邮箱地址不能为空` | `email` 字段缺失或为空 |
| 400 | `邮箱格式不正确` | `email` 不符合正则 `^[^\s@]+@[^\s@]+\.[^\s@]+$` |
| 400 | `请先完成滑块验证` | `captchaToken` 未传 |
| 400 | `验证已过期，请重新完成滑块验证` | captcha token 在 Redis 中不存在或已过期 |
| 429 | `发送验证码过于频繁，请稍后再试` | 同一邮箱或同一 IP 在 30 秒内重复请求 |
| 500 | `验证服务不可用` | Redis 连接不可用 |
| 500 | `发送邮箱验证码异常: ...` | SMTP 发送失败（携带具体错误信息） |

---

## 四、发送流程（网络接口级描述）

### 整体时序

```
客户端                          服务端                            Redis              SMTP 服务器
  │                               │                                 │                    │
  │  POST /api/ses/send-          │                                 │                    │
  │  verification-code            │                                 │                    │
  │  {email, captchaToken}        │                                 │                    │
  │ ────────────────────────────▶ │                                 │                    │
  │                               │  GET captcha:token:{token}      │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │ ◀────────────────────────────── │                    │
  │                               │  DEL captcha:token:{token}      │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │                                 │                    │
  │                               │  GET throttle:email:{email}     │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │  GET throttle:email:ip:{ip}     │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │                                 │                    │
  │                               │  SETEX email_verification_code: │                    │
  │                               │    {email} 900 {code}           │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │  SETEX throttle:email:{email}   │                    │
  │                               │    30 {timestamp}               │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │  SETEX throttle:email:ip:{ip}   │                    │
  │                               │    30 {timestamp}               │                    │
  │                               │ ──────────────────────────────▶ │                    │
  │                               │                                 │                    │
  │                               │  EHLO / STARTTLS / AUTH LOGIN   │                    │
  │                               │ ─────────────────────────────────────────────────▶ │
  │                               │  MAIL FROM / RCPT TO / DATA     │                    │
  │                               │ ─────────────────────────────────────────────────▶ │
  │                               │ ◀───────────────────────────────────────────────── │
  │                               │                                 │                    │
  │  ◀────────────────────────────│                                 │                    │
  │  {success: true,              │                                 │                    │
  │   data: {requestId: "..."}}   │                                 │                    │
```

### 步骤详解

#### Step 1：参数校验

- 检查 `email` 非空
- 检查 `email` 匹配格式正则 `^[^\s@]+@[^\s@]+\.[^\s@]+$`
- 检查 `captchaToken` 非空
- 检查 Redis 连接可用

#### Step 2：滑块验证

- 从 Redis 读取 key：`captcha:token:{captchaToken}`
- 读取后立即删除该 key（一次性使用，防重放）
- 若 key 不存在或已过期 → 返回 400，要求用户重新完成滑块验证

#### Step 3：频率控制（双重节流）

检查两个 Redis key，任一存在即返回 429：

| Redis Key | TTL | 含义 |
|---|---|---|
| `throttle:email:{email}` | 30s | 同一邮箱 30 秒内只能发送一次 |
| `throttle:email:ip:{clientIP}` | 30s | 同一 IP 30 秒内只能发送一次 |

> 客户端 IP 从请求头 `X-Forwarded-For` 的第一个值获取，无代理时回退为 `127.0.0.1`。

#### Step 4：生成验证码并存入 Redis

- 生成 6 位随机数字验证码（范围 100000-999999）
- 存入 Redis：`SETEX email_verification_code:{email} 900 {code}`
  - TTL = 900 秒（15 分钟）
- 设置节流标记：
  - `SETEX throttle:email:{email} 30 {timestamp}`
  - `SETEX throttle:email:ip:{ip} 30 {timestamp}`

#### Step 5：通过 SMTP 发送邮件

连接到腾讯云 SMTP 服务器并发送邮件。SMTP 会话参数：

| 参数 | 值 | 说明 |
|---|---|---|
| Host | `{TENCENTCLOUD_SMTP_HOST}` | 腾讯云 SMTP 服务器 |
| Port | `{TENCENTCLOUD_SMTP_PORT}` | `465`（SSL）或 `587`（STARTTLS） |
| Secure | `true`（465 端口）/ `false`（587 端口） | 是否使用 SSL 直连 |
| Auth User | `{TENCENTCLOUD_SMTP_USER}` | SMTP 认证用户名 |
| Auth Pass | `{TENCENTCLOUD_SMTP_PASSWORD}` | SMTP 认证密码 |

邮件信封（SMTP `MAIL FROM` / `RCPT TO`）：

| 字段 | 值 |
|---|---|
| MAIL FROM | `noreply@{发件域名}` 实际地址为 `{TENCENTCLOUD_SMTP_USER}` |
| RCPT TO | 请求参数中的 `email` |
| From (header) | `"noreply@{域名}" <{TENCENTCLOUD_SMTP_USER}>` |
| To (header) | 请求参数中的 `email` |
| Subject | `邮箱验证 - 智健启能` |

#### Step 6：返回结果

- 成功：返回 HTTP 200，`data.requestId` 为 SMTP 服务器返回的 `messageId`
- 失败：返回 HTTP 500，`message` 包含 SMTP 错误详情

#### Step 7：客户端校验验证码

客户端后续可通过独立的验证接口校验验证码（读取 Redis key `email_verification_code:{email}` 并比对），验证通过后删除该 key。

---

## 五、邮件内容规范

### HTML 邮件结构

邮件正文使用 HTML 格式，建议遵循以下规范：

```
结构层次：
├── 外层容器（最大宽度 600px，圆角 24px，白色背景）
│   ├── Header：Logo 图片 + 产品名称
│   ├── Divider：1px 分割线
│   ├── Body：
│   │   ├── 标题（如"安全验证"）
│   │   ├── 说明文字
│   │   ├── 验证码展示区（灰底圆角卡片，等宽字体居中展示 6 位数字）
│   │   └── 过期提示
│   └── Footer：安全提示 + 版权信息
```

### 设计约束

- 移动端适配：使用 `@media only screen and (max-width: 600px)` 覆盖容器宽度和圆角
- 字体栈：`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`
- 验证码字体：等宽字体（`Monaco, Consolas, monospace`），字间距 `0.2em`
- 品牌色：主色 `#f6993b`（橙），文字色 `#1E293B` / `#64748B`，背景 `#F8FAFC`

### HTML 邮件模板示例

> ⚠️ 以下为 HTML 结构说明，具体内容请根据项目品牌调整。代码仅为示意，不绑定任何编程语言。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#F8FAFC;font-family:-apple-system,...">
  <table width="100%"><tr><td align="center" style="padding:40px 20px;">
    <table width="600" style="background:#fff;border-radius:24px;...">
      <!-- Header: Logo + 产品名 -->
      <tr><td>...</td></tr>
      <!-- Body: 标题 + 说明 + 验证码 + 过期时间 -->
      <tr><td>...</td></tr>
      <!-- Footer: 安全提示 + 版权 -->
      <tr><td>...</td></tr>
    </table>
  </td></tr></table>
</body>
</html>
```

---

## 六、Redis Key 设计汇总

| Key Pattern | 类型 | TTL | 用途 |
|---|---|---|---|
| `captcha:token:{token}` | 任意 | 由滑块服务设定 | 人机验证 token（验证后删除） |
| `throttle:email:{email}` | String (timestamp) | 30s | 邮箱维度的发送频率控制 |
| `throttle:email:ip:{ip}` | String (timestamp) | 30s | IP 维度的发送频率控制 |
| `email_verification_code:{email}` | String (6位数字) | 900s (15min) | 邮箱验证码存储 |

---

## 七、前端调用约定

### 触发验证码发送的前置条件

客户端在调用 `POST /api/ses/send-verification-code` 前，必须：

1. 用户已完成滑块验证 → 获得 `captchaToken`
2. 用户输入的邮箱格式已通过前端初步校验

### 调用模式

```
前端组件                    sesService                     API Route
   │                            │                              │
   │  sendVerificationCode()    │                              │
   │ ─────────────────────────▶ │                              │
   │                            │  POST /api/ses/              │
   │                            │    send-verification-code    │
   │                            │ ───────────────────────────▶ │
   │                            │ ◀─────────────────────────── │
   │ ◀───────────────────────── │                              │
```

> 示例代码（仅为说明调用模式，不涉及具体语言）：
> ```
> service.sendVerificationCode({ email: "user@example.com", captchaToken: "xxx" })
> ```

### 消费者场景

验证码邮件在以下场景被触发：

| 场景 | 说明 |
|---|---|
| 用户注册 | 输入邮箱后发送验证码 |
| 邮箱登录 | 选择邮箱验证码登录模式 |
| 修改密码 | 向已绑定的邮箱发送验证码 |
| 绑定/更换邮箱 | 向新邮箱发送验证码以确认所有权 |

---

## 八、常见问题

### Q: 为什么选择 SMTP 方式而非 API SDK？

SMTP 方式不依赖 `tencentcloud-sdk-nodejs`，使用标准的 SMTP 协议（RFC 5321），可以对接任何支持 SMTP 的邮件库。腾讯云 SES API SDK（`SendEmail` 接口）需要 `SecretId`/`SecretKey` 签名认证，而 SMTP 方式只需用户名密码，部署更简单。

### Q: 端口 465 vs 587 如何选择？

- **465（SSL）**：SMTP over SSL，连接即加密，推荐使用
- **587（STARTTLS）**：先明文连接再升级 TLS，部分云环境防火墙兼容性更好

本 skill 使用 465 端口 + `secure: true`。

### Q: SMTP 密码和腾讯云 API SecretKey 是同一个吗？

**不是。** SMTP 密码是在 SES 控制台单独生成的，仅用于 SMTP 认证。API SecretKey 用于调用腾讯云其他 API（如 SMS 短信服务），两者独立。

### Q: 如何扩展为发送其他类型的邮件？

在现有 SMTP 连接基础上，只需构造不同的 `Subject` 和 `html` 内容即可发送任意事务邮件。注意：
- 发件地址必须使用已配置的发件域名
- 腾讯云 SES 对发送频率和内容有审核要求
- 建议为不同类型的邮件也加入 Redis 节流控制

---

## 九、安全检查清单

- [ ] SMTP 凭据（`TENCENTCLOUD_SMTP_PASSWORD`）仅存储在服务端环境变量，不暴露给前端
- [ ] 发送验证码前必须校验滑块验证 token
- [ ] 验证码存储使用 Redis TTL 自动过期
- [ ] 双重频率控制（邮箱 + IP），防止短信轰炸
- [ ] 滑块验证 token 一次性使用（读后即删），防重放攻击
- [ ] 接口路径加入公开白名单（如反向代理配置）以允许未登录用户访问
- [ ] 邮件内容中的链接使用 HTTPS
