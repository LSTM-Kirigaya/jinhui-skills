---
name: kimi-code-api
description: Kimi Code (api.kimi.com/coding) integration—OAuth 2.0 device flow, refresh tokens, OpenAI-compatible chat/models requests, KimiCLI User-Agent, and manual API key fallback. Use when wiring Kimi Code auth, Bearer tokens, or OpenAI-style clients against Kimi’s coding endpoint.
---

# Kimi Code API

可复用的概念索引：与具体仓库、框架、文件路径无关。细节按主题拆到子目录。

| 主题 | 说明 |
|------|------|
| [凭据与替代方案](credentials/README.md) | Device OAuth、手动 API Key/Token、解析优先级与切换注意点 |
| [OAuth 设备码全流程](oauth-device-flow/README.md) | `auth.kimi.com`、轮询、`refresh_token`、本地持久化 |
| [OpenAI 兼容请求](openai-compatible-requests/README.md) | Base URL、路径、`Authorization`、必选 `User-Agent`、CORS 与传输层 |
