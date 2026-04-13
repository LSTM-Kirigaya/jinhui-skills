# 应用外壳：根布局与主内容区

对应实现：`apps/desktop/frontend/src/App.tsx` 中 `header` 之下的结构。

## 根容器

- 外层：`min-h-screen` + **纵向 flex** `flex flex-col` + **`overflow-hidden`**，高度占满视口（可配合 `height: 100%`、`box-sizing: border-box` 在 Tauri 内铺满）。
- **目的**：把滚动限制在 **`main`**，避免整页包括顶栏一起滚动（顶栏另用 `sticky` 加固）。
- 若需求指定 macOS 风格外框：在该最外层容器增加 **`12px` 圆角 + `1px border`**，并保持无 `box-shadow`。

## 主内容区 `main`

- 与顶栏为兄弟：顶栏 **`shrink-0`**，主区 **`flex-1 flex`**。
- **滚动**：`main` 使用 **`overflow-y-auto`**，并配合 **`min-h-0`**，解决 flex 子元素默认 `min-height: auto` 导致无法内部滚动的问题。
- **内边距**：`main` 常设 **`p-4`**，作为全局内容与窗口边缘的间距。
- **子组件**：默认挂载 **`ExpertMode`**；设置、快照、任务队列为 **条件渲染的叠层**（见 `overlays-settings` 文件夹）。

## 主题包裹

- 根使用 MUI **`ThemeProvider`** + **`CssBaseline`**；调色在主题层完成，不在本分册展开。

## 与顶栏的衔接

- 顶栏与主区在结构上形成「**顶栏 | 工作区**」上下两段；注意勿给 `main` 错误设置 `h-screen` 造成双滚动条。
