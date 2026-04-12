# 申请开通与测试环境

## 申请流程

当前观猹尚未实现 OAuth2 前端管理页面，请按以下步骤申请开通：

1. 填写**观猹 OAuth2.0 服务开通信息收集表**
2. 联系观猹官方人员对接
3. 官方人员根据提供的信息创建客户端
4. 获取 `client_id` 和 `client_secret`，妥善保存

## 创建客户端参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 应用名称，将在授权页面展示为 `"{name} 请求获取权限"` |
| `domain` | string | 是 | 回调地址的 URI Schema，例如 `http://localhost:3000` |
| `allowed_scopes` | string | 是 | 申请的权限范围，多个值用空格分隔。可选值：`read`（基础信息）、`email`（邮箱）、`phone`（手机号） |
| `is_public` | boolean | 否 | 是否为公开客户端（默认 `false`） |

### 客户端类型说明

- **机密客户端**（`is_public=false`）：有后端能安全存储 `client_secret`
- **公开客户端**（`is_public=true`）：无法安全存储 secret，如纯前端应用，流程中**必须**使用 PKCE 进行认证

## 开发环境测试信息

| 类型 | client_id | client_secret |
|------|-----------|---------------|
| 机密客户端 | `1p9Mcr+CNLPAMFC0` | `aqkUs+5ZGLSVG6A/L/I0ib9uownWxH+w` |
| 非机密客户端 | `3p9Mcr+CNLPAMFC0` | （无需） |

## 存量 Client 获取 phone/email

适用于 2026 年 3 月 30 日前接入上线的 Client：

1. **联系运营开通 scope**：联系观猹官方人员，申请为已有 `client_id` 增加 `email` 或 `phone` scope 权限
2. **修改授权请求参数**：在跳转授权页面时，将 `scope` 参数中增加所需的权限值，例如将 `scope=read` 改为 `scope=read email phone`

> ⚠️ 两步缺一不可——未开通 scope 时传参无效，已开通但未传参也不会返回对应字段。
