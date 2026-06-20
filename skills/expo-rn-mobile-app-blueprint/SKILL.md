---
name: expo-rn-blueprint
description: 在 monorepo 中搭建或迁移 Expo React Native 移动应用的蓝图。支持共享包、鉴权路由、模拟器硬件键盘输入，以及小程序到原生应用的迁移规范。
tags: ["expo", "react-native", "mobile-app", "monorepo", "mini-program"]
model: deepseek-chat
rootUrl: https://cdn.jsdelivr.net/gh/LSTM-Kirigaya/jinhui-skills@main/skills/expo-rn-mobile-app-blueprint/SKILL.md
---

# Expo RN Mobile App Blueprint

## Goal

Create a production-shaped Expo React Native app that can live beside other app surfaces in a monorepo and can be used as the target for future mini-program or web feature migrations.

This skill is intentionally generic. Do not copy customer names, company names, bundle identifiers, internal API hosts, secrets, brand text, or domain-specific business data into new output. Replace all identities with caller-provided values or neutral placeholders.

## Workflow

1. Inspect the existing repo structure and package manager.
2. Create or update an `apps/mobile/` Expo app using the stack in `references/stack.md`.
3. Add shared platform-neutral code under `packages/*` when the repo has reusable types, calculations, or API clients.
4. Implement the app shell using the directory map in `references/structure.md`.
5. Implement API/auth using `references/auth-api.md`.
6. Ensure all editable fields follow `references/simulator-keyboard-input.md`.
7. Verify with `references/verification.md`.
8. Document migration rules so future agents know what belongs in shared packages versus native screens.

## Fast Scaffold

When starting from an empty app folder, use:

```bash
python3 scripts/create-expo-rn-app-blueprint.py --target apps/mobile --app-name ExampleApp --package-name com.example.mobile
```

Then adapt labels, colors, routes, and API endpoints to the caller's project. The scaffold is a starting point, not a substitute for reading the existing codebase.

## References

- Read `references/stack.md` before choosing dependencies or versions.
- Read `references/structure.md` before creating files or moving surfaces under `apps/`.
- Read `references/auth-api.md` when wiring login, token storage, API clients, or shared packages.
- Read `references/simulator-keyboard-input.md` whenever the app has `TextInput` fields or must support computer keyboard input in iOS Simulator / Android Emulator.
- Read `references/verification.md` before finalizing.

## Usage Examples

### Example 1

**User:**
我有一个现有的 Taro 微信小程序 monorepo，现在想并行开发一个 Expo React Native 原生应用，把小程序里的课程、训练、探索、知识库、工具箱、我的这几个页面迁过去。请帮我搭一个完整的 apps/mobile 骨架。

**AI:**
我会按 `expo-rn-mobile-app-blueprint` 的规范帮你搭建 `apps/mobile`：
1. 使用 Expo SDK 56 / React Native 0.85 / React 19 技术栈。
2. 采用 `apps/mobile/` + `packages/core/` + `packages/api-client/` 的 monorepo 布局。
3. 用 React Navigation 7 实现 auth-gated 根栈与底部 Tab。
4. 把小程序里的纯逻辑、DTO、枚举抽到 `packages/core`，页面 UI 放在 `apps/mobile/src/screens`。
5. 用 AsyncStorage 做 token 缓存，所有 `TextInput` 按模拟器硬件键盘规范处理。
6. 最后运行 typecheck 与 Expo export 验证。

### Example 2

**User:**
帮我生成一个空白的 Expo React Native 应用脚手架，放到 apps/mobile 目录，应用名叫 CoachApp，包名 com.coachlink.app。

**AI:**
可以直接使用本 skill 提供的脚手架脚本：
```bash
python3 scripts/create-expo-rn-app-blueprint.py --target apps/mobile --app-name CoachApp --package-name com.coachlink.app
```
执行后会得到 `apps/mobile/` 的基础骨架。生成后请替换 `app.json` 里的 `extra.apiBaseUrl` 为本地开发地址，并根据业务调整 screens、theme 和 api 适配。
