#!/usr/bin/env python3
from __future__ import annotations
"""下载并解压 arXiv 论文的 LaTeX 源码。

用法:
    python3 fetch_arxiv.py <arxiv_id_or_url>

示例:
    python3 fetch_arxiv.py 2601.07372
    python3 fetch_arxiv.py https://arxiv.org/abs/2601.07372
"""

import re
import sys
import tarfile
import urllib.request
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "nanochat" / "knowledge"

# 依次尝试的源码下载地址，前面的优先级更高
SOURCE_URL_PATTERNS = [
    "https://arxiv.org/e-print/{arxiv_id}",
    "https://arxiv.org/src/{arxiv_id}.tar.gz",
    "https://arxiv.org/src/{arxiv_id}",
]


def extract_arxiv_id(value: str) -> str:
    """从 arxiv ID 或 URL 中提取标准 ID。"""
    value = value.strip()
    if m := re.search(r"(\d{4}\.\d{4,5})(v\d+)?", value):
        return m.group(1)
    if m := re.search(r"arxiv\.org/(?:abs|src|pdf|e-print)/([a-zA-Z0-9_.-]+)", value):
        return m.group(1).replace(".pdf", "").split("v")[0]
    raise ValueError(f"无法从输入中提取 arxiv ID: {value}")


def find_main_tex(extract_dir: Path) -> Path | None:
    """在解压目录中定位入口 tex 文件（包含 \\documentclass）。"""
    candidates = []
    for tex_file in extract_dir.rglob("*.tex"):
        try:
            text = tex_file.read_text(encoding="utf-8", errors="ignore")
            if r"\documentclass" in text:
                # 优先选择根目录下的 main.tex 或同名 tex
                rel = tex_file.relative_to(extract_dir)
                score = 0
                if rel.name.lower() == "main.tex":
                    score = 100
                elif rel.parent == Path("."):
                    score = 50
                candidates.append((score, tex_file))
        except Exception:
            continue
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def download(url: str, dest: Path) -> None:
    """将 url 下载到 dest，自动跟随重定向。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    arxiv_id = extract_arxiv_id(sys.argv[1])
    tar_path = CACHE_DIR / f"{arxiv_id}.tar.gz"
    extract_dir = CACHE_DIR / arxiv_id

    if tar_path.exists():
        print(f"源码包已存在: {tar_path}")
    else:
        print(f"正在下载 arxiv:{arxiv_id} 的 LaTeX 源码...")
        last_error = None
        for pattern in SOURCE_URL_PATTERNS:
            url = pattern.format(arxiv_id=arxiv_id)
            try:
                download(url, tar_path)
                print(f"下载成功: {url}")
                break
            except Exception as e:
                last_error = e
                print(f"  尝试失败 {url}: {e}")
        else:
            print(f"所有下载地址均失败: {last_error}", file=sys.stderr)
            return 2

    if not extract_dir.exists():
        print(f"正在解压到: {extract_dir}")
        extract_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(tar_path, "r:gz") as tf:
            tf.extractall(path=extract_dir)
    else:
        print(f"解压目录已存在: {extract_dir}")

    main_tex = find_main_tex(extract_dir)
    print(f"arxiv_id={arxiv_id}")
    print(f"tar_path={tar_path}")
    print(f"extract_dir={extract_dir}")
    if main_tex:
        print(f"main_tex_path={main_tex}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
