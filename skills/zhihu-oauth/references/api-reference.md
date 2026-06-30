# API 参考

## 1. 授权接口

```http
GET https://openapi.zhihu.com/authorize
```

### 请求参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `redirect_uri` | 是 | 授权回调地址（需与申请时一致） |
| `app_id` | 是 | 第三方应用 ID |
| `response_type` | 是 | 固定值：`code` |
| `state` | 否 | 防 CSRF 攻击的随机字符串（强烈推荐） |

### 示例

```
https://openapi.zhihu.com/authorize?redirect_uri=https://yourdomain.com/callback&app_id=YOUR_APP_ID&response_type=code&state=RANDOM_STATE
```

---

## 2. Token 交换接口

```http
POST https://openapi.zhihu.com/access_token
Content-Type: application/json
```

### 请求参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `app_id` | 是 | 第三方应用 ID |
| `app_key` | 是 | 第三方应用密钥 |
| `grant_type` | 是 | 固定值：`authorization_code` |
| `redirect_uri` | 是 | 授权回调地址（需与申请时一致） |
| `code` | 是 | 授权码 |

### 返回数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | string | 访问令牌 |
| `token_type` | string | 固定值：`bearer` |
| `expires_in` | long | 有效期（秒），默认 30 天 |

### 返回示例

```json
{
  "access_token": "fc42fc30390c455184ddbd7e710d05ad",
  "token_type": "bearer",
  "expires_in": 2592000
}
```

---

## 3. 用户信息接口

```http
GET https://openapi.zhihu.com/user
Authorization: Bearer {access_token}
```

### 返回数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `uid` | int | 知乎用户 ID |
| `fullname` | string | 用户昵称 |
| `gender` | string | 性别：`male`、`female`、`unknown` |
| `headline` | string | 个人简介 |
| `description` | string | 个人描述 |
| `avatar_path` | string | 头像 URL |
| `phone_no` | string | 手机号（需授权，否则为空） |
| `email` | string | 邮箱（需授权，否则为空） |

### 返回示例

```json
{
  "uid": 23456789876,
  "fullname": "用户昵称",
  "gender": "male",
  "headline": "个人简介",
  "description": "个人描述",
  "avatar_path": "https://picl.zhimg.com/xxx.jpg",
  "phone_no": "+8618800000000",
  "email": "user@zhihu.com"
}
```

---

## 4. 用户对象字段

社交关系接口返回的用户对象包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `uid` | int | 知乎用户 ID |
| `hash_id` | string | 用户 hash ID（用于 URL） |
| `fullname` | string | 用户昵称 |
| `gender` | string | 性别 |
| `headline` | string | 个人简介 |
| `description` | string | 个人描述 |
| `avatar_path` | string | 头像 URL |
| `url` | string | 用户主页 URL |
| `email` | string | 邮箱（根据权限返回） |
| `phone_no` | string | 手机号（根据权限返回） |

---

## 5. 粉丝列表

```http
GET https://openapi.zhihu.com/user/followers?page=0&per_page=10
Authorization: Bearer {access_token}
```

返回粉丝用户列表。

---

## 6. 关注列表

```http
GET https://openapi.zhihu.com/user/followed?page=0&per_page=10
Authorization: Bearer {access_token}
```

返回关注用户列表。

---

## 7. 关注动态

```http
GET https://openapi.zhihu.com/user/moments?page=0&per_page=10
Authorization: Bearer {access_token}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `page` | int | 否 | 页码，从 0 开始 | 0 |
| `per_page` | int | 否 | 每页数量，最大 50，总计最多查询 200 条 | 10 |

### 返回数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | array | 动态列表 |
| `data[].actor.name` | string | 动作发起人昵称 |
| `data[].action_text` | string | 动作描述（如"回答了问题"） |
| `data[].action_time` | int | 动作时间（Unix 时间戳） |
| `data[].target.title` | string | 内容标题 |
| `data[].target.excerpt` | string | 内容摘要 |
| `data[].target.author.name` | string | 内容作者昵称 |

### 返回示例

```json
{
  "data": [
    {
      "actor": { "name": "用户昵称" },
      "action_text": "回答了问题",
      "action_time": 1713830400,
      "target": {
        "title": "问题标题",
        "excerpt": "回答摘要...",
        "author": { "name": "作者昵称" }
      }
    }
  ]
}
```
