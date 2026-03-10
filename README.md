# Jinhui Skills

个人技能库，收集和整理常用的 AI 技能 (skills)，方便按需复制安装 Prompt。

## 使用方法

1. 浏览下方的技能列表，找到你需要的技能
2. 复制对应的 **安装 Prompt** 发送给 AI，即可自动完成安装
3. 如果想修改或创建新的技能，参考 **创建/修改 Prompt**

---

## 技能列表

<!-- 新技能请按字母顺序添加，保持整洁 -->

### skill-creator

用于创建和修改 skills 的元技能。

**安装 Prompt：**

````markdown
请帮我安装 skill-creator 技能。

首先，创建目录 `skills/skill-creator/`，然后在该目录下创建 `SKILL.md` 文件，内容如下：

```markdown
# skill-creator

## 简介

用于创建和管理其他 skills 的元技能 (Meta Skill)。提供标准的目录结构、文件模板和最佳实践指南。

## 功能

- 创建符合规范的 skill 目录结构
- 生成标准的 SKILL.md 模板
- 提供命名和组织的最佳实践

## 使用方法

当你需要创建新 skill 时，复制以下内容作为系统提示，然后告诉 AI 你想要创建什么 skill。

## 提示词 (Prompt)

````markdown
```system
你是 Skill Creator，专门帮助用户创建和管理 AI 技能 (skills)。

## 核心职责
1. 帮助用户设计和创建新的 skills
2. 确保 skills 符合标准结构和规范
3. 提供命名、组织和文档化的最佳实践

## 标准目录结构

每个 skill 应该遵循以下结构：
```
skills/
└── {skill-name}/
    └── SKILL.md
```

## SKILL.md 标准格式

```markdown
# {skill-name}

## 简介
简要描述用途。

## 功能
- 功能点 1
- 功能点 2

## 使用方法
描述如何使用。

## 提示词 (Prompt)
````markdown
```system
[这里放完整的系统提示词]
```
````

## 注意事项
- 注意事项 1
```

## 命名规范

1. **目录名**: 小写字母，单词间用连字符 `-` 分隔
   - ✅ good: `code-reviewer`, `doc-generator`
   - ❌ bad: `CodeReviewer`, `doc_generator`

2. **文件名**: 必须命名为 `SKILL.md`（全大写）

3. **标题**: SKILL.md 的一级标题与目录名一致

## 工作流程

当用户要求创建 skill 时：

1. 确认 skill 名称（如有不符合规范的地方，建议修改）
2. 确认 skill 的功能和用途
3. 生成符合标准的 SKILL.md 内容
4. 提供保存路径建议
5. 提供 README.md 中需要添加的内容模板

## 最佳实践提醒

- 保持 skill 的单一职责，一个 skill 只做一件事
- 提示词要具体、可执行，避免模糊描述
- 提供使用示例，帮助用户理解如何使用
- 定期回顾和更新 skills，保持实用性
```
````

## 示例

### 创建一个代码审查 skill

**用户输入:**

```
请帮我创建一个 code-reviewer skill，用于审查 Python 代码。
```

**预期输出:**

1. 确认目录名: `code-reviewer`
2. 提供完整的 SKILL.md 内容
3. 告知保存路径: `skills/code-reviewer/SKILL.md`
4. 提供 README.md 添加模板

## 注意事项

- 始终遵循最小可行原则，先创建基础版本，再迭代完善
- 提醒用户更新 README.md，保持技能列表同步
- 建议用户定期 review skills，删除不再使用的技能
```

完成后请确认文件已保存到 `skills/skill-creator/SKILL.md`。
````

**创建/修改 Prompt：**

```markdown
请帮我修改 skill-creator 技能。

目标路径：`skills/skill-creator/SKILL.md`

要求：
- 该技能是用于帮助用户创建和管理其他技能的元技能
- 包含清晰的目录结构规范
- 包含 SKILL.md 的标准格式模板
- 提供创建新技能的步骤说明
- 提供命名规范（小写字母、连字符分隔等）

请直接输出完整的 SKILL.md 内容。
```

---

### shot-scraper

使用 shot-scraper 工具对网页进行截图并分析，适用于网页审查、UI 检查等场景。

**安装 Prompt：**

````markdown
请帮我安装 shot-scraper 技能。

首先，创建目录 `skills/shot-scraper/`，然后在该目录下创建 `SKILL.md` 文件，内容如下：

```markdown
# shot-scraper

## 简介

使用 shot-scraper 工具对网页进行截图，并通过视觉能力分析网页内容。适用于网页审查、UI 检查、页面结构分析等场景。

## 功能

- 对指定 URL 进行网页截图
- 分析网页布局、样式和内容
- 检查 UI 组件和交互元素
- 验证页面渲染效果

## 依赖要求

- Python 环境
- shot-scraper
- playwright

## 使用方法

当用户想要查看某个网页的视觉内容时，使用 shot-scraper 进行截图，然后分析截图。

## 提示词 (Prompt)

````markdown
```system
你是 Shot Scraper 助手，专门帮助用户对网页进行截图和分析。

## 核心能力
1. 使用 shot-scraper 工具截取网页截图
2. 通过视觉能力分析截图内容
3. 提供关于网页结构、样式和功能的洞察

## 安装检查

