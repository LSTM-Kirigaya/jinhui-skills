# Simulator Hardware Keyboard Input

Every screen with text entry must work when a developer clicks into the iOS Simulator or Android Emulator and types from the computer keyboard.

## Code Rules

Use React Native `TextInput` directly unless there is a strong reason to wrap it. Avoid custom numeric keyboards for basic login/forms.

For each editable field:

- Do not set `editable={false}` except during a real disabled/loading state.
- Do not intercept all touches with overlays above the input.
- Set `value` and `onChangeText`.
- Set `autoCorrect={false}` for identifiers, codes, and passwords.
- Set `autoCapitalize="none"` for identifiers and passwords.
- Set an `inputMode` that matches the expected content:
  - `email` for email or account identifiers
  - `numeric` for verification codes and numeric fields
  - `text` or omitted for free text
- Set `keyboardType` as a platform hint, not as the only validation mechanism.
- Set `returnKeyType` and `onSubmitEditing` so hardware Enter moves to the next field or submits.
- Use refs to focus the next input from `onSubmitEditing`.

Example:

```tsx
const passwordRef = useRef<TextInput>(null)

<TextInput
  value={account}
  onChangeText={setAccount}
  autoCapitalize="none"
  autoCorrect={false}
  inputMode="email"
  keyboardType="email-address"
  returnKeyType="next"
  submitBehavior="submit"
  onSubmitEditing={() => passwordRef.current?.focus()}
/>

<TextInput
  ref={passwordRef}
  value={password}
  onChangeText={setPassword}
  autoCapitalize="none"
  autoCorrect={false}
  secureTextEntry
  returnKeyType="done"
  submitBehavior="submit"
  onSubmitEditing={submit}
/>
```

## Simulator Checks

iOS Simulator:

- Enable hardware keyboard in the Simulator menu: `I/O` -> `Keyboard` -> `Connect Hardware Keyboard`.
- Click the field and type letters/numbers from the computer keyboard.
- Press Enter and confirm focus moves or the form submits.

Android Emulator:

- Ensure the emulator allows hardware keyboard input in the AVD settings.
- Click the field and type from the computer keyboard.
- Press Enter and confirm focus moves or the form submits.

## Anti-Patterns

- Relying only on a custom keypad for normal form fields.
- Using `keyboardType="number-pad"` without an `onSubmitEditing` path for hardware Enter.
- Blocking inputs behind full-screen loading overlays that remain mounted after loading ends.
- Putting domain validation in keyboard selection instead of explicit validation.
