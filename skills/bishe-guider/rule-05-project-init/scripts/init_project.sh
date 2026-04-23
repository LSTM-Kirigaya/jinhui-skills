#!/usr/bin/bash
#
# init_project.sh
# 初始化标准化的毕业论文项目结构
#
# 用法:
#   ./init_project.sh [项目目录名]
#
# 示例:
#   ./init_project.sh my-thesis
#

set -euo pipefail

PROJECT_NAME="${1:-thesis-project}"

echo "初始化毕业论文项目: $PROJECT_NAME"

# 创建目录结构
mkdir -p "$PROJECT_NAME"/src/chapters
mkdir -p "$PROJECT_NAME"/src/figures
mkdir -p "$PROJECT_NAME"/src/bib
mkdir -p "$PROJECT_NAME"/references/from-proposal
mkdir -p "$PROJECT_NAME"/references/from-scholar/pdfs
mkdir -p "$PROJECT_NAME"/references/from-scholar/bibtex
mkdir -p "$PROJECT_NAME"/references/from-scholar/notes
mkdir -p "$PROJECT_NAME"/references/extracted
mkdir -p "$PROJECT_NAME"/proposal/report
mkdir -p "$PROJECT_NAME"/proposal/slides
mkdir -p "$PROJECT_NAME"/proposal/materials
mkdir -p "$PROJECT_NAME"/example-theses
mkdir -p "$PROJECT_NAME"/experiments/code
mkdir -p "$PROJECT_NAME"/experiments/data
mkdir -p "$PROJECT_NAME"/experiments/results
mkdir -p "$PROJECT_NAME"/experiments/design
mkdir -p "$PROJECT_NAME"/experiments/figures
mkdir -p "$PROJECT_NAME"/scripts

# 生成 LaTeX 主文件模板
cat > "$PROJECT_NAME/src/main.tex" <<'EOF'
\documentclass[UTF8,a4paper,12pt]{ctexart}
\usepackage{geometry}
\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit, backgrounds}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{listings}
\usepackage{xcolor}

\title{论文标题}
\author{作者姓名}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
摘要内容...
\end{abstract}

\tableofcontents
\newpage

\input{chapters/chapter-01-introduction}
\input{chapters/chapter-02-related-work}
\input{chapters/chapter-03-methodology}
\input{chapters/chapter-04-experiments}
\input{chapters/chapter-05-conclusion}

\bibliographystyle{plain}
\bibliography{bib/references}

\appendix
\input{chapters/appendix}

\end{document}
EOF

# 生成章节骨架
for chapter in chapter-01-introduction chapter-02-related-work chapter-03-methodology chapter-04-experiments chapter-05-conclusion appendix; do
    cat > "$PROJECT_NAME/src/chapters/${chapter}.tex" <<EOF
% ${chapter}.tex

EOF
done

# 生成空 BibTeX 文件
touch "$PROJECT_NAME/src/bib/references.bib"

# 生成 Makefile
cat > "$PROJECT_NAME/src/Makefile" <<'EOF'
.PHONY: all clean

MAIN = main

all:
	pdflatex $(MAIN).tex
	bibtex $(MAIN)
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot *.synctex.gz
EOF

# 生成参考文献笔记模板
cat > "$PROJECT_NAME/references/from-scholar/notes/README.md" <<'EOF'
# 文献阅读笔记

本目录存放从 Google Scholar 检索到的论文阅读笔记。

每篇文献一个 Markdown 文件，命名格式：`作者-年份-标题关键词.md`

## 笔记模板

```markdown
# 论文标题

- **作者：**
- **期刊/会议：**
- **年份：**
- **链接/PDF：** ../pdfs/xxx.pdf
- **BibTeX：** ../bibtex/xxx.bib
- **数据 CID：**

## 核心贡献

## 与本文的关系

## 可借鉴之处

## 关键图表
```
EOF

# 生成 experiments/server-access.md 模板
cat > "$PROJECT_NAME/experiments/server-access.md" <<'EOF'
# 实验室服务器访问信息

## SSH 登录

```bash
ssh username@server-address
```

## 实验环境

| 项目 | 版本 |
|------|------|
| Python | |
| PyTorch | |
| CUDA | |
| Conda 环境 | |

## 常用路径

| 用途 | 路径 |
|------|------|
| 代码目录 | |
| 数据目录 | |
| 结果目录 | |

## 运行实验

```bash
# 激活环境
conda activate env-name

# 运行训练
python train.py --config configs/exp1.yaml
```

## 注意事项

- GPU 使用规范：
- 数据备份策略：
EOF

# 生成 example-theses/README.md
cat > "$PROJECT_NAME/example-theses/README.md" <<'EOF'
# 参考范文

本目录存放往届通过盲审的优秀论文，供写作参考。

## 存放规范

- 文件名格式：`年份-作者-标题.pdf`
- 存放前确认已获得作者同意
- 仅用于学习结构和写作风格，禁止直接复制内容

## 参考重点

1. 章节结构和篇幅分配
2. 文献综述的组织方式
3. 实验设计和结果呈现
4. 创新点的提炼和表述
EOF

# 生成项目 README.md
cat > "$PROJECT_NAME/README.md" <<'EOF'
# 毕业论文项目

## 目录说明

| 目录 | 说明 |
|------|------|
| `src/` | 论文 LaTeX 源码 |
| `references/` | 参考文献资料（PDF、笔记、BibTeX） |
| `proposal/` | 开题报告、PPT 及相关材料 |
| `example-theses/` | 参考范文（可选） |
| `experiments/` | 实验代码、数据、结果 |
| `scripts/` | 辅助脚本工具 |

## 编译论文

```bash
cd src
make
```

## 清理临时文件

```bash
cd src
make clean
```

## 添加参考文献

1. 将 PDF 放入 `references/from-scholar/pdfs/`
2. 将 BibTeX 放入 `references/from-scholar/bibtex/`
3. 将阅读笔记放入 `references/from-scholar/notes/`
4. 在 `src/bib/references.bib` 中统一维护引用
EOF

# 生成 AGENTS.md
cat > "$PROJECT_NAME/AGENTS.md" <<'EOF'
# 项目 Agent 配置

## 项目信息

| 属性 | 内容 |
|------|------|
| **论文题目** | |
| **学位类型** | 本科 / 硕士 / 博士 |
| **学校** | |
| **当前阶段** | 开题 / 撰写 / 修改 / 定稿 |

## 快速命令

```bash
# 编译论文
cd src && make

# 编译 TikZ 图片
cd scripts && ./compile_tikz_to_png.sh ../src/figures/fig1.tex

# 提取 PDF 图片
cd scripts && python extract_figures_from_pdf.py input.pdf -o ../references/extracted/
```
EOF

# 复制工具脚本到项目 scripts/
cp "$(dirname "$0")/compile_tikz_to_png.sh" "$PROJECT_NAME/scripts/"
cp "$(dirname "$0")/extract_figures_from_pdf.py" "$PROJECT_NAME/scripts/"
chmod +x "$PROJECT_NAME/scripts/compile_tikz_to_png.sh"
chmod +x "$PROJECT_NAME/scripts/extract_figures_from_pdf.py"

echo ""
echo "项目初始化完成！"
echo ""
echo "目录结构:"
find "$PROJECT_NAME" -type f | sort | sed 's|^|  |'
