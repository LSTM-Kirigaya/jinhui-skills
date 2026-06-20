---
name: rn-app-builder
description: 基于真实项目沉淀的 React Native 移动端 App 一键构建方案。覆盖 Expo 初始化、monorepo 共享包、鉴权路由、API 适配、主题系统与构建发布。
tags: ["react-native", "expo", "mobile-app", "typescript", "monorepo"]
model: deepseek-chat
rootUrl: https://cdn.jsdelivr.net/gh/LSTM-Kirigaya/jinhui-skills@main/skills/rn-app-builder/SKILL.md
---

# React Native App Builder

## 目标

一键搭建或复刻一个生产级 Expo + React Native + TypeScript 移动端 App。适用于：

- 从零开始新建 `apps/mobile`
- 在 monorepo 中补齐移动端应用
- 为已有后端快速配套一个原生 App 壳
- 统一团队 RN 项目结构、依赖版本与工程实践

## 核心能力

- **统一技术栈**：Expo SDK 56 / React Native 0.85 / React 19 / TypeScript
- **monorepo 友好**：共享 `packages/core`（类型/纯计算）与 `packages/api-client`（平台无关 HTTP 客户端）
- **鉴权路由**：`AuthProvider` + React Navigation 7，启动自检 token，未登录进登录页，已登录进主 Tab
- **API 适配器**：RN 侧注入 `fetch`、`AsyncStorage`、文件上传，业务代码保持平台无关
- **主题与组件**：统一颜色、间距、圆角、阴影，复用 Page / AppButton / Card 等基础组件
- **工程化**：TypeScript strict、Metro / Babel 配置、EAS 构建脚本
- **模拟器键盘**：所有输入框支持电脑键盘输入与回车跳转

## 快速开始

```bash
python3 skills/rn-app-builder/scripts/create-rn-app.py \
  --target apps/mobile \
  --app-name MyApp \
  --package-name com.example.myapp \
  --api-base-url http://127.0.0.1:3010
```

生成后按需替换：

1. `app.json` 中的应用名、scheme、bundleIdentifier / package、图标
2. `src/config.ts` 中的 `API_BASE_URL`
3. `src/screens/LoginScreen.tsx` 的登录方式（密码 / 短信 / 微信）
4. `src/navigation/RootNavigator.tsx` 的业务路由与 Tab
5. `src/theme/index.ts` 的品牌色

## 推荐目录结构

```
apps/mobile/
  App.tsx
  app.json
  index.ts
  package.json
  babel.config.js
  metro.config.js
  tsconfig.json
  tsconfig.typecheck.json
  src/
    api.ts                 # 创建 apiClient，注入 RN 适配器与 AsyncStorage
    config.ts              # API_BASE_URL、版本号、调试开关
    env.d.ts               # 环境变量类型
    theme/                 # colors / spacing / radius / shadow
    components/            # Page、AppButton、Card 等基础组件
    providers/             # AuthProvider、DialogProvider 等
    navigation/            # RootNavigator、TabBar、types
    screens/               # LoginScreen、HomeScreen、ProfileScreen ...
    hooks/                 # useHomeDashboard 等业务 hooks
    utils/                 # date、image、errors 等工具
packages/
  core/                    # DTO、枚举、纯计算（平台无关）
  api-client/              # 适配器式 HTTP 客户端 + TokenStorage 接口
```

## 关键模块

### 1. AuthProvider

职责单一：

- 启动时检查 `AsyncStorage` 中是否有 token
- 暴露 `isBootstrapping` / `isAuthenticated`
- 提供 `loginWithPassword`、`loginWithSMSCode`、`loginWithWechat`、`logout`
- `RootNavigator` 据此渲染登录栈或主 Tab

### 2. API 适配器

`packages/api-client` 定义接口：

```ts
interface ApiClientAdapters {
  request(url: string, options?: { method?; headers?; body?; timeoutMs? }): Promise<{ status; data; headers }>
  uploadFile(input: UploadFileInput): Promise<{ status; data; headers }>
  tokenStorage: {
    getAccessToken(): Promise<string | null>
    setTokens(tokens: { accessToken; refreshToken; userId }): Promise<void>
    clearTokens(): Promise<void>
  }
}
```

`apps/mobile/src/api.ts` 注入：

- `fetch` 做请求，自动 JSON 序列化
- `AsyncStorage` 存取 token
- `XMLHttpRequest` 做多文件上传（带进度与超时）

### 3. 导航

```
RootStack
├── 未登录：Login
└── 已登录：MainTabs
    ├── HomeTab
    ├── StatsTab
    ├── CommunityTab
    └── ProfileTab
```

