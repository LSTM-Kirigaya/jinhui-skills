#!/usr/bin/env python3
"""Create a generic Expo React Native app shell.

This script intentionally writes neutral names and placeholder API settings.
Patch the generated app after reading the target repository.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target app directory, e.g. apps/mobile")
    parser.add_argument("--app-name", default="ExampleApp")
    parser.add_argument("--package-name", default="com.example.mobile")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:3000")
    args = parser.parse_args()

    target = Path(args.target)
    slug = args.app_name.lower().replace(" ", "-")

    package_json = {
        "name": f"@example/{slug}",
        "version": "0.0.0",
        "private": True,
        "main": "index.ts",
        "scripts": {
            "start": "expo start",
            "android": "expo run:android",
            "ios": "expo run:ios",
            "web": "expo start --web",
            "typecheck": "tsc --project tsconfig.typecheck.json --noEmit --pretty false",
        },
        "dependencies": {
            "@react-native-async-storage/async-storage": "2.2.0",
            "@react-navigation/bottom-tabs": "^7.18.0",
            "@react-navigation/native": "^7.3.1",
            "@react-navigation/native-stack": "^7.17.3",
            "expo": "~56.0.0",
            "expo-constants": "~18.0.13",
            "expo-status-bar": "~56.0.4",
            "lucide-react-native": "^1.20.0",
            "react": "19.2.3",
            "react-native": "0.85.3",
            "react-native-safe-area-context": "~5.7.0",
            "react-native-screens": "4.25.2",
            "react-native-svg": "15.15.4",
        },
        "devDependencies": {
            "@types/react": "~19.2.14",
            "babel-preset-expo": "~56.0.15",
            "typescript": "~6.0.3",
        },
    }
    write(target / "package.json", json.dumps(package_json, indent=2))

    app_json = {
        "expo": {
            "name": args.app_name,
            "slug": slug,
            "scheme": slug,
            "version": "0.0.1",
            "orientation": "portrait",
            "userInterfaceStyle": "automatic",
            "ios": {"supportsTablet": True, "bundleIdentifier": args.package_name},
            "android": {"package": args.package_name, "versionCode": 1},
            "extra": {"apiBaseUrl": args.api_base_url},
            "plugins": ["expo-status-bar"],
        }
    }
    write(target / "app.json", json.dumps(app_json, indent=2))

    write(target / "index.ts", "import { registerRootComponent } from 'expo'\nimport App from './App'\n\nregisterRootComponent(App)")
    write(target / "babel.config.js", "module.exports = function (api) {\n  api.cache(true)\n  return { presets: ['babel-preset-expo'] }\n}")
    write(target / "tsconfig.json", '{\n  "extends": "expo/tsconfig.base",\n  "compilerOptions": { "strict": true }\n}')
    write(target / "tsconfig.typecheck.json", '{\n  "extends": "./tsconfig.json",\n  "include": ["App.tsx", "src/**/*.ts", "src/**/*.tsx"]\n}')

    write(target / "App.tsx", """
import { StatusBar } from 'expo-status-bar'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { AuthProvider } from './src/providers/AuthProvider'
import { RootNavigator } from './src/navigation/RootNavigator'

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <RootNavigator />
        <StatusBar style="auto" />
      </AuthProvider>
    </SafeAreaProvider>
  )
}
""")

    write(target / "src/theme/index.ts", """
export const colors = {
  background: '#F8F5F3',
  surface: '#FFFFFF',
  surfaceMuted: '#EEE7E2',
  border: '#E0D7D0',
  text: '#251F1C',
  textSecondary: '#756A64',
  textMuted: '#A99D96',
  brand: '#CF6D4E',
}

export const spacing = { xs: 8, sm: 16, md: 24, lg: 32 }
export const radius = { sm: 8, md: 16, lg: 24 }
""")

    write(target / "src/providers/AuthProvider.tsx", """
import { createContext, useContext, useMemo, useState, type PropsWithChildren } from 'react'

type AuthContextValue = {
  isAuthenticated: boolean
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: PropsWithChildren) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const value = useMemo(() => ({
    isAuthenticated,
    login: () => setIsAuthenticated(true),
    logout: () => setIsAuthenticated(false),
  }), [isAuthenticated])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used within AuthProvider')
  return value
}
""")

    write(target / "src/navigation/RootNavigator.tsx", """
import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { Text, View } from 'react-native'
import { UserRound } from 'lucide-react-native'
import { useAuth } from '../providers/AuthProvider'
import { LoginScreen } from '../screens/LoginScreen'

const Stack = createNativeStackNavigator()
const Tab = createBottomTabNavigator()

function Placeholder({ title }: { title: string }) {
  return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><Text>{title}</Text></View>
}

function Tabs() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Home" options={{ tabBarIcon: ({ color, size }) => <UserRound color={color} size={size} /> }}>
        {() => <Placeholder title="Home" />}
      </Tab.Screen>
    </Tab.Navigator>
  )
}

export function RootNavigator() {
  const { isAuthenticated } = useAuth()
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? <Stack.Screen name="Tabs" component={Tabs} /> : <Stack.Screen name="Login" component={LoginScreen} />}
      </Stack.Navigator>
    </NavigationContainer>
  )
}
""")

    write(target / "src/screens/LoginScreen.tsx", """
import { useRef, useState } from 'react'
import { StyleSheet, Text, TextInput, View } from 'react-native'
import { useAuth } from '../providers/AuthProvider'
import { colors, radius, spacing } from '../theme'

export function LoginScreen() {
  const { login } = useAuth()
  const [account, setAccount] = useState('')
  const [password, setPassword] = useState('')
  const passwordRef = useRef<TextInput>(null)

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Example App</Text>
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
        placeholder="Email or phone"
        style={styles.input}
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
        onSubmitEditing={login}
        placeholder="Password"
        style={styles.input}
      />
      <Text onPress={login} style={styles.button}>Sign in</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, justifyContent: 'center', padding: spacing.sm, gap: spacing.sm, backgroundColor: colors.background },
  title: { color: colors.text, fontSize: 32, fontWeight: '900', textAlign: 'center' },
  input: { minHeight: 52, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, backgroundColor: colors.surface, paddingHorizontal: spacing.sm },
  button: { minHeight: 52, borderRadius: radius.md, overflow: 'hidden', backgroundColor: colors.brand, color: colors.surface, textAlign: 'center', textAlignVertical: 'center', fontWeight: '800' },
})
""")

    print(f"Created Expo React Native app blueprint at {target}")


if __name__ == "__main__":
    main()
