# 凭据与替代方案

## 三种常见用法

1. **Device OAuth（设备码）**  
   用户在浏览器完成登录；客户端得到 `access_token` + `refresh_token`。适合桌面/CLI，无需用户粘贴长密钥。

2. **手动 API Key / Token**  
   用户在设置里直接填写字符串，作为 `Authorization: Bearer …` 的密钥（与 OpenAI 兼容用法一致）。不经过 OAuth 文件或设备码流程。

3. **并存时的优先级（建议）**  
   - 若同时存在「OAuth 存盘令牌」与「手动填写的 Key」，需在产品层二选一规则，避免无效旧 Key 覆盖有效 OAuth（常见做法：OAuth 登录成功后清空该厂商槽位的手动 Key；或 OAuth 优先于手动）。  
   - 若仅需手动 Key：先撤销/删除本地 OAuth 状态，再填 Key。

## 解析顺序（概念）

对 **Kimi Coding** 类端点（`api.kimi.com` 且路径含 `/coding`）：

1. 若 OAuth 的 access 可用（含经 `refresh_token` 换新后的 access），用其作为 Bearer 密钥。  
2. 否则回退到用户配置里的手动 API Key/Token。

实现时把「拿有效字符串」集中在一个函数里，聊天、拉模型列表、带工具的补全等统一调用，避免重复逻辑。
