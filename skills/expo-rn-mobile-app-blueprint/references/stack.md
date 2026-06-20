# Stack

Use this stack when the user asks for the same technical approach:

- Expo SDK `~56.0.0`
- React Native `0.85.x`
- React `19.2.x`
- TypeScript
- React Navigation 7:
  - `@react-navigation/native`
  - `@react-navigation/native-stack`
  - `@react-navigation/bottom-tabs`
- `@react-native-async-storage/async-storage` for local token/session cache
- `react-native-safe-area-context`
- `react-native-screens`
- `react-native-svg`
- `lucide-react-native` for icons
- Expo modules commonly needed by feature migrations:
  - `expo-constants`
  - `expo-status-bar`
  - `expo-file-system`
  - `expo-image-picker`
  - `expo-clipboard`

## Package Scripts

Provide scripts similar to:

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

Use neutral defaults until the user gives real identifiers:

- `name`: caller-provided product name
- `slug`: kebab-case app name
- `scheme`: kebab-case app name or caller-provided deep-link scheme
- `ios.bundleIdentifier`: `com.example.mobile` unless provided
- `android.package`: same reverse-DNS identifier unless provided
- `extra.apiBaseUrl`: local development base URL only, never a private production host

Do not hard-code secrets or internal domains in `app.json`.
