# 规则 5：项目初始化

## 适用范围

本规则用于在毕业论文项目尚未建立或需要重新初始化时，构建一个标准化的毕业设计论文项目结构。

**触发条件：**
- 用户表示"开始写论文"但当前目录没有标准结构
- 用户要求"初始化论文项目"
- 发现当前工作目录缺少 `src/`、`references/` 等核心文件夹

---

## 标准项目结构

初始化后应生成以下目录结构：

```
{project-name}/
├── README.md                  # 项目说明文档（包含编译命令、目录说明）
├── AGENTS.md                  # Agent 配置（可选，用于 Kimi Code CLI）
├── src/                       # 论文源代码（LaTeX / Word）
│   ├── main.tex               # 主文件
│   ├── chapters/              # 章节文件
│   │   ├── chapter-01-introduction.tex
│   │   ├── chapter-02-related-work.tex
│   │   ├── chapter-03-methodology.tex
│   │   ├── chapter-04-experiments.tex
│   │   ├── chapter-05-conclusion.tex
│   │   └── appendix.tex
│   ├── figures/               # TikZ 图表源码
│   ├── bib/                   # 参考文献数据库
│   │   └── references.bib
│   └── Makefile               # 编译脚本
├── references/                # 参考文献资料
│   ├── from-proposal/         # 开题报告中的原始参考文件
│   ├── from-scholar/          # Google Scholar 下载的文献
│   │   ├── pdfs/              # 原始 PDF
│   │   ├── bibtex/            # BibTeX 条目
│   │   └── notes/             # 阅读笔记（Markdown）
│   └── extracted/             # 从文献中提取的图片/代码/数据
├── proposal/                  # 开题资料
│   ├── report/                # 开题报告（PDF / Word）
│   ├── slides/                # 开题 PPT
│   └── materials/             # 其他相关材料
├── example-theses/            # 参考范文（可选）
│   └── README.md              # 说明哪些论文可供参考
├── experiments/               # 实验结果
│   ├── code/                  # 实验代码
│   ├── data/                  # 实验数据
│   ├── results/               # 实验输出结果
│   ├── design/                # 实验设计图、对比方案图
│   ├── figures/               # 实验生成的图表
│   └── server-access.md       # 实验室服务器登录信息
└── scripts/                   # 工具脚本
    ├── compile_tikz_to_png.sh # 编译 TikZ 为 PNG
    ├── extract_figures_from_pdf.py  # 从 PDF 提取图片
    └── init_project.sh        # 项目初始化脚本（本脚本）
```

---

## 各目录详细说明

### `src/` — 论文源代码

存放论文的全部源码文件。

| 文件/目录 | 用途 |
|----------|------|
| `main.tex` | LaTeX 主文件，包含导言区、章节引入、参考文献设置 |
| `chapters/` | 各章节独立 `.tex` 文件，便于分章节编辑和版本控制 |
| `figures/` | TikZ 绘图源码（`.tex`），每张图一个独立文件 |
| `bib/references.bib` | BibTeX 参考文献数据库 |
| `Makefile` | 一键编译命令：`make` 编译全文，`make clean` 清理临时文件 |

**模板主文件结构：**
```latex
\documentclass[UTF8]{ctexart}
\usepackage{...}
\begin{document}
\title{论文标题}
\author{作者}
\maketitle
\input{chapters/chapter-01-introduction}
\input{chapters/chapter-02-related-work}
\input{chapters/chapter-03-methodology}
\input{chapters/chapter-04-experiments}
\input{chapters/chapter-05-conclusion}
\bibliography{bib/references}
\end{document}
```

### `references/` — 参考文献资料

集中管理所有与论文相关的文献资料。

| 子目录 | 用途 |
|--------|------|
| `from-proposal/` | 开题阶段收集的原始参考文件 |
| `from-scholar/pdfs/` | Google Scholar 下载的论文 PDF |
| `from-scholar/bibtex/` | 从 Scholar 导出的 `.bib` 条目文件 |
| `from-scholar/notes/` | 文献阅读笔记（Markdown 格式），每篇文献一个文件 |
| `extracted/` | 从文献中提取的：关键图表、代码片段、数据集说明等 |

