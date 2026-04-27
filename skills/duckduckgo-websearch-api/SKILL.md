---
name: duckduckgo-websearch-api
description: >
  在 Agent 系统中集成 DuckDuckGo Web Search API，支持文本、图片、视频、新闻搜索。
  当 DuckDuckGo 不可用时，自动降级到 Bing 搜索作为兜底方案。
  无需官方 API Key，直接调用 DuckDuckGo 内部 HTTP 端点（i.js / v.js / news.js / lite）
  或 Bing HTML 搜索，适用于需要轻量级搜索能力的 Agent 服务。
tags:
  - duckduckgo
  - websearch
  - search-api
  - bing
  - agent
model: deepseek-chat
rootUrl: https://cdn.jsdelivr.net/gh/LSTM-Kirigaya/jinhui-skills@main/skills/duckduckgo-websearch-api/SKILL.md
---

# DuckDuckGo WebSearch API

在 Agent 系统中直接调用 DuckDuckGo 的 HTTP 端点实现搜索服务，无需 API Key。若 DuckDuckGo 被屏蔽，则自动 fallback 到 Bing 搜索。

## 架构概览

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User query    │────▶│  Get vqd token   │────▶│  Call JSON API  │
└─────────────────┘     │  (duckduckgo.com)│     │  (i.js/v.js/...)│
                        └──────────────────┘     └─────────────────┘
                                                              │
                        ┌──────────────────┐                  ▼
                        │  Parse results   │◀─────────────────┘
                        └──────────────────┘
```

**文本搜索**无需 vqd token，可直接使用 DuckDuckGo Lite HTML POST 或 Bing GET。

## 核心流程

### 1. 获取 vqd token（图片/视频/新闻必需）

```
GET https://duckduckgo.com?q={encoded_query}
Headers:
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

从 HTML 响应中提取 `vqd`：
- `vqd="([\d-]+)"`
- `vqd=([\d-]+)`
- `vqd:"([\d-]+)"`

> 若网络屏蔽 DuckDuckGo 导致获取失败，直接降级到 Bing 文本搜索。

### 2. 调用搜索 API

| 搜索类型 | 端点 | 说明 |
|----------|------|------|
| 图片 | `GET https://duckduckgo.com/i.js` | 需 `vqd`、`o=json`、`q`、`l`、`p` |
| 视频 | `GET https://duckduckgo.com/v.js` | 需 `vqd`、`o=json`、`q`、`l`、`p` |
| 新闻 | `GET https://duckduckgo.com/news.js` | 需 `vqd`、`o=json`、`noamp=1`、`q`、`l`、`p` |
| 建议 | `GET https://duckduckgo.com/ac/` | 无需 `vqd`，参数 `q`、`type=list` |

通用请求头：
```
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
Accept: */*
Referer: https://duckduckgo.com/
```

JSON API 统一响应格式：
```json
{
  "results": [...],
  "next": "..."
}
```

### 3. 文本搜索兜底（Bing）

当 DuckDuckGo JSON API 不可用时：
- **DuckDuckGo Lite**: `POST https://lite.duckduckgo.com/lite/`
- **Bing**: `GET https://www.bing.com/search`

详见 `references/bing-text-search.md` 和 `references/duckduckgo-http-api.md`。

## 反爬虫与容错

| 措施 | 处理方式 |
|------|----------|
| vqd token | 从初始 HTML 抓取，失败则降级 Bing |
| User-Agent | 使用真实浏览器 UA |
| Referer | JSON API 调用时设置 `https://duckduckgo.com/` |
| Cookie | 启用 cookie jar，Bing 需要 `_EDGE_CD` 和 `_EDGE_S` |
| 限流 | 请求间隔 0.75s，指数退避重试 3 次 |
| 网络屏蔽 | 直接 fallback 到 Bing 文本搜索 |

## 错误处理

| HTTP 状态 | 含义 | 动作 |
|-----------|------|------|
| 200 | 成功 | 解析 JSON 结果 |
| 202/301/400/403/429/418 | 限流/封禁 | 退避并重试 |
| 超时/连接拒绝 | 网络被屏蔽 | 使用代理或 fallback 到 Bing |
| 结果为空 | 无匹配 | 返回空列表 |

## 环境考量

- DuckDuckGo 在某些地区被屏蔽，Bing 可用性更广
- 若两者均不可用，可考虑 SearXNG 实例或其他搜索 API

## 参考文档

- [DuckDuckGo HTTP API 详情](references/duckduckgo-http-api.md) — 完整端点、参数、响应字段、过滤条件
- [Bing 文本搜索兜底](references/bing-text-search.md) — Bing 请求构造、Cookie、URL 解包、分页
