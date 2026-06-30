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

### [jinhui-stack-debug](skills/jinhui-stack-debug/SKILL.md)

网站和小程序调试的依赖关系排查指南。当调试陷入僵局时，系统性地识别是哪一层依赖导致的问题：数据、环境、版本、配置、状态、网络、权限、缓存、构建、运行时。

**Copyright © 锦恢 [kirigaya.cn](https://kirigaya.cn)**

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/jinhui-stack-debug/SKILL.md 安装该 skill。
```

**使用：**
```
这个页面功能不正常，帮我排查一下...
```

---

### [rn-app-builder](skills/rn-app-builder/SKILL.md)

基于真实项目沉淀的 React Native 移动端 App 一键构建方案。覆盖 Expo 初始化、monorepo 共享包、鉴权路由、API 适配、主题系统与构建发布。

**Copyright © 锦恢 [kirigaya.cn](https://kirigaya.cn)**

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/rn-app-builder/SKILL.md 安装该 skill。
```

**使用：**
```
帮我基于 React Native 搭建一个移动应用...
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

---

### [web-devtools](skills/web-devtools/SKILL.md)

基于 browser-use CLI 的浏览器自动化调试工具集，提供网页控制、元素交互、截图、Cookie 管理、云端浏览器等功能。支持无头/可视模式、真实 Chrome Profile、云端浏览器等。

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/web-devtools/SKILL.md 安装该 skill。
```

**使用：**
```
请帮我自动化操作这个网页...
```

---

### [zhihu-oauth](skills/zhihu-oauth/SKILL.md)

知乎 OAuth 2.0 接入指南。帮助开发者完成知乎 Authorization Code 授权流程，包括应用申请、授权页跳转、Token 换取、用户信息获取及社交关系接口调用。

**安装：**
```
请通过 https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/main/skills/zhihu-oauth/SKILL.md 安装该 skill。
```

**使用：**
```
帮我接入知乎 OAuth2.0 登录...
```

## 目录结构

```
jinhui-skills/
├── README.md                   # 本文件
├── skills/                     # 所有 skill 文件存放目录
│   ├── jinhui-stack-debug/         # 全栈调试与开发规范
│   │   ├── SKILL.md            # 主入口
│   │   ├── build-test-suite/   # 构建软件测试集指南
│   │   │   └── SKILL.md
│   │   ├── good-iteration-habits/  # 良好的软件迭代习惯
│   │   │   └── SKILL.md
│   │   ├── data/               # 数据依赖型
│   │   ├── environment/        # 环境依赖型
│   │   ├── version/            # 版本依赖型
│   │   ├── config/             # 配置依赖型
│   │   ├── state/              # 状态依赖型
│   │   ├── network/            # 网络依赖型
│   │   ├── permission/         # 权限依赖型
│   │   ├── cache/              # 缓存依赖型
│   │   ├── build/              # 构建依赖型
│   │   └── runtime/            # 运行时依赖型
│   ├── rn-app-builder/         # React Native App 一键构建方案
│   │   ├── SKILL.md            # 主入口
│   │   ├── agents/             # Agent 接口配置
│   │   │   └── openai.yaml
│   │   ├── references/         # 参考文档
│   │   │   ├── auth-api.md
│   │   │   ├── simulator-keyboard-input.md
│   │   │   ├── stack.md
│   │   │   ├── structure.md
│   │   │   └── verification.md
│   │   └── scripts/            # 脚手架脚本
│   │       └── create-rn-app.py
│   ├── tauri-devtools/         # Tauri 开发调试工具集
│   │   ├── SKILL.md            # 主入口
│   │   ├── setup/              # 初始化配置
│   │   ├── session/            # Session 管理
│   │   ├── ui-automation/      # UI 自动化
│   │   ├── window/             # 窗口管理
│   │   ├── ipc/                # IPC 调试
│   │   ├── logs/               # 日志分析
│   │   └── mobile/             # 移动开发
│   ├── weapp-devtools/         # 微信小程序调试工具集
│   │   ├── SKILL.md            # 主入口
│   │   ├── setup/              # 初始化配置
│   │   ├── session/            # 连接管理
│   │   ├── ui-automation/      # UI 自动化
│   │   ├── navigation/         # 页面导航
│   │   ├── network/            # 网络操作
│   │   └── logs/               # 日志分析
│   └── web-devtools/           # 浏览器自动化工具集 (browser-use)
│       ├── SKILL.md            # 主入口
│       ├── setup/              # 初始化配置
│       ├── session/            # 会话管理
│       ├── ui-automation/      # UI 自动化
│       ├── navigation/         # 页面导航
│       ├── cloud/              # 云平台
│       ├── tunnels/            # 隧道
│       └── profile/            # Profile 管理
└── templates/                  # 模板文件
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