**文献笔记模板：**
```markdown
# 文献标题

- **作者：**
- **期刊/会议：**
- **年份：**
- **链接/PDF：**
- **数据 CID：**

## 核心贡献

## 与本文的关系

## 可借鉴之处

## 关键图表
```

### `proposal/` — 开题资料

存放开题阶段的所有材料，用于理解项目的整体命题和研究意图。

| 子目录 | 用途 |
|--------|------|
| `report/` | 开题报告（学校格式的 PDF 或 Word） |
| `slides/` | 开题答辩 PPT |
| `materials/` | 其他辅助材料（导师意见、评审记录等） |

**作用：** 在正式撰写论文时，开题资料用于：
- 回顾最初拟定的研究问题和目标
- 核对研究内容是否偏离开题时的计划
- 提取开题报告中已有的文献综述和背景介绍

### `example-theses/` — 参考范文

存放往届通过盲审的优秀论文（PDF 或 Word），供写作参考。

**使用规范：**
- 仅用于学习结构和写作风格
- 禁止直接复制内容
- 存放前确认已获得学长学姐同意

### `experiments/` — 实验结果

集中管理实验相关的全部内容。

| 子目录 | 用途 |
|--------|------|
| `code/` | 实验源代码（含模型定义、训练脚本、评估脚本） |
| `data/` | 实验数据集（或数据集的获取说明） |
| `results/` | 实验输出（日志、模型权重、评估报告） |
| `design/` | 实验设计文档、对比方案设计图、消融实验设计 |
| `figures/` | 实验生成的图表（准确率曲线、对比柱状图等） |
| `server-access.md` | 实验室服务器 SSH 登录信息、环境配置说明 |

**`server-access.md` 模板：**
```markdown
# 实验室服务器访问信息

## SSH 登录
```bash
ssh username@server-address
```

## 实验环境
- Python 版本：
- PyTorch 版本：
- CUDA 版本：
- Conda 环境：

## 常用路径
- 代码目录：
- 数据目录：
- 结果目录：

## 运行实验
```bash
# 激活环境
conda activate env-name

# 运行训练
python train.py --config configs/exp1.yaml
```

## 注意事项
- GPU 使用规范
- 数据备份策略
```

### `scripts/` — 工具脚本

存放辅助论文写作的自动化脚本。

| 脚本 | 功能 |
|------|------|
| `compile_tikz_to_png.sh` | 将单个 TikZ `.tex` 文件编译为 PNG 图片 |
| `extract_figures_from_pdf.py` | 从 PDF 文档中提取嵌入的图片 |
| `init_project.sh` | 初始化本标准项目结构 |

---

## 初始化流程

当检测到项目未初始化时，执行以下步骤：

```
Step 1: 确认项目名称和论文题目
Step 2: 创建上述完整目录结构
Step 3: 在 src/ 中生成 LaTeX 模板骨架
Step 4: 在 experiments/ 中生成 server-access.md 模板
Step 5: 在 references/ 中生成文献笔记模板
Step 6: 在 scripts/ 中放置工具脚本
Step 7: 生成 README.md 和 AGENTS.md
Step 8: 验证目录完整性
```

---

## 输出要求

初始化完成后，必须以表格形式汇报创建的目录和文件：

| 路径 | 类型 | 状态 | 说明 |
|------|------|------|------|
| `src/main.tex` | 文件 | 已创建 | LaTeX 主文件模板 |
| `src/chapters/` | 目录 | 已创建 | 包含 5 个章节骨架文件 |
| `references/from-scholar/pdfs/` | 目录 | 已创建 | 待用户填充 |
| `scripts/compile_tikz_to_png.sh` | 文件 | 已创建 | TikZ 编译脚本 |
| ... | ... | ... | ... |
