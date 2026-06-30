#!/usr/bin/env python3
"""知乎 OAuth 2.0 接入示例 (Python)"""

import os
import urllib.parse
import requests

# ========== 配置（建议从环境变量读取） ==========
ZHIHU_APP_ID = os.environ.get("ZHIHU_APP_ID", "your_app_id")
ZHIHU_APP_KEY = os.environ.get("ZHIHU_APP_KEY", "your_app_key")
ZHIHU_REDIRECT_URI = os.environ.get("ZHIHU_REDIRECT_URI", "https://yourdomain.com/callback")
# ================================================


def build_authorize_url(redirect_uri: str | None = None, state: str | None = None) -> str:
    """生成知乎授权跳转 URL"""
    params = {
        "redirect_uri": redirect_uri or ZHIHU_REDIRECT_URI,
        "app_id": ZHIHU_APP_ID,
        "response_type": "code",
    }
    if state:
        params["state"] = state
    return "https://openapi.zhihu.com/authorize?" + urllib.parse.urlencode(params)


def exchange_code(code: str, redirect_uri: str | None = None) -> dict:
    """使用授权码换取 access_token"""
    payload = {
        "app_id": ZHIHU_APP_ID,
        "app_key": ZHIHU_APP_KEY,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri or ZHIHU_REDIRECT_URI,
        "code": code,
    }
    resp = requests.post("https://openapi.zhihu.com/access_token", json=payload)
    resp.raise_for_status()
    return resp.json()


def get_userinfo(access_token: str) -> dict:
    """获取当前登录用户信息"""
    resp = requests.get(
        "https://openapi.zhihu.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp.raise_for_status()
    return resp.json()


def get_followers(access_token: str, page: int = 0, per_page: int = 10) -> dict:
    """获取粉丝列表"""
    resp = requests.get(
        "https://openapi.zhihu.com/user/followers",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": page, "per_page": per_page},
    )
    resp.raise_for_status()
    return resp.json()


def get_followed(access_token: str, page: int = 0, per_page: int = 10) -> dict:
    """获取关注列表"""
    resp = requests.get(
        "https://openapi.zhihu.com/user/followed",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": page, "per_page": per_page},
    )
    resp.raise_for_status()
    return resp.json()


def get_moments(access_token: str, page: int = 0, per_page: int = 10) -> dict:
    """获取关注动态"""
    resp = requests.get(
        "https://openapi.zhihu.com/user/moments",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": page, "per_page": per_page},
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("用法示例：")
    print("1. 调用 build_authorize_url(state=your_state) 生成授权链接")
    print("2. 用户在回调中返回 code 后，调用 exchange_code(code) 换取 token")
    print("3. 使用 access_token 调用 get_userinfo() 获取用户信息")
