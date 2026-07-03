#!/usr/bin/env python3
from __future__ import annotations
"""扫描 LaTeX 源码中的图片引用，复制到测试工作区并统一转换为 PNG。

用法:
    python3 copy_figures.py <arxiv_id> <workspace_dir>

示例:
    python3 copy_figures.py 2606.32034 test-skills/read-paper/output
"""

import json
import re
import shutil
import subprocess
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
    candidates = []
    if source_tex.is_file():
        candidates.append(source_tex.parent / raw_name)
    candidates.append(extract_dir / raw_name)

    has_ext = Path(raw_name).suffix.lower() in IMAGE_EXTENSIONS
    search_paths = []
    for cand in candidates:
        search_paths.append(cand)
        if not has_ext:
            for ext in IMAGE_EXTENSIONS:
                search_paths.append(Path(str(cand) + ext))

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


def safe_stem(name: str) -> str:
    """生成仅含安全字符的文件名 stem。"""
    stem = Path(name).stem
    return re.sub(r"[^\w\-]", "_", stem)


def convert_to_png(src: Path, dest: Path) -> bool:
    """把任意支持格式的图片转换为 PNG。优先使用 macOS 内置 sips，其次 poppler/ImageMagick。"""
    dest.parent.mkdir(parents=True, exist_ok=True)

    # 1. sips（macOS 内置，支持 PDF/EPS/PNG/JPG）
    if shutil.which("sips"):
        try:
            subprocess.run(
                ["sips", "-s", "format", "png", str(src), "--out", str(dest)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
            if dest.exists():
                return True
        except Exception:
            pass

    # 2. pdftoppm（poppler，适合 PDF）
    if src.suffix.lower() == ".pdf" and shutil.which("pdftoppm"):
        try:
            tmp_prefix = dest.with_suffix("")
            subprocess.run(
                ["pdftoppm", "-png", str(src), str(tmp_prefix)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
            # pdftoppm 生成 {prefix}-1.png
            candidate = Path(f"{tmp_prefix}-1.png")
            if candidate.exists():
                shutil.move(str(candidate), str(dest))
                # 清理可能产生的多余页
                for extra in tmp_prefix.parent.glob(f"{tmp_prefix.name}-*.png"):
                    extra.unlink()
                return True
        except Exception:
            pass

    # 3. ImageMagick convert
    if shutil.which("convert"):
        try:
            subprocess.run(
                ["convert", str(src), str(dest)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
            if dest.exists():
                return True
        except Exception:
            pass

    return False


def prepare_png_asset(src: Path, assets_dir: Path, used_names: dict[str, int]) -> tuple[str, Path] | None:
    """把源文件处理成 assets 目录下的 PNG 文件，返回最终相对路径和文件路径。"""
    stem = safe_stem(src.name)
    counter = used_names.get(stem, 0)
    if counter == 0:
        dest_name = f"{stem}.png"
    else:
        dest_name = f"{stem}_{counter}.png"
    used_names[stem] = counter + 1

    dest = assets_dir / dest_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    if src.suffix.lower() == ".png":
        shutil.copy2(src, dest)
    else:
        if not convert_to_png(src, dest):
            return None

    return f"assets/{dest_name}", dest


def copy_and_convert_assets(refs: list[dict], extract_dir: Path, assets_dir: Path) -> tuple[list[dict], list[str]]:
    """复制/转换图片到 assets 目录，最终只保留 PNG。"""
    # 清空旧资源，避免残留 PDF 等非 PNG 文件
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
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

        rel_path = prepare_png_asset(src, assets_dir, used_names)
        if not rel_path:
            missing.append(raw)
            continue

        relative_path, dest_path = rel_path
        results.append({
            "original": raw,
            "original_filename": src.name,
            "relative_path": relative_path,
            "type": "png",
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
    figures, missing = copy_and_convert_assets(refs, extract_dir, assets_dir)

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
