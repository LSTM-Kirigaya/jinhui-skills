#!/usr/bin/env python3
"""
论文图片颜色分布一致性检查脚本

功能：
1. 提取指定目录下所有图片的主色调分布
2. 计算图片间的颜色相似度
3. 生成 HTML 报告，标记颜色风格差异较大的图片

支持的格式：PNG, JPG, JPEG, PDF
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np

try:
    from PIL import Image
    import matplotlib.pyplot as plt
    from matplotlib.colors import rgb_to_hsv
except ImportError:
    print("缺少依赖，请安装: pip install Pillow matplotlib numpy")
    sys.exit(1)


def pdf_to_image(pdf_path: str, dpi: int = 150) -> Image.Image:
    """将 PDF 转换为图片（需要 pdf2image 或 PyMuPDF）"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        page = doc[0]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    except ImportError:
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=dpi)
            return images[0]
        except ImportError:
            raise ImportError(
                "处理 PDF 需要 PyMuPDF (pip install PyMuPDF) "
                "或 pdf2image (pip install pdf2image)"
            )


def load_image(path: str) -> Image.Image:
    """加载图片，支持 PDF 格式"""
    ext = Path(path).suffix.lower()
    if ext == '.pdf':
        return pdf_to_image(path)
    return Image.open(path).convert('RGB')


def extract_color_features(img: Image.Image) -> Dict:
    """
    提取图片颜色特征

    返回：
        - dominant_hue: 主色调（HSV 中的 H）
        - saturation_mean: 平均饱和度
        - value_mean: 平均明度
        - hue_histogram: 色调直方图（36 个 bin）
        - color_palette: 主要颜色（K-means 聚类）
    """
    # 缩小图片以加速处理
    img_small = img.resize((200, 200))
    rgb = np.array(img_small) / 255.0
    hsv = rgb_to_hsv(rgb.reshape(-1, 3)).reshape(200, 200, 3)

    # 提取 H, S, V 通道
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # 计算主色调（排除低饱和度像素，避免白色/灰色干扰）
    valid_mask = s > 0.1
    if valid_mask.sum() > 0:
        dominant_hue = np.median(h[valid_mask])
    else:
        dominant_hue = 0.0

    # 色调直方图
    hue_hist, _ = np.histogram(
        h[valid_mask] if valid_mask.sum() > 0 else h,
        bins=36, range=(0, 1)
    )
    hue_hist = hue_hist / hue_hist.sum() if hue_hist.sum() > 0 else hue_hist

    # K-means 聚类提取主色
    pixels = rgb.reshape(-1, 3)
    # 随机采样加速
    if len(pixels) > 5000:
        idx = np.random.choice(len(pixels), 5000, replace=False)
        pixels = pixels[idx]

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(pixels)
    palette = kmeans.cluster_centers_
    labels = kmeans.labels_
    palette_ratio = np.bincount(labels, minlength=5) / len(labels)

    return {
        'dominant_hue': dominant_hue,
        'saturation_mean': float(s.mean()),
        'value_mean': float(v.mean()),
        'hue_histogram': hue_hist,
        'color_palette': palette,
        'palette_ratio': palette_ratio
    }


def color_similarity(feat1: Dict, feat2: Dict) -> float:
    """计算两张图片的颜色相似度（0-1，越高越相似）"""
    # 色调直方图相似度（余弦相似度）
    h1 = feat1['hue_histogram']
    h2 = feat2['hue_histogram']
    hist_sim = np.dot(h1, h2) / (np.linalg.norm(h1) * np.linalg.norm(h2) + 1e-8)

    # 饱和度差异
    sat_diff = abs(feat1['saturation_mean'] - feat2['saturation_mean'])
    sat_sim = max(0, 1 - sat_diff)

    # 明度差异
    val_diff = abs(feat1['value_mean'] - feat2['value_mean'])
    val_sim = max(0, 1 - val_diff)

    # 综合相似度
    similarity = 0.5 * hist_sim + 0.25 * sat_sim + 0.25 * val_sim
    return float(similarity)


