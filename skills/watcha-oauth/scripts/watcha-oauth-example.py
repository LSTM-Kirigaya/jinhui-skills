#!/usr/bin/env python3
"""观猹 OAuth2.0 接入示例 (Python)"""

import urllib.parse
import requests

# ========== 配置 ==========
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"  # 公开客户端可不填
REDIRECT_URI = "https://myapp.com/callback"
SCOPE = "read email"
# ==========================


def build_authorize_url(code_challenge: str) -> str:
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "random_string",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return "https://watcha.cn/oauth/authorize?" + urllib.parse.urlencode(params)


def exchange_code(code: str, code_verifier: str | None = None) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
    }
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET
    if code_verifier:
        data["code_verifier"] = code_verifier

    resp = requests.post("https://watcha.cn/oauth/api/token", data=data)
    resp.raise_for_status()
    return resp.json()


def refresh_token(refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    resp = requests.post("https://watcha.cn/oauth/api/token", data=data)
    resp.raise_for_status()
    return resp.json()


def get_userinfo(access_token: str) -> dict:
    resp = requests.get(
        "https://watcha.cn/oauth/api/userinfo",
        params={"access_token": access_token},
    )
    resp.raise_for_status()
    return resp.json()


def introspect(token: str, token_type_hint: str = "access_token") -> dict:
    data = {
        "token": token,
        "token_type_hint": token_type_hint,
    }
    resp = requests.post("https://watcha.cn/oauth/api/introspect", data=data)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    # 示例：仅展示函数用法，实际需在 Web 框架中分步调用
    print("用法示例：")
    print("1. 生成 PKCE 参数后调用 build_authorize_url() 获取授权链接")
    print("2. 用户在回调中返回 code 后，调用 exchange_code() 换取 token")
    print("3. 使用 access_token 调用 get_userinfo() 获取用户信息")
