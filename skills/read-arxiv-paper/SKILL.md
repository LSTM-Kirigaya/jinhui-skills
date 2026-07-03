---
name: read-arxiv-paper
description: 读取 arxiv 论文的 LaTeX 源码并生成结构化中文摘要或中文博客 JSON。当用户给出 arxiv URL（如 https://arxiv.org/abs/2601.07372）并要求阅读、总结、提炼论文观点时，使用默认工作流生成 ./knowledge/summary_{tag}.md；当用户要求生成中文博客、输出 JSON、保留图表并输出到测试工作区时，启用 read-paper 工作流。
tags:
  - arxiv
  - paper
  - reading
  - latex
  - summary
  - blog
  - json
  - chinese-blog
  - structured-output
  - research
model: deepseek-chat
rootUrl: https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/read-arxiv-paper/SKILL.md
examples:
  - 帮我读一下这篇 arxiv 论文 https://arxiv.org/abs/2601.07372 并写一个总结
  - 总结这篇论文 https://arxiv.org/abs/2509.12345，看看对我们的项目有什么启发
  - 把这篇论文 https://arxiv.org/abs/2606.32034 生成中文博客 JSON，保留所有图表
---

# arXiv 论文阅读

## 触发条件

当用户给出一个 arxiv 论文 URL 并要求阅读、总结、分析时启用本 skill。

- 若用户要求 **Markdown 摘要/总结**，使用「默认工作流」。
- 若用户要求 **中文博客 JSON / 保留图表 / 结构化输出**，使用「read-paper 工作流」。

## 输入 URL 示例

```
https://arxiv.org/abs/2601.07372
```

## 默认工作流：生成 Markdown 摘要

### 1. 标准化 URL

- 从用户提供的 URL 中提取 `arxiv_id`。
- 构造 TeX 源码下载地址：
  ```
  https://arxiv.org/src/{arxiv_id}
  ```
- **必须获取 LaTeX 源码（`.tar.gz`），而不是 PDF**。

### 2. 下载论文源码

- 缓存路径：`~/.cache/nanochat/knowledge/{arxiv_id}.tar.gz`。
- 如果文件已存在，跳过下载。
- 推荐调用工具脚本：
  ```bash
  python3 skills/read-arxiv-paper/scripts/fetch_arxiv.py {arxiv_id}
  ```

### 3. 解包

- 将源码解压到：`~/.cache/nanochat/knowledge/{arxiv_id}/`。
- 工具脚本会自动完成此步骤。

### 4. 定位入口文件

- 在解压目录中寻找入口 `.tex` 文件，通常是 `main.tex`，也可能是与论文同名的 `.tex`。
- 选择包含 `\documentclass` 的文件作为入口。

### 5. 阅读论文

- 读取入口文件内容。
- 递归解析 `\input{...}` / `\include{...}` / `\bibliography{...}` 等引用，读取相关 `.tex`、`.bib`、`.sty` 文件。
- 跳过二进制资源文件（`.png`、`.jpg`、`.pdf`、`.eps` 等）。
- 合并得到完整论文文本。

### 6. 生成总结

- 在当前项目的 `./knowledge/` 目录下创建 `summary_{tag}.md`。
- **tag 命名规则**：
  - 根据论文主题生成一个简短、有意义的英文小写标签，例如 `conditional_memory`、`rag_fusion`、`moe_scaling`。
  - 先检查 `./knowledge/summary_{tag}.md` 是否已存在；若存在，换一个 tag 或在 tag 后加序号（如 `rag_fusion_2`），**禁止覆盖已有文件**。
- **总结内容要求**：
  - 用中文撰写。
  - 包含：研究背景、核心方法、主要实验/结果、创新点、局限性。
  - **结合当前项目**：如果论文与当前工作项目（例如 nanochat）的技术栈或目标相关，主动阅读项目相关代码，并在总结中明确指出论文对当前项目的启发、可落地的方向或值得尝试的实验。
  - 保留关键公式、方法名称、论文链接。

---

# read-paper：生成中文博客 JSON

## 触发条件

当用户输入 arxiv URL，并明确或隐含以下任一目标时启用 `read-paper` 工作流：

- “生成中文博客” / “写成博客” / “转成博客”
- “输出 JSON” / “结构化数据”
- “保留图表” / “图片也要”
- 要求“摘要基础介绍、解决痛点、总结未来展望”作为博客元数据

