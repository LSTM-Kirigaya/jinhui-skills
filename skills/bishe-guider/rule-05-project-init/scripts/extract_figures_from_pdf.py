#!/usr/bin/env python3
"""
extract_figures_from_pdf.py
从 PDF 文档中提取嵌入的图片

用法:
    python extract_figures_from_pdf.py input.pdf --output ./extracted_images/

支持格式:
    - 直接嵌入的图像对象
    - 生成 PNG 文件
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("错误: 需要 PyMuPDF。请运行: pip install PyMuPDF")
    sys.exit(1)


def extract_images_from_pdf(pdf_path: str, output_dir: str, min_size: int = 100) -> int:
    """
    从 PDF 中提取所有嵌入图片

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
        min_size: 最小图片尺寸（像素），过滤过小的图标

    Returns:
        提取的图片数量
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    extracted = 0
    seen_images = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images, start=1):
            xref = img[0]

            # 去重：同一 xref 在不同页面可能重复出现
            if xref in seen_images:
                continue
            seen_images.add(xref)

            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image["width"]
            height = base_image["height"]

            # 过滤过小图片（通常是图标或装饰元素）
            if width < min_size or height < min_size:
                continue

            # 生成文件名
            filename = f"page{page_num + 1}_img{img_index}_{width}x{height}.{image_ext}"
            filepath = output_path / filename

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            extracted += 1
            print(f"  [{extracted}] {filename} ({width}x{height}, {len(image_bytes)} bytes)")

    doc.close()
    return extracted


def main():
    parser = argparse.ArgumentParser(description="从 PDF 中提取嵌入的图片")
    parser.add_argument("pdf", help="输入 PDF 文件路径")
    parser.add_argument("-o", "--output", default="./extracted_images", help="输出目录")
    parser.add_argument("--min-size", type=int, default=100, help="最小图片尺寸（默认 100px）")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"错误: 文件不存在: {args.pdf}")
        sys.exit(1)

    print(f"提取图片: {args.pdf}")
    print(f"输出目录: {args.output}")
    print("-" * 50)

    count = extract_images_from_pdf(args.pdf, args.output, args.min_size)

    print("-" * 50)
    if count > 0:
        print(f"完成: 共提取 {count} 张图片")
    else:
        print("未提取到图片（PDF 中可能没有嵌入图片，或图片被矢量化）")


if __name__ == "__main__":
    main()
