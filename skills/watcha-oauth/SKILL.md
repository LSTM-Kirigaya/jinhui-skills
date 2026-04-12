---
name: watcha-oauth
description: 观猹（Watcha）OAuth2.0 接入指南。用于帮助开发者完成观猹 Authorization Code 授权流程，包括客户端申请、授权页跳转、Token 换取、用户信息获取、Token 刷新与校验。适用于 Web 应用、移动 App 等场景，支持 PKCE 扩展。
rootUrl: file:///Users/kirigaya/project/jinhui-skills/skills/watcha-oauth/SKILL.md
tags:
  - oauth
  - watcha
  - authentication
  - api
model: deepseek-chat
---

# 观猹 OAuth2.0 接入指南

## 快速开始

1. **申请开通**：填写申请表单并获取 `client_id` 和 `client_secret`
2. **引导授权**：将用户跳转至观猹授权页面
3. **处理回调**：在 `redirect_uri` 接收 `code`，换取 `access_token`
4. **获取用户信息**：使用 `access_token` 调用用户接口

## 参考文档

- **申请与测试**：见 [references/application.md](references/application.md) — 包含申请表单、测试环境 client_id/client_secret
- **授权流程**：见 [references/authorization-flow.md](references/authorization-flow.md) — 包含完整授权流程、Scope 说明、回调处理、错误码
- **API 参考**：见 [references/api-reference.md](references/api-reference.md) — 包含 Token 换取、刷新、校验、用户信息 API 的详细请求与响应

## 脚本工具

- **PKCE 生成**：`scripts/generate-pkce.py` — 生成 `code_verifier` 和 `code_challenge`
- **Python 完整示例**：`scripts/watcha-oauth-example.py`
- **Node.js 完整示例**：`scripts/watcha-oauth-example.js`

## 核心端点

| 用途 | 端点 |
|------|------|
| 授权页 | `GET https://watcha.cn/oauth/authorize` |
| 换取/刷新 Token | `POST https://watcha.cn/oauth/api/token` |
| 用户信息 | `GET https://watcha.cn/oauth/api/userinfo` |
| Token 校验 | `POST https://watcha.cn/oauth/api/introspect` |

## 注意事项

- `client_id` 含 `+`、`/`、`=` 等特殊字符，URL 传递时必须做 URL 编码
- 公开客户端（`is_public=true`）必须使用 PKCE
- `email` 和 `phone` 仅在申请了对应 scope 且用户同意后才返回