## 工作流

### 1. 标准化 URL 并下载源码

- 从 URL 中提取 `arxiv_id`。
- 调用脚本下载并解压：
  ```bash
  python3 skills/read-arxiv-paper/scripts/fetch_arxiv.py {arxiv_id}
  ```
- 缓存位置：`~/.cache/nanochat/knowledge/{arxiv_id}/`。

### 2. 定位入口文件与递归阅读

- 找到含 `\documentclass` 的入口 `.tex`。
- 递归读取 `\input{}` / `\include{}` / `\bibliography{}`。
- 跳过二进制资源文件，但记录 `\includegraphics{...}` 引用的图片文件名。

### 3. 复制图表到测试工作区

- 调用：
  ```bash
  python3 skills/read-arxiv-paper/scripts/copy_figures.py {arxiv_id} test-skills/read-paper/output
  ```
- 支持的图片格式：`.png`、`.jpg`、`.jpeg`、`.pdf`、`.eps`。
- 复制后生成 `test-skills/read-paper/output/figure_manifest.json`。

### 4. 提取表格

- 调用：
  ```bash
  python3 skills/read-arxiv-paper/scripts/extract_tables.py {arxiv_id} test-skills/read-paper/output
  ```
- 输出 `test-skills/read-paper/output/tables.json`。

### 5. 生成中文博客 JSON

- 由大模型阅读完整论文文本，按下方 **JSON Schema** 生成结构化中文博客。
- 章节要“浓缩、缩短”，但**必须保留所有图表引用**；每章至少保留原文中的关键方法名、核心公式、实验结论。
- 输出文件：`test-skills/read-paper/output/blog_{arxiv_id}.json`。

### 6. 生成预览页面

- 调用：
  ```bash
  python3 skills/read-arxiv-paper/scripts/generate_preview.py test-skills/read-paper/output/blog_{arxiv_id}.json
  ```
- 输出 `test-skills/read-paper/output/preview.html`。

### 7. 报告结果

- 向用户返回 JSON 路径、assets 目录路径、图表复制数量、预览文件路径。

## 输出路径规范

- 测试工作区根目录：`{project_root}/test-skills/read-paper/`
- JSON 输出：`{project_root}/test-skills/read-paper/output/blog_{arxiv_id}.json`
- 图表资源：`{project_root}/test-skills/read-paper/output/assets/`
- 预览文件：`{project_root}/test-skills/read-paper/output/preview.html`
- 图表在 JSON 中的引用路径统一使用相对路径：`assets/{filename}`

## 图表处理规则

- 复制图片时保持原始文件名；若重名，追加 `_1`、`_2` 序号。
- 无法识别的 EPS/PDF 文件也复制到 `assets/`，并在 JSON 中标注 `type` 字段。
- 如果 `\includegraphics` 引用的文件不存在，记录到 JSON 的 `resources.missing_files`。
- 不转换 PDF/EPS 为图片，预览页中 PDF 使用 `<embed>`，EPS 提供下载链接。

## JSON Schema

最终输出文件：`test-skills/read-paper/output/blog_{arxiv_id}.json`

### 顶层字段

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `schema_version` | string | Schema 版本 | `"1.0.0"` |
| `arxiv_id` | string | 论文 arxiv ID | `"2606.32034"` |
| `title` | string | 论文英文标题 | `"QVal: Cheaply Evaluating Dense Supervision Signals"` |
| `title_cn` | string | 论文中文标题 | `"QVal：低成本评估密集监督信号"` |
| `source_url` | string | 原文链接 | `"https://arxiv.org/abs/2606.32034"` |
| `authors` | array[string] | 作者列表 | `["Author A", "Author B"]` |
| `published_at` | string | arxiv 发布日期（ISO 8601） | `"2026-06-10"` |
| `generated_at` | string | 生成时间（ISO 8601） | `"2026-07-03T12:00:00+08:00"` |
| `metadata` | object | 博客元数据 | — |
| `chapters` | array[Chapter] | 章节数组 | — |
| `resources` | object | 资源清单 | — |

### `metadata` 对象

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `abstract_intro` | string | 摘要基础介绍：2-3 段中文概括论文问题与核心思路 | `"QVal 提出了一种无需训练的评估平台..."` |
| `pain_points` | string | 解决痛点：现有方法不足、本文针对的难点 | `"传统方法需要完整训练循环..."` |
| `future_outlook` | string | 未来展望：局限性与潜在研究方向 | `"未来可将 QVal 扩展至离线强化学习..."` |