业务子页面（分析、记录、设置、消息等）统一挂在 RootStack 下，通过 `navigation.navigate('ScreenName')` 跳转。

### 4. 主题

统一导出：

```ts
export const colors = { brand, brandDark, background, surface, text, textSecondary, danger, warning, ... }
export const spacing = { xs, sm, md, lg, xl }
export const radius = { sm, md, lg, pill }
export const shadow = { shadowColor, shadowOpacity, shadowRadius, shadowOffset, elevation }
```

所有 screen / component 只引用 `theme`，不硬编码色值。

## 依赖清单

```json
{
  "expo": "~56.0.0",
  "react": "19.2.3",
  "react-native": "0.85.3",
  "@react-navigation/native": "^7.3.1",
  "@react-navigation/bottom-tabs": "^7.18.0",
  "@react-navigation/native-stack": "^7.17.3",
  "@react-native-async-storage/async-storage": "2.2.0",
  "react-native-safe-area-context": "~5.7.0",
  "react-native-screens": "4.25.2",
  "react-native-svg": "15.15.4",
  "lucide-react-native": "^1.20.0"
}
```

按需追加：

- `expo-image-picker` — 相册 / 拍照
- `expo-file-system` — 本地文件读写
- `expo-clipboard` — 剪贴板
- `expo-media-library` — 保存图片到相册

## 输入框规范

所有 `TextInput` 必须支持 iOS Simulator / Android Emulator 的电脑键盘：

- 绑定 `value` + `onChangeText`
- 账号/密码：`autoCapitalize="none" autoCorrect={false}`
- 邮箱：`inputMode="email" keyboardType="email-address"`
- 验证码：`inputMode="numeric"`
- 设置 `returnKeyType` + `onSubmitEditing`，用 ref 聚焦下一项或提交

## 验证清单

```bash
npm install
npm --workspace apps/mobile run typecheck
npx expo export --platform ios --output-dir /tmp/mobile-ios-export --clear
```

运行：

```bash
npm --workspace apps/mobile run start
# 或
npm --workspace apps/mobile run ios
npm --workspace apps/mobile run android
```

确认：

- Metro 启动无依赖解析错误
- 未登录打开登录页，已登录打开主 Tab
- 输入框可用电脑键盘输入，回车可聚焦/提交
- 接口基地址指向正确的开发环境

## 注意事项

- 不要把生产域名、密钥、bundle ID 写死到 skill 示例中；生成后由调用方替换
- 图片、品牌名、隐私协议文案必须随项目替换
- 优先把纯逻辑抽到 `packages/core`，保持 screens 薄
- 物理设备调试需要 LAN IP 与防火墙放行端口

## 参考文档

- `references/stack.md` — 依赖版本与脚本
- `references/structure.md` — 目录结构详解
- `references/auth-api.md` — 鉴权与 API 客户端
- `references/simulator-keyboard-input.md` — 模拟器键盘输入规范
- `references/verification.md` — 验证与发布检查

## Usage Examples

### Example 1

**User:**
帮我基于一个已有后端，从零搭建一个 React Native 移动应用，放到 apps/mobile，包含登录、首页、我的三个 Tab。

**AI:**
我会使用 `rn-app-builder` 帮你一键搭建 `apps/mobile`：
1. 运行脚手架脚本生成 Expo SDK 56 + React Native 0.85 + React 19 基础结构。
2. 配置 `packages/core` 存放用户、首页数据等 DTO。
3. 配置 `packages/api-client` 作为平台无关 HTTP 客户端。
4. 在 `apps/mobile/src/api.ts` 注入 `fetch` + `AsyncStorage`。
5. 实现 `AuthProvider` 做 token 自检与登录状态管理。
6. 用 React Navigation 7 实现 Login → MainTabs（Home / Stats / Profile）。
7. 替换 `app.json`、主题色、API 基地址后即可运行验证。

### Example 2

**User:**
我们的 monorepo 里已经有 web 和小程序了，现在想加一个原生 App，共享类型和 API 请求逻辑，该怎么做？

**AI:**
按 `rn-app-builder` 的 monorepo 模式来做：
1. 在 `packages/core` 定义共享 DTO 与纯函数（web/小程序/App 共用）。
2. 在 `packages/api-client` 定义 `ApiClientAdapters` 接口与业务请求方法。
3. 新增 `apps/mobile`，注入 RN 专属的 `fetch`、`AsyncStorage`、文件上传适配器。
4. App 只写 UI、导航、权限与平台相关代码，业务逻辑复用 `packages/*`。
5. 配置 `tsconfig.json` paths 指向本地 `packages/*/src`。
