---
name: zhihu-oauth
description: 知乎 OAuth 2.0 接入指南。用于帮助开发者完成知乎 Authorization Code 授权流程，包括 APP_ID/APP_KEY 申请、授权页跳转、Token 换取、用户信息获取及社交关系接口调用。适用于 Web 应用第三方登录场景。
rootUrl: https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/refs/heads/main/skills/zhihu-oauth/SKILL.md
tags:
  - oauth
  - zhihu
  - authentication
  - api
model: deepseek-chat
---

# 知乎 OAuth 2.0 接入指南

## 快速开始

1. **申请开通**：发送邮件至 `product-platform@zhihu.com` 申请 `app_id` 和 `app_key`，并提供 `redirect_uri`
2. **引导授权**：将用户跳转至知乎授权页面
3. **处理回调**：在 `redirect_uri` 接收 `code`，后端换取 `access_token`
4. **获取用户信息**：使用 `access_token` 调用用户信息接口

## 参考文档

- **申请开通**：见 [references/application.md](references/application.md) — 包含申请邮箱、邮件主题、所需信息
- **授权流程**：见 [references/authorization-flow.md](references/authorization-flow.md) — 包含完整授权流程、回调处理、错误码
- **API 参考**：见 [references/api-reference.md](references/api-reference.md) — 包含授权、Token 交换、用户信息、社交关系接口的详细请求与响应

## 脚本工具

- **Python 完整示例**：`scripts/zhihu-oauth-example.py`
- **Node.js/Express 完整示例**：`scripts/zhihu-oauth-example.js`

## 核心端点

| 用途 | 端点 | 方法 |
|------|------|------|
| 授权页 | `https://openapi.zhihu.com/authorize` | GET |
| 换取 Token | `https://openapi.zhihu.com/access_token` | POST |
| 用户信息 | `https://openapi.zhihu.com/user` | GET |
| 粉丝列表 | `https://openapi.zhihu.com/user/followers` | GET |
| 关注列表 | `https://openapi.zhihu.com/user/followed` | GET |
| 关注动态 | `https://openapi.zhihu.com/user/moments` | GET |

## 注意事项

- `app_id` 和 `app_key` 需通过环境变量注入，**严禁硬编码或提交到代码仓库**
- 必须生成随机 `state` 参数防止 CSRF 攻击，并在回调时验证
- Token 交换必须在后端完成，不能暴露给前端
- 知乎 OAuth 目前**不支持 `refresh_token`**，token 默认有效期 30 天
- 生产环境 `redirect_uri` 必须使用 HTTPS
