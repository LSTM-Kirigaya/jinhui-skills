#!/usr/bin/env python3
from __future__ import annotations
"""扫描 LaTeX 源码中的图片引用并复制到测试工作区。

用法:
    python3 copy_figures.py <arxiv_id> <workspace_dir>

示例:
    python3 copy_figures.py 2606.32034 test-skills/read-paper/output
"""

import json
import re
import shutil
import sys
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "nanochat" / "knowledge"
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf", ".eps"]
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def find_graphics(extract_dir: Path) -> list[dict]:
    """遍历所有 .tex 文件，提取 \\includegraphics 引用的文件名。"""
    refs = []
    seen = set()
    for tex_file in extract_dir.rglob("*.tex"):
        try:
            text = tex_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in GRAPHICS_RE.finditer(text):
            raw = m.group(1).strip()
            if raw in seen:
                continue
            seen.add(raw)
            refs.append({
                "original": raw,
                "source_tex": str(tex_file),
            })
    return refs


def resolve_file(extract_dir: Path, raw_name: str, source_tex: Path) -> Path | None:
    """解析图片文件在解压目录中的真实路径。"""
    # 优先按原始路径（相对当前 tex 或根目录）查找
    candidates = []
    if source_tex.is_file():
        candidates.append(source_tex.parent / raw_name)
    candidates.append(extract_dir / raw_name)

    # 若原始路径无扩展名，尝试补全常见扩展名
    has_ext = Path(raw_name).suffix.lower() in IMAGE_EXTENSIONS
    search_paths = []
    for cand in candidates:
        search_paths.append(cand)
        if not has_ext:
            for ext in IMAGE_EXTENSIONS:
                search_paths.append(Path(str(cand) + ext))

    # 同时尝试仅按 basename 在解压目录全局搜索（处理子目录歧义）
    basename = Path(raw_name).name
    if not has_ext:
        for ext in IMAGE_EXTENSIONS:
            search_paths.extend(extract_dir.rglob(basename + ext))
    else:
        search_paths.extend(extract_dir.rglob(basename))

    for cand in search_paths:
        if cand.is_file():
            return cand.resolve()
    return None


def safe_basename(path: Path) -> str:
    """生成仅含安全字符的文件名。"""
    name = path.name
    # 保留字母、数字、点、下划线、连字符
    return re.sub(r"[^\w.\-]", "_", name)


def copy_assets(refs: list[dict], extract_dir: Path, assets_dir: Path) -> list[dict]:
    """复制图片到 assets 目录，返回带 relative_path 的清单。"""
    assets_dir.mkdir(parents=True, exist_ok=True)
    used_names: dict[str, int] = {}
    results = []
    missing = []

    for ref in refs:
        raw = ref["original"]
        source_tex = Path(ref["source_tex"])
        src = resolve_file(extract_dir, raw, source_tex)
        if not src:
            missing.append(raw)
            continue

        base = safe_basename(src)
        name = Path(base).stem
        ext = Path(base).suffix
        # 处理重名
        counter = used_names.get(base, 0)
        if counter == 0:
            dest_name = base
        else:
            dest_name = f"{name}_{counter}{ext}"
        used_names[base] = counter + 1

        dest = assets_dir / dest_name
        shutil.copy2(src, dest)

        file_type = Path(dest_name).suffix.lower().lstrip(".") or "unknown"
        results.append({
            "original": raw,
            "original_filename": src.name,
            "relative_path": f"assets/{dest_name}",
            "type": file_type,
            "found": True,
        })

    return results, missing


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    arxiv_id = sys.argv[1]
    workspace_dir = Path(sys.argv[2])
    extract_dir = CACHE_DIR / arxiv_id
    if not extract_dir.exists():
        print(f"未找到解压目录: {extract_dir}", file=sys.stderr)
        return 2

    assets_dir = workspace_dir / "assets"
    refs = find_graphics(extract_dir)
    figures, missing = copy_assets(refs, extract_dir, assets_dir)

    manifest = {
        "arxiv_id": arxiv_id,
        "workspace_dir": str(workspace_dir),
        "assets_dir": "assets",
        "figures": figures,
        "missing": missing,
    }

    manifest_path = workspace_dir / "figure_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"figure_count={len(figures)}")
    print(f"missing_count={len(missing)}")
    print(f"manifest_path={manifest_path}")
    if missing:
        print(f"missing_files={','.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