### `chapters` 数组元素

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `chapter_index` | integer | 章节序号（从 1 开始） | `1` |
| `title` | string | 章节英文原标题 | `"Introduction"` |
| `title_cn` | string | 章节中文标题 | `"引言"` |
| `summary` | string | 浓缩后的中文正文，保留关键方法与结论 | `"本文指出..."` |
| `figures` | array[Figure] | 本章出现的图片 | — |
| `tables` | array[Table] | 本章出现的表格 | — |
| `key_takeaways` | array[string] | 本章 1-3 条要点 | `["QVal 无需训练即可评估"]` |

### `figures` 数组元素

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `figure_id` | string | 原 LaTeX 标签或生成的 ID | `"fig:overview"` |
| `caption` | string | 图片标题（英文原文） | `"Overview of QVal framework."` |
| `caption_cn` | string | 图片标题中文翻译 | `"QVal 框架概览。"` |
| `original_filename` | string | 原文件名 | `"overview.png"` |
| `relative_path` | string | 相对工作区根目录的路径 | `"assets/overview.png"` |
| `type` | string | 文件类型：`png` / `jpg` / `jpeg` / `pdf` / `eps` / `unknown` | `"png"` |
| `alt_text` | string | 图片 alt 文本 | `"QVal 框架图"` |

### `tables` 数组元素

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `table_id` | string | 原 LaTeX 标签或生成的 ID | `"tab:results"` |
| `caption` | string | 表格标题（英文原文） | `"Main results on DMControl."` |
| `caption_cn` | string | 表格标题中文翻译 | `"DMControl 上的主实验结果"` |
| `markdown` | string | Markdown 表格源码 | `"\| Task \| QVal \| ... \|"` |
| `headers` | array[string] | 表头 | `["Task", "QVal", "Baseline"]` |
| `rows` | array[array[string]] | 二维表格数据 | `[["walker-walk", "0.92", "0.85"]]` |

### `resources` 对象

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `assets_dir` | string | 资源目录相对路径 | `"assets"` |
| `figure_count` | integer | 成功复制的图片数量 | `5` |
| `table_count` | integer | 提取的表格数量 | `3` |
| `copied_files` | array[string] | 已复制文件相对路径列表 | `["assets/fig1.png"]` |
| `missing_files` | array[string] | 引用但未找到的文件列表 | `[]` |
| `latex_dir` | string | 原始 LaTeX 解压目录 | `"~/.cache/nanochat/knowledge/2606.32034"` |

## 工具脚本

- `scripts/fetch_arxiv.py`：下载并解压指定 arxiv_id 的 LaTeX 源码。
  ```bash
  python3 skills/read-arxiv-paper/scripts/fetch_arxiv.py 2601.07372
  ```
- `scripts/copy_figures.py`：复制论文图片到测试工作区。
  ```bash
  python3 skills/read-arxiv-paper/scripts/copy_figures.py 2606.32034 test-skills/read-paper/output
  ```
- `scripts/extract_tables.py`：提取论文表格。
  ```bash
  python3 skills/read-arxiv-paper/scripts/extract_tables.py 2606.32034 test-skills/read-paper/output
  ```
- `scripts/generate_preview.py`：从 JSON 生成 HTML 预览页。
  ```bash
  python3 skills/read-arxiv-paper/scripts/generate_preview.py test-skills/read-paper/output/blog_2606.32034.json
  ```

## 注意事项

- 不要下载 PDF 作为阅读来源，LaTeX 源码更利于提取完整文本和公式。
- 递归读取时跳过二进制资源文件。
- 如果 arxiv 没有提供源码或源码不是 LaTeX（如只有 PDF/Word），告知用户无法处理。
- 总结文件放在 `./knowledge/`（项目本地），便于用户直接打开和引用；缓存放在 `~/.cache/nanochat/knowledge/`。
- `read-paper` 输出放在 `test-skills/read-paper/output/`，该目录已被 `.gitignore` 忽略，不会进入版本控制。
- 生成 JSON 前检查 `blog_{arxiv_id}.json` 是否已存在；若存在，先备份为 `blog_{arxiv_id}_{timestamp}.json`，再写入新文件。
