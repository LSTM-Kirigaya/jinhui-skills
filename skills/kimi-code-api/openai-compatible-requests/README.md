# OpenAI 兼容请求（Kimi Coding）

业务 API 基址：**`https://api.kimi.com/coding/v1`**（与 `auth.kimi.com` 不同主机）。

## 路径（与 OpenAI 一致的风格）

- `POST /chat/completions` — 聊天、流式、工具调用（function calling）  
- `GET /models` — 模型列表  

路径前拼接 Base URL（注意末尾是否已有 `/v1`，避免双斜杠）。

## 鉴权

- `Authorization: Bearer <access_token 或用户手动填写的 API Key>`  
- 若密钥字符串本身已含 `Bearer ` 前缀，拼接前应去掉重复前缀。

## 必加请求头（Coding 接口）

对 **`api.kimi.com`** 且路径包含 **`/coding`** 的调用，需带：

```http
User-Agent: KimiCLI/1.0.0
```

（或与 Kimi 官方 CLI 同族的版本号形式，如 `KimiCLI/x.y.z`。）缺少时常见 **403**（如 access 被终止类错误）。

OAuth 请求阶段也建议使用同类 User-Agent，与服务端策略一致。

## 请求体

与 OpenAI Chat Completions 兼容：`model`、`messages`、可选 `stream`、`temperature`、`max_tokens`；工具场景下 `tools`、`tool_choice` 等。具体模型名以 `/models` 返回为准（示例名如 `kimi-for-coding`，以实际为准）。

## 浏览器与 CORS

网页直接 `fetch` 跨域常被拒绝。可选方案：

- 桌面壳：**原生 HTTP 客户端**或框架提供的 **HTTP 插件**代发请求；  
- 自有后端：服务端转发；  
- 扩展/仅本地：按环境配置代理。

## 与其它厂商分支

若同一套 UI 支持 Anthropic 等，需按 host 分支：Anthropic 使用 `x-api-key` 等自有头，**不要**对 Kimi Coding 端点套用 Anthropic 逻辑。
