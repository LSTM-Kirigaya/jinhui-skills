#!/usr/bin/env python3
from __future__ import annotations
"""将 read-paper 生成的中文博客 JSON 与 PNG 资源发布到远程接口。

用法:
    export READ_PAPER_PUBLISH_URL=https://api.example.com/v1/papers/publish
    export READ_PAPER_UPLOAD_URL=https://api.example.com/v1/papers/upload   # 可选
    export READ_PAPER_PUBLISH_TOKEN=your_token                              # 可选

    python3 publish_blog.py <blog_json_path>

示例:
    python3 publish_blog.py test-skills/read-paper/output/blog_2606.32034.json
"""

import json
import os
import posixpath
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]


def load_env() -> tuple[str, str, str | None]:
    """读取环境变量并校验。"""
    publish_url = os.environ.get("READ_PAPER_PUBLISH_URL", "").strip()
    if not publish_url:
        print("错误：未设置 READ_PAPER_PUBLISH_URL", file=sys.stderr)
        sys.exit(2)

    upload_url = os.environ.get("READ_PAPER_UPLOAD_URL", "").strip()
    if not upload_url:
        upload_url = derive_upload_url(publish_url)

    token = os.environ.get("READ_PAPER_PUBLISH_TOKEN", "").strip() or None
    return publish_url, upload_url, token


def derive_upload_url(publish_url: str) -> str:
    """从发布 URL 派生上传 URL：取目录路径追加 /upload。"""
    parsed = urlparse(publish_url)
    base = posixpath.dirname(parsed.path)
    new_path = posixpath.join(base, "upload")
    return f"{parsed.scheme}://{parsed.netloc}{new_path}"


def auth_header(token: str | None) -> list[str]:
    """返回 curl 用的认证 header 参数。"""
    if token:
        return ["-H", f"Authorization: Bearer {token}"]
    return []


def curl_json(method: str, url: str, extra_args: list[str], token: str | None) -> dict:
    """使用 curl 发送请求并解析 JSON 响应。"""
    cmd = [
        "curl", "-s", "-S", "-L", "-X", method,
        *auth_header(token),
        *extra_args,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"curl 失败: {result.stderr.strip()}")
    return json.loads(result.stdout)


def upload_asset(file_path: Path, upload_url: str, arxiv_id: str, token: str | None) -> str:
    """上传单个 PNG 资源，返回远程 URL。"""
    extra = [
        "-F", f"file=@{file_path}",
        "-F", f"arxiv_id={arxiv_id}",
        "-F", f"filename={file_path.name}",
    ]
    resp = curl_json("POST", upload_url, extra, token)
    if not resp.get("success"):
        error = resp.get("error", "unknown error")
        raise RuntimeError(error)
    remote_url = resp.get("url") or resp.get("remote_url")
    if not remote_url:
        raise RuntimeError("上传接口未返回 url/remote_url")
    return remote_url


def discover_assets(workspace_dir: Path) -> list[Path]:
    """扫描 assets 目录下所有 PNG 文件。"""
    assets_dir = workspace_dir / "assets"
    if not assets_dir.exists():
        return []
    return sorted(p for p in assets_dir.rglob("*") if p.is_file() and p.suffix.lower() == ".png")


def upload_all_assets(
    workspace_dir: Path,
    upload_url: str,
    arxiv_id: str,
    token: str | None,
) -> dict[str, str]:
    """上传全部 PNG 资源，返回 relative_path -> remote_url 映射。"""
    assets = discover_assets(workspace_dir)
    total = len(assets)
    url_map: dict[str, str] = {}

    for idx, file_path in enumerate(assets, start=1):
        relative_path = f"assets/{file_path.name}"
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                remote_url = upload_asset(file_path, upload_url, arxiv_id, token)
                url_map[relative_path] = remote_url
                print(f"upload_progress={idx}/{total} file={relative_path} status=success remote={remote_url}")
                break
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    wait = BACKOFF_SECONDS[attempt]
                    print(f"upload_progress={idx}/{total} file={relative_path} status=retry attempt={attempt+1} wait={wait}s error={e}")
                    time.sleep(wait)
                else:
                    print(f"upload_progress={idx}/{total} file={relative_path} status=failed error={e}")
        else:
            print(f"错误：资源上传失败，终止发布流程: {last_error}", file=sys.stderr)
            sys.exit(3)

    return url_map


def patch_blog_json(blog: dict, url_map: dict[str, str]) -> dict:
    """改写 blog JSON：为每个 figure 增加 remote_url，顶层增加 arxiv 对象。"""
    arxiv_id = blog.get("arxiv_id", "")
    blog.setdefault("arxiv", {})
    blog["arxiv"] = {
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "html_url": f"https://arxiv.org/html/{arxiv_id}",
        "source_url": f"https://arxiv.org/e-print/{arxiv_id}",
    }

    for chapter in blog.get("chapters", []):
        for figure in chapter.get("figures", []):
            rel = figure.get("relative_path", "")
            if rel in url_map:
                figure["remote_url"] = url_map[rel]

    return blog


def save_patched_json(blog: dict, json_path: Path) -> Path:
    """保存改写后的 JSON 到本地。"""
    out_path = json_path.parent / f"{json_path.stem}_published.json"
    out_path.write_text(json.dumps(blog, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def publish_blog(blog: dict, publish_url: str, token: str | None, json_path: Path) -> dict:
    """POST 最终 JSON 到发布接口。"""
    print("publish_status=pending")
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            if shutil.which("curl"):
                # 写入临时文件避免命令行过长
                tmp_path = json_path.parent / ".publish_payload.json"
                tmp_path.write_text(json.dumps(blog, ensure_ascii=False), encoding="utf-8")
                extra = [
                    "-H", "Content-Type: application/json",
                    "-d", f"@{tmp_path}",
                ]
                resp = curl_json("POST", publish_url, extra, token)
            else:
                # 无 curl 时的回退（仅支持简单 POST，无 multipart）
                req = urllib.request.Request(
                    publish_url,
                    data=json.dumps(blog, ensure_ascii=False).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                if token:
                    req.add_header("Authorization", f"Bearer {token}")
                with urllib.request.urlopen(req, timeout=120) as r:
                    resp = json.loads(r.read().decode("utf-8"))

            if not resp.get("success"):
                error = resp.get("error", "unknown error")
                raise RuntimeError(error)
            return resp
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = BACKOFF_SECONDS[attempt]
                print(f"publish_status=retry attempt={attempt+1} wait={wait}s error={e}")
                time.sleep(wait)
            else:
                print(f"错误：发布 POST 失败: {last_error}", file=sys.stderr)
                saved = save_patched_json(blog, json_path)
                print(f"已保存改写后的 JSON: {saved}")
                sys.exit(4)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"JSON 文件不存在: {json_path}", file=sys.stderr)
        return 1

    publish_url, upload_url, token = load_env()
    print(f"publish_url={publish_url}")
    print(f"upload_url={upload_url}")

    blog = json.loads(json_path.read_text(encoding="utf-8"))
    arxiv_id = blog.get("arxiv_id", "")
    workspace_dir = json_path.parent

    assets = discover_assets(workspace_dir)
    print(f"asset_count={len(assets)}")

    url_map = upload_all_assets(workspace_dir, upload_url, arxiv_id, token)
    blog = patch_blog_json(blog, url_map)
    resp = publish_blog(blog, publish_url, token, json_path)

    published_url = resp.get("publishedUrl") or resp.get("published_url") or resp.get("url")
    post_id = resp.get("postId") or resp.get("post_id")
    print(f"publish_status=success published_url={published_url} post_id={post_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
