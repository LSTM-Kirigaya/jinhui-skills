#!/usr/bin/env python3
from __future__ import annotations
"""从 LaTeX 源码中提取 table/tabular 环境并转成结构化表格数据。

用法:
    python3 extract_tables.py <arxiv_id> <workspace_dir>

示例:
    python3 extract_tables.py 2606.32034 test-skills/read-paper/output
"""

import json
import re
import sys
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "nanochat" / "knowledge"
TABLE_ENV_RE = re.compile(r"\\begin\{(table\*?)\}", re.IGNORECASE)
TABULAR_RE = re.compile(r"\\begin\{tabular\}(?:\[[^\]]*\])?\{[^}]*\}(.*?)\\end\{tabular\}", re.DOTALL | re.IGNORECASE)
CAPTION_RE = re.compile(r"\\caption\{", re.IGNORECASE)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")


def find_matching_brace(text: str, start: int) -> int:
    """从 start（左花括号位置）开始找到匹配的右花括号。"""
    if text[start] != "{":
        return -1
    depth = 1
    i = start + 1
    while i < len(text) and depth > 0:
        if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif text[i] == "}" and (i == 0 or text[i - 1] != "\\"):
            depth -= 1
        i += 1
    return i


def extract_caption(table_text: str) -> str:
    """提取 \\caption{...} 内容，支持一层嵌套。"""
    for m in CAPTION_RE.finditer(table_text):
        end = find_matching_brace(table_text, m.end() - 1)
        if end > 0:
            return table_text[m.end():end - 1].strip()
    return ""


def extract_label(table_text: str) -> str:
    """提取 \\label{...} 内容。"""
    m = LABEL_RE.search(table_text)
    return m.group(1).strip() if m else ""


def strip_latex_commands(cell: str) -> str:
    """移除单元格中不影响可读性的简单 LaTeX 命令。"""
    # 移除 \textbf{}、\textit{}、\emph{} 等简单命令，保留花括号内文本
    cell = re.sub(r"\\(textbf|textit|emph|texttt|mathbf|mathit|mathrm)\{([^}]*)\}", r"\2", cell)
    # 移除剩余独立反斜杠命令（粗略）
    cell = re.sub(r"\\[A-Za-z]+\*?\s?", " ", cell)
    # 移除多余空白
    return " ".join(cell.split())


def tabular_to_markdown(raw: str) -> tuple[str, list[str], list[list[str]]]:
    """将 tabular 内容转换为 Markdown 表格与结构化数据。"""
    # 移除 \hline、\toprule、\midrule、\bottomrule、\noalign 等
    cleaned = re.sub(r"\\(hline|toprule|midrule|bottomrule|cline\{[^}]*\}|noalign\{[^}]*\})", "", raw)
    # 按行分割（\\ 表示换行）
    rows_raw = [r.strip() for r in re.split(r"\\\\", cleaned) if r.strip()]

    headers: list[str] = []
    rows: list[list[str]] = []
    for idx, row_raw in enumerate(rows_raw):
        cells = [strip_latex_commands(c) for c in row_raw.split("&")]
        cells = [c for c in cells if c or len(cells) > 1]
        if not cells:
            continue
        if idx == 0:
            headers = cells
        else:
            rows.append(cells)

    # 构造 Markdown
    md_lines: list[str] = []
    if headers:
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        # 补齐列数
        padded = row + [""] * (len(headers) - len(row)) if headers else row
        md_lines.append("| " + " | ".join(padded) + " |")
    markdown = "\n".join(md_lines)
    return markdown, headers, rows


def find_tables(extract_dir: Path) -> list[dict]:
    """在解压目录中提取所有 table 环境。"""
    tables = []
    for tex_file in extract_dir.rglob("*.tex"):
        try:
            text = tex_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 使用简单栈找到每个 table 环境范围
        pos = 0
        while True:
            m = TABLE_ENV_RE.search(text, pos)
            if not m:
                break
            env_name = m.group(1)
            begin_str = f"\\begin{{{env_name}}}"
            end_str = f"\\end{{{env_name}}}"
            start = m.start()
            end = text.find(end_str, start)
            if end == -1:
                break
            end += len(end_str)
            table_text = text[start:end]

            caption = extract_caption(table_text)
            label = extract_label(table_text)
            table_id = label or f"table_{len(tables)+1}"

            # 在 table 环境内查找 tabular
            tab_m = TABULAR_RE.search(table_text)
            if tab_m:
                tabular_raw = tab_m.group(1)
                markdown, headers, rows = tabular_to_markdown(tabular_raw)
            else:
                markdown, headers, rows = "", [], []

            tables.append({
                "table_id": table_id,
                "caption": caption,
                "markdown": markdown,
                "headers": headers,
                "rows": rows,
                "source_file": str(tex_file.relative_to(extract_dir)),
            })
            pos = end

    return tables


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

    tables = find_tables(extract_dir)
    output = {
        "arxiv_id": arxiv_id,
        "table_count": len(tables),
        "tables": tables,
    }

    out_path = workspace_dir / "tables.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"table_count={len(tables)}")
    print(f"tables_path={out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