def generate_report(
    image_paths: List[str],
    features: List[Dict],
    similarities: np.ndarray,
    output_path: str
) -> None:
    """生成 HTML 报告"""

    n = len(image_paths)
    names = [Path(p).name for p in image_paths]

    # 计算每幅图与其他图的平均相似度
    avg_sims = []
    for i in range(n):
        others = [j for j in range(n) if j != i]
        avg_sim = similarities[i, others].mean() if others else 1.0
        avg_sims.append(avg_sim)

    # 标记异常（相似度低于阈值）
    THRESHOLD = 0.6
    anomalies = [i for i, sim in enumerate(avg_sims) if sim < THRESHOLD]

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>论文图片颜色一致性检查报告</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
    h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
    h2 {{ color: #555; margin-top: 30px; }}
    .summary {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .anomaly {{ border-left: 4px solid #f44336; background: #ffebee; }}
    .normal {{ border-left: 4px solid #4CAF50; background: #e8f5e9; }}
    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
    th {{ background: #4CAF50; color: white; }}
    tr:hover {{ background: #f5f5f5; }}
    .palette {{ display: flex; gap: 5px; margin-top: 5px; }}
    .color-box {{ width: 30px; height: 30px; border: 1px solid #ccc; border-radius: 3px; }}
    .metric {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
    .metric-good {{ background: #c8e6c9; color: #2e7d32; }}
    .metric-warn {{ background: #ffcc80; color: #e65100; }}
    .metric-bad {{ background: #ffcdd2; color: #c62828; }}
    .heatmap {{ margin: 20px 0; }}
    img {{ max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px; }}
</style>
</head>
<body>
<h1>📊 论文图片颜色一致性检查报告</h1>

<div class="summary">
    <h2>检查概览</h2>
    <p><strong>检查图片总数：</strong>{n}</p>
    <p><strong>平均相似度阈值：</strong>{THRESHOLD}</p>
    <p><strong>异常图片数：</strong>{len(anomalies)}</p>
    <p><strong>整体一致性评分：</strong>{np.mean(avg_sims):.2%}</p>
</div>
"""

    if anomalies:
        html += """
<div class="summary anomaly">
    <h2>⚠️ 异常图片（颜色风格不一致）</h2>
    <p>以下图片的颜色分布与其他图片差异较大，建议检查并统一画风：</p>
    <table>
        <tr><th>图片</th><th>文件名</th><th>平均相似度</th><th>主色调</th><th>饱和度</th><th>明度</th></tr>
"""
        for i in anomalies:
            feat = features[i]
            hue_deg = feat['dominant_hue'] * 360
            sim_class = 'metric-bad' if avg_sims[i] < 0.4 else 'metric-warn'
            html += f"""
        <tr>
            <td><img src="{image_paths[i]}" alt="{names[i]}"></td>
            <td>{names[i]}</td>
            <td><span class="metric {sim_class}">{avg_sims[i]:.2%}</span></td>
            <td>{hue_deg:.0f}°</td>
            <td>{feat['saturation_mean']:.2f}</td>
            <td>{feat['value_mean']:.2f}</td>
        </tr>
"""
        html += "    </table></div>"

    html += """
<div class="summary">
    <h2>📋 所有图片颜色详情</h2>
    <table>
        <tr><th>图片</th><th>文件名</th><th>平均相似度</th><th>主色调</th><th>饱和度</th><th>明度</th><th>主要配色</th></tr>
"""

    for i in range(n):
        feat = features[i]
        hue_deg = feat['dominant_hue'] * 360
        if avg_sims[i] >= 0.7:
            sim_class = 'metric-good'
        elif avg_sims[i] >= THRESHOLD:
            sim_class = 'metric-warn'
        else:
            sim_class = 'metric-bad'

        palette_html = '<div class="palette">'
        for j, color in enumerate(feat['color_palette']):
            ratio = feat['palette_ratio'][j]
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
            )
            palette_html += f'<div class="color-box" style="background:{hex_color};width:{max(20, int(ratio * 100))}px" title="{ratio:.1%}"></div>'
        palette_html += '</div>'

        html += f"""
        <tr>
            <td><img src="{image_paths[i]}" alt="{names[i]}"></td>
            <td>{names[i]}</td>
            <td><span class="metric {sim_class}">{avg_sims[i]:.2%}</span></td>
            <td>{hue_deg:.0f}°</td>
            <td>{feat['saturation_mean']:.2f}</td>
            <td>{feat['value_mean']:.2f}</td>
            <td>{palette_html}</td>
        </tr>
"""

    html += "    </table></div>"

    # 相似度矩阵热力图
    html += """
<div class="summary">
    <h2>🔥 颜色相似度矩阵</h2>
    <p>行/列交叉处的数值表示对应两张图片的颜色相似度。</p>
    <table>
        <tr><th>图片</th>
"""
    for name in names:
        html += f'<th title="{name}">{name[:10]}...</th>'
    html += '</tr>'

    for i in range(n):
        html += f'<tr><td><b>{names[i][:15]}</b></td>'
        for j in range(n):
            sim = similarities[i, j]
            if sim >= 0.7:
                color = '#c8e6c9'
            elif sim >= THRESHOLD:
                color = '#ffcc80'
            else:
                color = '#ffcdd2'
            html += f'<td style="background:{color};text-align:center;font-size:12px;">{sim:.2f}</td>'
        html += '</tr>'

    html += "    </table></div>"

    html += """
<div class="summary">
    <h2>📖 使用说明</h2>
    <ul>
        <li><strong>主色调：</strong>HSV 色彩空间中的 H 值（0-360°），代表图片的整体色相倾向</li>
        <li><strong>饱和度：</strong>颜色鲜艳程度，0=灰度，1=纯彩色</li>
        <li><strong>明度：</strong>颜色明亮程度，0=黑，1=白</li>
        <li><strong>平均相似度：</strong>该图与其他所有图的相似度平均值，低于 60% 建议检查</li>
        <li><strong>配色方案：</strong>通过 K-means 提取的 5 种主要颜色，宽度代表占比</li>
    </ul>
</div>

</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"报告已生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='检查论文图片颜色分布一致性')
    parser.add_argument('--input', '-i', required=True, help='图片所在目录')
    parser.add_argument('--output', '-o', default='color_report.html', help='输出报告路径')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归搜索子目录')
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"错误: 目录不存在: {input_dir}")
        sys.exit(1)

    # 收集图片文件
    patterns = ['*.png', '*.jpg', '*.jpeg', '*.pdf']
    image_paths = []
    for pattern in patterns:
        if args.recursive:
            image_paths.extend(input_dir.rglob(pattern))
        else:
            image_paths.extend(input_dir.glob(pattern))

    image_paths = sorted([str(p) for p in image_paths])

    if not image_paths:
        print(f"未在 {input_dir} 中找到图片文件（支持: PNG, JPG, JPEG, PDF）")
        sys.exit(1)

    print(f"发现 {len(image_paths)} 张图片，开始分析...")

    # 提取特征
    features = []
    for i, path in enumerate(image_paths):
        print(f"  [{i+1}/{len(image_paths)}] 分析: {Path(path).name}")
        try:
            img = load_image(path)
            feat = extract_color_features(img)
            features.append(feat)
        except Exception as e:
            print(f"    错误: {e}")
            features.append(None)

    # 过滤失败的
    valid_indices = [i for i, f in enumerate(features) if f is not None]
    image_paths = [image_paths[i] for i in valid_indices]
    features = [features[i] for i in valid_indices]

    if len(features) < 2:
        print("可分析图片少于 2 张，无法计算相似度")
        sys.exit(1)

    # 计算相似度矩阵
    n = len(features)
    similarities = np.eye(n)
    print("计算相似度矩阵...")
    for i in range(n):
        for j in range(i + 1, n):
            sim = color_similarity(features[i], features[j])
            similarities[i, j] = sim
            similarities[j, i] = sim

    # 生成报告
    generate_report(image_paths, features, similarities, args.output)
    print("检查完成!")


if __name__ == '__main__':
    main()
