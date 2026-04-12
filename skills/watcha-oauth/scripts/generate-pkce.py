#!/usr/bin/env python3
"""生成 PKCE code_verifier 和 code_challenge (S256)"""

import base64
import hashlib
import secrets


def generate_pkce() -> tuple[str, str]:
    """返回 (code_verifier, code_challenge)"""
    verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode("ascii").rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    return verifier, challenge


if __name__ == "__main__":
    verifier, challenge = generate_pkce()
    print(f"code_verifier:  {verifier}")
    print(f"code_challenge: {challenge}")
