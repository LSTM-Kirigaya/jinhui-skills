# Verification

在仓库根目录运行验证命令。

## 最小检查

```bash
npm install
npm --workspace apps/mobile run typecheck
npx expo export --platform ios --output-dir /tmp/mobile-ios-export --clear
```

如果仓库有更严格的门禁，也一并运行：

```bash
npm run lint
npm run typecheck
npm test
```

## 运行时检查

启动 Expo：

```bash
npm --workspace apps/mobile run start
```

或指定平台：

```bash
npm --workspace apps/mobile run ios
npm --workspace apps/mobile run android
```

确认：

- Metro 启动无依赖解析错误。
- 未登录时打开 Login 页面。
- 已登录时打开 MainTabs 首页。
- `TextInput` 可在 iOS Simulator / Android Emulator 中用电脑键盘输入。
- 回车可聚焦下一输入框或提交表单。
- 登录后 token 正确写入 AsyncStorage，重启后保持登录态。
- 接口基地址指向正确的开发环境（非生产域名）。

## 常见修复

- 缺少 Expo preset：安装 `babel-preset-expo`。
- Workspace 模块解析失败：检查 `metro.config.js` 与 `tsconfig.json` 的 paths。
- iOS Simulator 无法访问 localhost API：通常使用 `127.0.0.1`。
- Android Emulator 无法访问 localhost API：使用 `10.0.2.2` 或 LAN IP。
- 物理设备需要 LAN IP 与防火墙放行端口。
