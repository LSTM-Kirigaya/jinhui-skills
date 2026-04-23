#!/usr/bin/bash
#
# compile_tikz_to_png.sh
# 将单个 TikZ .tex 文件编译为 PNG 图片
#
# 用法:
#   ./compile_tikz_to_png.sh input.tex [output.png] [dpi]
#
# 示例:
#   ./compile_tikz_to_png.sh figure1.tex
#   ./compile_tikz_to_png.sh figure1.tex output.png 300
#

set -euo pipefail

INPUT_TEX="${1:-}"
OUTPUT_PNG="${2:-}"
DPI="${3:-300}"

# 检查输入
if [[ -z "$INPUT_TEX" ]]; then
    echo "错误: 未指定输入文件"
    echo "用法: $0 input.tex [output.png] [dpi]"
    exit 1
fi

if [[ ! -f "$INPUT_TEX" ]]; then
    echo "错误: 文件不存在: $INPUT_TEX"
    exit 1
fi

# 推断输出文件名
if [[ -z "$OUTPUT_PNG" ]]; then
    OUTPUT_PNG="${INPUT_TEX%.tex}.png"
fi

BASENAME=$(basename "$INPUT_TEX" .tex)
WORKDIR=$(mktemp -d)

echo "编译: $INPUT_TEX → $OUTPUT_PNG (DPI=$DPI)"

# 准备带有独立文档类的临时文件
cat > "$WORKDIR/compile_temp.tex" <<EOF
\\documentclass[tikz,border=10pt]{standalone}
\\usepackage{ctex}
\\usepackage{amsmath,amssymb}
\\usepackage{tikz}
\\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit, backgrounds, patterns, decorations.pathreplacing}
\\usepackage{pgfplots}
\\pgfplotsset{compat=1.18}
\\begin{document}
\\input{$(realpath "$INPUT_TEX")}
\\end{document}
EOF

# 编译为 PDF
cd "$WORKDIR"
pdflatex -interaction=nonstopmode -halt-on-error compile_temp.tex > /dev/null 2>&1 || {
    echo "错误: LaTeX 编译失败"
    echo "查看日志: $WORKDIR/compile_temp.log"
    cat "$WORKDIR/compile_temp.log" | tail -30
    rm -rf "$WORKDIR"
    exit 1
}

# 转换 PDF 为 PNG
if command -v pdftoppm &> /dev/null; then
    pdftoppm -png -r "$DPI" -singlefile compile_temp.pdf "$WORKDIR/output"
    mv "$WORKDIR/output.png" "$OUTPUT_PNG"
elif command -v convert &> /dev/null; then
    convert -density "$DPI" compile_temp.pdf -quality 100 "$OUTPUT_PNG"
elif command -v sips &> /dev/null; then
    # macOS 内置 sips
    sips -s format png -s formatOptions best --out "$OUTPUT_PNG" compile_temp.pdf
else
    echo "错误: 未找到 PDF 转 PNG 工具 (pdftoppm / ImageMagick / sips)"
    rm -rf "$WORKDIR"
    exit 1
fi

rm -rf "$WORKDIR"
echo "完成: $OUTPUT_PNG"
