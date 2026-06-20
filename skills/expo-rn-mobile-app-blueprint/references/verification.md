# Verification

Run checks from the repo root unless the repo documents otherwise.

## Minimum Checks

```bash
npm install
npm --workspace apps/mobile run typecheck
npx expo export --platform ios --output-dir /tmp/mobile-ios-export --clear
```

If the repo has broader gates, also run them:

```bash
npm run lint
npm run typecheck
npm test
```

## Runtime Check

Start Expo:

```bash
npm --workspace apps/mobile run start
```

or, when the repo provides a LAN-aware wrapper:

```bash
npm run dev:mobile
```

Confirm:

- Metro starts without dependency resolution errors.
- The unauthenticated app opens on the login screen.
- Clicking into inputs accepts computer keyboard input in simulator/emulator.
- Enter moves focus or submits.
- Auth bootstrap does not flash the wrong screen after a stored token exists.

## Common Fixes

- Missing Expo preset: install `babel-preset-expo` in the mobile workspace.
- Workspace module resolution issues: configure Metro watch folders and resolver paths for root `node_modules`.
- Simulator cannot reach localhost API:
  - iOS simulator can usually use `127.0.0.1`.
  - Android emulator often needs `10.0.2.2` or a LAN IP.
  - Physical devices need a LAN IP and a firewall-open API port.