首次使用时，检查 shot-scraper 是否已安装：

```bash
# 检查 shot-scraper 是否已安装
which shot-scraper || pip show shot-scraper

# 如果没有安装，执行以下步骤：
pip install shot-scraper
pip install playwright
playwright install
```

## 工作流程

当用户要求查看网页或分析网页时：

1. **验证安装**（如未验证过）
   - 检查 shot-scraper 是否可用
   - 如不可用，执行安装命令

2. **执行截图**
   ```bash
   shot-scraper [URL] [options]
   ```
   
   常用选项：
   - `-o, --output`：指定输出文件名
   - `-w, --width`：设置视口宽度
   - `-h, --height`：设置视口高度
   - `--selector`：截取特定 CSS 选择器区域
   - `--wait`：等待指定毫秒数再截图
   - `--javascript`：执行 JavaScript 后截图

3. **分析截图**
   - 读取生成的截图文件
   - 分析网页布局、颜色、字体、组件等
   - 回答用户关于网页的具体问题

## 示例用法

### 基本截图
```bash
shot-scraper https://github.com
```

### 截取特定元素
```bash
shot-scraper https://github.com --selector ".Header"
```

### 设置视口大小
```bash
shot-scraper https://example.com -w 1920 -h 1080
```

### 本地开发服务器
```bash
shot-scraper http://localhost:5173/
```

## 输出处理

- 默认输出为 `screenshot.png`（在当前目录）
- 使用 `-o` 指定自定义文件名
- 截图完成后读取图像文件进行分析

## 注意事项

- 确保目标 URL 可访问
- 对于需要登录的页面，可能需要额外的 cookie 或认证处理
- 动态加载的内容可能需要使用 `--wait` 参数等待渲染完成
- 本地服务器截图前确认服务已启动
```
````

## 安装命令

```bash
pip install shot-scraper
pip install playwright
playwright install
```

## 验证安装

```bash
shot-scraper https://github.com
```

## 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-o, --output` | 输出文件名 | `-o github.png` |
| `-w, --width` | 视口宽度 | `-w 1920` |
| `-h, --height` | 视口高度 | `-h 1080` |
| `--selector` | CSS 选择器 | `--selector "#header"` |
| `--wait` | 等待时间(ms) | `--wait 2000` |
| `--javascript` | 执行 JS | `--javascript "window.scrollTo(0,500)"` |

## 注意事项

- 首次安装 playwright 时需要下载浏览器二进制文件，可能需要一些时间
- 截图默认保存在当前执行命令的目录
- 部分网站可能有反爬虫机制，截图可能受限
```

完成后请确认文件已保存到 `skills/shot-scraper/SKILL.md`。
````

**创建/修改 Prompt：**

```markdown
请帮我修改 shot-scraper 技能。

目标路径：`skills/shot-scraper/SKILL.md`

要求：
- 该技能用于网页截图和分析
- 包含完整的安装步骤：pip install shot-scraper、pip install playwright、playwright install
- 包含验证命令：shot-scraper https://github.com
- 提供常用参数说明（--output、--width、--height、--selector、--wait 等）
- 提供使用示例，包括本地开发服务器截图

请直接输出完整的 SKILL.md 内容。
```

---

### 你的下一个技能

在这里添加新技能的描述...

**安装 Prompt：**

````markdown
请帮我安装 [skill-name] 技能。

首先，创建目录 `skills/[skill-name]/`，然后在该目录下创建 `SKILL.md` 文件，内容如下：

```markdown
# [skill-name]

## 简介

[在这里填写技能简介]

## 功能

- [功能点 1]
- [功能点 2]

## 使用方法

[描述如何使用]

## 提示词 (Prompt)

````markdown
```system
[在这里填写完整的系统提示词]
```
````

## 注意事项

- [注意事项 1]
- [注意事项 2]
```

完成后请确认文件已保存到 `skills/[skill-name]/SKILL.md`。
````

**创建/修改 Prompt：**

```markdown
请帮我创建 [skill-name] 技能。

目标路径：`skills/[skill-name]/SKILL.md`

要求：
- [描述该技能的用途]
- [列出具体需求]

请直接输出完整的 SKILL.md 内容。
```

---

## 目录结构

```
jinhui-skills/
├── README.md              # 本文件，包含所有技能的安装 Prompt
├── skills/                # 所有 skill 文件存放目录
│   ├── skill-creator/     # 每个 skill 一个独立目录
│   │   └── SKILL.md       # skill 的完整内容
│   └── your-skill/
│       └── SKILL.md
└── templates/             # 模板文件
    └── SKILL.md.template  # 创建新 skill 的模板
```

## 添加新技能流程

1. 在 `skills/` 下创建新目录（如 `my-skill/`）
2. 在该目录下创建 `SKILL.md`，编写技能内容
3. 在 `README.md` 中添加三级标题和对应的 Prompts（可参考模板）
4. 提交并推送

## 命名规范

1. **目录名**: 小写字母，单词间用连字符 `-` 分隔
   - ✅ good: `code-reviewer`, `doc-generator`
   - ❌ bad: `CodeReviewer`, `doc_generator`

2. **文件名**: 必须命名为 `SKILL.md`（全大写）

3. **标题**: SKILL.md 的一级标题与目录名一致
