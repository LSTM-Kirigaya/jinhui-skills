# Stack

推荐统一使用以下技术栈，保证新项目和已有项目一致。

## 核心依赖

- Expo SDK `~56.0.0`
- React Native `0.85.x`
- React `19.2.x`
- TypeScript `~6.0.x`

## 导航

- `@react-navigation/native`
- `@react-navigation/native-stack`
- `@react-navigation/bottom-tabs`

## 本地存储与权限

- `@react-native-async-storage/async-storage` — token / 用户缓存
- `react-native-safe-area-context`
- `react-native-screens`
- `react-native-svg`

## 图标与 UI

- `lucide-react-native` — 图标
- 自定义 `theme` 目录管理 colors / spacing / radius / shadow

## 常用 Expo 模块

按需安装：

- `expo-constants` — 读取 app.json extra
- `expo-status-bar`
- `expo-file-system`
- `expo-image-picker`
- `expo-clipboard`
- `expo-media-library`

## Package Scripts

```json
{
  "start": "expo start",
  "start:lan": "node ../../scripts/start-mobile-dev.cjs",
  "android": "expo run:android",
  "ios": "expo run:ios",
  "web": "expo start --web",
  "typecheck": "tsc --project tsconfig.typecheck.json --noEmit --pretty false",
  "prebuild": "expo prebuild",
  "build:ios:preview": "npx eas-cli build -p ios --profile preview",
  "build:ios:production": "npx eas-cli build -p ios --profile production"
}
```

## App Config

使用中性默认值，由调用方替换：

- `name`: 调用方提供的应用名
- `slug`: kebab-case 应用名
- `scheme`: kebab-case 应用名或调用方提供的 deeplink scheme
- `ios.bundleIdentifier`: `com.example.mobile`（除非提供）
- `android.package`: 同上
- `extra.apiBaseUrl`: 本地开发基地址，不要写生产域名

不要在 `app.json` 中硬编码密钥、生产域名或项目专属配置。
