#!/usr/bin/env python3
from __future__ import annotations
"""从 read-paper 生成的 JSON 渲染一个最简 HTML 预览页。

用法:
    python3 generate_preview.py <blog_json_path>

示例:
    python3 generate_preview.py test-skills/read-paper/output/blog_2606.32034.json
"""

import html
import json
import re
import sys
from pathlib import Path


def escape(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def simple_markdown_to_html(text: str) -> str:
    """极简 Markdown 到 HTML 转换：段落、粗体、斜体、代码。"""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    out = []
    for p in paragraphs:
        p = html.escape(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p)
        p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
        p = p.replace("\n", "<br>")
        out.append(f"<p>{p}</p>")
    return "\n".join(out)


def render_table(table: dict) -> str:
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers and not rows:
        md = table.get("markdown", "")
        if md:
            return f"<pre class=\"table-md\">{escape(md)}</pre>"
        return ""

    cols = len(headers) if headers else (len(rows[0]) if rows else 1)
    th = "\n".join(f"    <th>{escape(h)}</th>" for h in headers) if headers else ""
    thead = f"<thead>\n<tr>\n{th}\n</tr>\n</thead>" if headers else ""
    tbody_rows = []
    for row in rows:
        cells = "\n".join(f"    <td>{escape(str(c))}</td>" for c in row)
        tbody_rows.append(f"<tr>\n{cells}\n</tr>")
    tbody = "\n".join(tbody_rows)
    return f"""
<div class=\"table-wrap\">
<table>
{thead}
<tbody>
{tbody}
</tbody>
</table>
</div>
""".strip()


def render_figure(figure: dict, base_dir: Path) -> str:
    rel = figure.get("relative_path", "")
    caption = figure.get("caption", "")
    caption_cn = figure.get("caption_cn", "")
    file_type = figure.get("type", "").lower()
    alt = figure.get("alt_text", caption_cn or caption)
    src = base_dir / rel if rel else ""

    if file_type in ("png", "jpg", "jpeg"):
        return f"""
<figure>
  <img src="{html.escape(rel)}" alt="{html.escape(alt)}" loading="lazy">
  <figcaption>{html.escape(caption_cn or caption)}</figcaption>
</figure>
""".strip()
    elif file_type == "pdf":
        return f"""
<figure>
  <embed src="{html.escape(rel)}" type="application/pdf" width="100%" height="500px">
  <figcaption>{html.escape(caption_cn or caption)}</figcaption>
</figure>
""".strip()
    elif file_type == "eps":
        return f"""
<figure>
  <a href="{html.escape(rel)}" download>下载 EPS 图</a>
  <figcaption>{html.escape(caption_cn or caption)}</figcaption>
</figure>
""".strip()
    else:
        return f"""
<figure>
  <a href="{html.escape(rel)}" download>下载资源 ({html.escape(file_type or 'unknown')})</a>
  <figcaption>{html.escape(caption_cn or caption)}</figcaption>
</figure>
""".strip()


def render_chapter(chapter: dict, base_dir: Path) -> str:
    title = html.escape(chapter.get("title_cn", chapter.get("title", "")))
    summary = chapter.get("summary", "")
    takeaways = chapter.get("key_takeaways", [])
    figures = chapter.get("figures", [])
    tables = chapter.get("tables", [])

    takeaways_html = ""
    if takeaways:
        items = "\n".join(f"    <li>{simple_markdown_to_html(t)}</li>" for t in takeaways)
        takeaways_html = f"<h4>本章要点</h4>\n<ul>\n{items}\n</ul>"

    figures_html = "\n".join(render_figure(f, base_dir) for f in figures)
    tables_html = "\n".join(render_table(t) for t in tables)

    return f"""
<section class="chapter">
  <h2>{title}</h2>
  <div class="summary">
    {simple_markdown_to_html(summary)}
  </div>
  {takeaways_html}
  <div class="figures">
    {figures_html}
  </div>
  <div class="tables">
    {tables_html}
  </div>
</section>
""".strip()


def render_html(blog: dict, json_path: Path) -> str:
    base_dir = json_path.parent
    title = html.escape(blog.get("title_cn", blog.get("title", "论文博客")))
    source_url = html.escape(blog.get("source_url", ""))
    arxiv_id = html.escape(blog.get("arxiv_id", ""))
    meta = blog.get("metadata", {})

    def meta_card(key: str, label: str) -> str:
        return f"""
<div class="meta-card">
  <h3>{html.escape(label)}</h3>
  <div class="meta-body">{simple_markdown_to_html(meta.get(key, ""))}</div>
</div>
""".strip()

    chapters_html = "\n".join(render_chapter(c, base_dir) for c in blog.get("chapters", []))

    resources = blog.get("resources", {})
    missing = resources.get("missing_files", [])
    missing_html = ""
    if missing:
        items = "\n".join(f"    <li>{html.escape(m)}</li>" for m in missing)
        missing_html = f"<div class=\"warning\"><h4>缺失文件</h4><ul>\n{items}\n</ul></div>"

    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 820px; margin: 0 auto; padding: 24px; line-height: 1.7; color: #1f2937; }
    h1 { font-size: 1.8rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 12px; }
    h2 { font-size: 1.4rem; margin-top: 32px; color: #111827; }
    h3 { font-size: 1.1rem; margin-bottom: 8px; color: #374151; }
    a { color: #2563eb; }
    .subtitle { color: #6b7280; margin-bottom: 24px; }
    .meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 32px; }
    .meta-card { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }
    .meta-body { font-size: 0.95rem; }
    .summary { margin: 16px 0; }
    .chapter { border-bottom: 1px solid #f3f4f6; padding-bottom: 24px; }
    figure { margin: 20px 0; }
    figure img { max-width: 100%; height: auto; border: 1px solid #e5e7eb; border-radius: 8px; }
    figcaption { font-size: 0.9rem; color: #4b5563; margin-top: 8px; }
    .table-wrap { overflow-x: auto; margin: 16px 0; }
    table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
    th, td { border: 1px solid #d1d5db; padding: 8px 12px; text-align: left; }
    th { background: #f3f4f6; }
    .warning { background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 12px; margin-top: 24px; }
    pre.table-md { background: #f9fafb; padding: 12px; overflow-x: auto; border-radius: 8px; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
    """

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
{css}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="subtitle">
    arXiv ID: <a href="{source_url}" target="_blank">{arxiv_id}</a>
  </div>

  <div class="meta-grid">
    {meta_card("abstract_intro", "摘要基础介绍")}
    {meta_card("pain_points", "解决痛点")}
    {meta_card("future_outlook", "未来展望")}
  </div>

  {chapters_html}

  {missing_html}
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"JSON 文件不存在: {json_path}", file=sys.stderr)
        return 2

    blog = json.loads(json_path.read_text(encoding="utf-8"))
    html_content = render_html(blog, json_path)

    out_path = json_path.parent / "preview.html"
    out_path.write_text(html_content, encoding="utf-8")
    print(f"preview_path={out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
