# Structure

Use an apps monorepo layout:

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
      api.ts
      config.ts
      env.d.ts
      components/
        AppButton.tsx
        Page.tsx
        SectionCard.tsx
      navigation/
        RootNavigator.tsx
        types.ts
      providers/
        AuthProvider.tsx
      screens/
        LoginScreen.tsx
        TrainingScreen.tsx
        ExploreScreen.tsx
        KnowledgeScreen.tsx
        ToolboxScreen.tsx
        ProfileScreen.tsx
      theme/
        index.ts
packages/
  core/
  api-client/
```

## What Goes Where

- `packages/core`: platform-neutral types, enums, pure calculations, DTO contracts.
- `packages/api-client`: adapter-based HTTP client and token-storage contract.
- `apps/mobile/src/api.ts`: React Native adapters for fetch and AsyncStorage.
- `apps/mobile/src/providers`: stateful app providers, especially auth/session bootstrap.
- `apps/mobile/src/navigation`: auth-gated root stack and main bottom tabs.
- `apps/mobile/src/screens`: native UI screens; do not import mini-program APIs.
- `apps/mobile/src/components`: reusable native components only.

## Migration Rules

- Move pure logic out of mini-program pages before reusing it.
- Do not import Taro, DOM APIs, browser storage, or mini-program globals into the mobile app.
- Replace platform capabilities with React Native or Expo modules:
  - storage -> AsyncStorage
  - image/video pickers -> Expo modules
  - file access -> `expo-file-system`
  - clipboard -> `expo-clipboard`
  - navigation -> React Navigation
- Keep native screens thin and move shared request/formatting logic into packages.

## Git Ignore

Ignore local/native build state:

```gitignore
apps/mobile/.expo/
apps/mobile/.expo-shared/
apps/mobile/android/.gradle/
apps/mobile/android/app/build/
apps/mobile/ios/build/
```
