# Structure

推荐采用 monorepo 布局，把平台无关逻辑抽到 `packages/*`，原生相关代码保留在 `apps/mobile`。

```text
apps/
  mobile/
    App.tsx
    app.json
    babel.config.js
    metro.config.js
    index.ts
    package.json
    tsconfig.json
    tsconfig.typecheck.json
    src/
      api.ts                 # 创建 apiClient，注入 RN 适配器
      config.ts              # API_BASE_URL、版本号、调试开关
      env.d.ts               # 环境变量类型声明
      components/            # AppButton、Card、Page 等基础组件
      navigation/
        RootNavigator.tsx    # Auth gate：未登录 -> Login，已登录 -> MainTabs
        CustomTabBar.tsx     # 自定义底部 Tab（可选）
        types.ts             # 导航参数类型
      providers/
        AuthProvider.tsx     # 登录状态、token 自检
        DialogProvider.tsx   # 全局弹窗（可选）
      screens/
        LoginScreen.tsx
        HomeScreen.tsx
        ProfileScreen.tsx
        ...                  # 业务页面
      theme/
        index.ts             # colors / spacing / radius / shadow
      hooks/                 # 业务 hooks
      utils/                 # date、image、errors 等工具
packages/
  core/                    # 平台无关：DTO、枚举、纯计算
  api-client/              # 适配器式 HTTP 客户端 + TokenStorage 接口
```

## 职责划分

- `packages/core`: 类型、枚举、纯计算、DTO 契约。web / 小程序 / App 可共用。
- `packages/api-client`: 平台无关的请求构造、错误处理、token 接口、业务方法。
- `apps/mobile/src/api.ts`: 注入 RN 的 `fetch`、文件上传、`AsyncStorage` 等适配器。
- `apps/mobile/src/providers`: 有状态 provider，尤其是 AuthProvider。
- `apps/mobile/src/navigation`: 路由定义与 auth gate。
- `apps/mobile/src/screens`: 原生 UI 页面，保持薄，复用 packages 逻辑。
- `apps/mobile/src/components`: 仅原生可复用组件。

## tsconfig paths

在 `apps/mobile/tsconfig.json` 中指向本地 packages：

```json
{
  "compilerOptions": {
    "paths": {
      "@example/core": ["../../packages/core/src"],
      "@example/api-client": ["../../packages/api-client/src"]
    }
  },
  "include": ["App.tsx", "src", "../../packages/core/src", "../../packages/api-client/src"]
}
```

## Git Ignore

忽略本地/原生构建产物：

```gitignore
apps/mobile/.expo/
apps/mobile/.expo-shared/
apps/mobile/android/.gradle/
apps/mobile/android/app/build/
apps/mobile/ios/build/
```
