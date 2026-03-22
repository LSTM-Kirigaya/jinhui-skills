# Jinhui Skills

个人技能库，收集和整理常用的 AI 技能 (skills)。

## 使用方法

**安装 Skill：**

```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/{skill-name}/SKILL.md 安装该 skill。
```

**使用 Skill：**

```
请根据已安装的 skill 能力，帮我完成以下任务...
```

## 技能列表

<!-- 新技能请按字母顺序添加 -->

### [skill-creator](skills/skill-creator/SKILL.md)

用于创建和管理其他 skills 的元技能。提供标准的目录结构、文件模板和最佳实践指南。

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/skill-creator/SKILL.md 安装该 skill。
```

**使用：**
```
请帮我创建一个新的 skill，用于...
```

---

### [shot-scraper](skills/shot-scraper/SKILL.md)

使用 shot-scraper 工具对网页进行截图并分析，适用于网页审查、UI 检查等场景。

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/shot-scraper/SKILL.md 安装该 skill。
```

**使用：**
```
请帮我截图并分析这个网页: ...
```

---

### [tauri-devtools](skills/tauri-devtools/SKILL.md)

Tauri 应用开发调试工具集，提供截图、DOM 检查、元素交互、IPC 监控等功能。包含完整的初始化配置指南和踩坑记录。

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/tauri-devtools/SKILL.md 安装该 skill。
```

**使用：**
```
请帮我调试这个 Tauri 应用...
```

---

### [weapp-devtools](skills/weapp-devtools/SKILL.md)

微信小程序自动化调试工具集，基于 miniprogram-automator 封装，提供截图、元素检查、页面导航、网络 Mock 等功能。包含完整的 9420 端口配置指南。

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/weapp-devtools/SKILL.md 安装该 skill。
```

**使用：**
```
请帮我调试这个微信小程序...
```

## 目录结构

```
jinhui-skills/
├── README.md              # 本文件
├── skills/                # 所有 skill 文件存放目录
│   ├── skill-creator/
│   │   └── SKILL.md
│   ├── shot-scraper/
│   │   └── SKILL.md
│   ├── tauri-devtools/    # Tauri 开发调试工具集（含子目录结构）
│   │   ├── SKILL.md       # 主入口
│   │   ├── setup/         # 初始化配置
│   │   ├── session/       # Session 管理
│   │   ├── ui-automation/ # UI 自动化
│   │   ├── window/        # 窗口管理
│   │   ├── ipc/           # IPC 调试
│   │   ├── logs/          # 日志分析
│   │   └── mobile/        # 移动开发
│   └── weapp-devtools/    # 微信小程序调试工具集
│       ├── SKILL.md       # 主入口
│       ├── setup/         # 初始化配置
│       ├── session/       # 连接管理
│       ├── ui-automation/ # UI 自动化
│       ├── navigation/    # 页面导航
│       ├── network/       # 网络操作
│       └── logs/          # 日志分析
└── templates/             # 模板文件
    └── SKILL.md.template
```

## 添加新技能

1. 在 `skills/` 下创建新目录（如 `my-skill/`）
2. 在该目录下创建 `SKILL.md`，编写技能内容
3. 在 `README.md` 的技能列表中添加简介和链接
4. 提交并推送

## 命名规范

- **目录名**: 小写字母，单词间用连字符 `-` 分隔
- **文件名**: 必须命名为 `SKILL.md`（全大写）
