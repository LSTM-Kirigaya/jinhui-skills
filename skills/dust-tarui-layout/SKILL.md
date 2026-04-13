---
name: dust-tarui-layout
description: 通用 Tauri 桌面端 UI 布局模板，复现 DiskRookie 风格的无边框窗口外壳、粘性顶栏、主内容滚动区与专家模式分栏结构。适用于从 0 到 1 快速构建类似布局的客户端软件（如笔记管理、即时通讯等）。基于 Tauri 2 + React + MUI + Tailwind。
rootUrl: https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/dust-tarui-layout/SKILL.md
tags:
  - tauri
  - desktop
  - layout
  - template
  - react
model: deepseek-chat
---

# DiskRookie 应用布局（结构复现指南）

本 Skill 描述 **DiskRookie** 桌面端（`apps/desktop/frontend`）的 **空间结构、区域划分与交互分区**，便于在另一套配色下复刻相同布局。  
默认不强制色板与主题 token；但若需求明确，可在本 Skill 上增加项目级外观约束（见下方“项目化外观补充”）。

## 技术栈与入口（仅结构）

- **壳**：Tauri 2，单窗口，**系统标题栏关闭**（自绘顶栏）。
- **根布局**：React + `ThemeProvider` + `CssBaseline`，根节点为 **纵向 flex 全屏**。
- **组件库**：MUI 用于按钮/对话框等；**Tailwind** 用于大量布局 class（`flex`、`grid`、`min-h-0` 等）。
- **顶栏**：本项目 **无左侧独立导航栏**；**全局操作集中在窗口顶部一条自定义 `header`**（应用名、快照入口、外链、队列、设置、系统窗口按钮）。

## 分册目录（每类内容一个文件夹）

| 文件夹 | 说明 |
|--------|------|
| [window-frame/](window-frame/index.md) | Tauri 窗口几何、无边框、透明与最小尺寸 |
| [title-bar/](title-bar/index.md) | 顶栏高度、左/中/右分区、拖拽区、macOS 与 Win/Linux 差异 |
| [app-shell/](app-shell/index.md) | 根容器与主内容区滚动、与 `ExpertMode` 的嵌套关系 |
| [expert-workbench/](expert-workbench/index.md) | 专家模式：工具条、模式切换、扫描结果分栏与状态机 |
| [overlays-settings/](overlays-settings/index.md) | 设置/快照/任务队列叠层与典型对话框结构 |

阅读顺序建议：**window-frame → title-bar → app-shell → expert-workbench → overlays-settings**。

## 复现时优先保证的约束

1. **顶栏固定**：`sticky top-0`，高度约 **40px（`h-10`）**，主内容区在其下方占满剩余高度。
2. **主内容可滚动**：外层 `overflow-hidden`，内层 `main` 使用 **`flex-1` + `min-h-0` + `overflow-y-auto`**，避免 flex 子项高度撑破窗口。
3. **拖拽**：顶栏可拖拽区域使用 **`data-tauri-drag-region`**；可点击控件上 **`stopPropagation`** 避免误拖。
4. **分栏**：扫描结果在宽屏下常见 **左侧固定宽度侧栏（约 `w-80`）+ 右侧自适应**，右侧内部再用 **响应式 grid**。

## 项目化外观补充（当前仓库约束）

当用户要求与当前示例一致时，除结构外还需满足：

1. **圆角**：应用最外层容器使用 **macOS 常见圆角 `12px`**（例如 `rounded-[12px]`）。
2. **外框**：最外层容器添加 **1px 边框**（`border`），颜色用主题分隔线同级语义色即可。
3. **去阴影**：最外层容器不加 CSS `box-shadow`；Tauri 窗口层 `shadow` 也应设为 `false`。
4. **透明配合**：若窗口 `transparent: true`，需确保 `html/body/#root` 与 `CssBaseline` 不绘制不透明底色，避免圆角外露区域发灰。

## 后续：颜色与主题的质询清单（给使用本 Skill 的协作者）

在实现或换肤前，应向产品/用户确认以下问题（**本分册不预设答案**）：

1. **明暗策略**：仅浅色、仅深色、还是跟随系统？是否需要持久化用户选择？
2. **品牌主色**：主按钮、链接、聚焦环所使用的主色与对比色（需满足可读性与 WCAG）。
3. **表面层级**：页面底、卡片、顶栏、悬停/按下态分别使用几层“表面”，是否区分边框与分隔线。
4. **语义色**：成功、警告、错误、信息类提示是否沿用固定语义色，是否与主色解耦。
5. **圆角与密度**：全局圆角尺度（小按钮 vs 大卡片）、控件间距是否对齐 MUI `theme.shape` / 自定义 spacing。
6. **字体**：标题与正文族、等宽（路径/Token）是否单独指定；是否加载 Web 字体。
7. **无障碍**：焦点可见性、最小点击区域（尤其顶栏约 24–40px 的图标按钮）。

将以上答案映射到 **MUI `createTheme`** 与 **Tailwind 语义扩展**（或 CSS 变量）即可在**保持本 Skill 布局不变**的前提下替换外观。
