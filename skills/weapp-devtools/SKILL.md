---
name: weapp-devtools
description: 用于调试微信小程序的自动化工具集，基于 miniprogram-automator 封装，提供截图、元素检查、页面导航、网络 Mock 等功能。Use when working with WeChat Mini Programs for: (1) Debugging UI with screenshots and element inspection, (2) Automating interactions like clicks, input, and swipes, (3) Navigating between pages and tabs, (4) Mocking network requests, (5) Reading console logs and errors.
---

# WeApp DevTools

用于调试微信小程序的自动化工具集，基于 miniprogram-automator 封装，提供截图、元素检查、页面导航、网络 Mock 等功能。

## 快速开始

### 第一步：检查环境

```bash
# 检查是否安装了 mrc (miniprogram-remote-control)
mrc --version

# 检查微信开发者工具是否在 9420 端口运行
lsof -i :9420
```

### 第二步：启动开发者工具自动化

**⚠️ 重要：不同系统 CLI 路径不同，请根据你的系统选择正确的命令：**

**macOS：**
```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto \
  --project /path/to/miniprogram \
  --auto-port 9420
```

**Windows：**
```cmd
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" auto ^
  --project C:\path\to\miniprogram ^
  --auto-port 9420
```

> 📖 **详细路径说明**请参考 [setup/SETUP.md](./setup/SETUP.md) 的【微信开发者工具 CLI 路径】章节

**或 GUI 方式：** 微信开发者工具 → 菜单栏 → 工具 → 自动化

### 第三步：基础调试

```bash
# 截图查看当前页面
mrc screenshot ./debug.png --port 9420

# 获取当前页面信息
mrc where --port 9420

# 获取系统信息
mrc sysinfo --port 9420
```

---

## 📚 完整功能目录

> 以下功能按类别组织，点击链接查看详细用法。

### 🔧 [初始化配置](./setup/SETUP.md)

**新项目的必要配置** - 如果这是你第一次使用 WeApp DevTools，请先看这里。

包含：
- 安装 miniprogram-remote-control
- 启动开发者工具自动化服务
- 项目路径配置
- 端口配置

---

### 🔌 [连接管理](./session/SESSION.md)

管理与微信开发者工具的连接。

**常用命令：**
```bash
# 测试连接
mrc where --port 9420

# 检查连接状态
lsof -i :9420
```

---

### 🎯 [UI 自动化](./ui-automation/UI_AUTOMATION.md)

核心调试功能：截图、元素检查、点击、输入、滑动等。

**功能列表：**
- 📸 页面截图
- 🔍 元素存在检查
- 👆 点击/长按/双击元素
- ⌨️ 输入文本
- 🎨 获取元素样式
- ⏱️ 等待元素
- 📜 JavaScript 执行

---

### 🧭 [页面导航](./navigation/NAVIGATION.md)

管理小程序页面跳转和导航。

**功能列表：**
- Tab 页面切换
- 页面返回
- 重启到指定页面
- 获取页面栈信息

---

### 🌐 [网络操作](./network/NETWORK.md)

网络请求拦截和 Mock。

**功能列表：**
- Mock 网络请求
- 移除 Mock
- 清除所有 Mock

---

### 📝 [日志分析](./logs/LOGS.md)

读取小程序运行时日志。

**功能列表：**
- 读取控制台日志
- 读取错误日志
- 读取警告日志

---

## 典型调试工作流

### 场景 1：检查 UI 问题

```bash
# 1. 截图看当前状态
mrc screenshot ./issue.png --port 9420

# 2. 检查关键元素是否存在
mrc exists view --port 9420
mrc exists button --port 9420

# 3. 查看控制台日志
mrc logs error 20 --port 9420
```

### 场景 2：测试表单交互

```bash
# 1. 先截图确认初始状态
mrc screenshot ./before.png --port 9420

# 2. 检查输入框是否存在
mrc exists textarea --port 9420

# 3. 输入文本
mrc type textarea "测试内容" --port 9420

# 4. 截图看结果
mrc screenshot ./after.png --port 9420
```

### 场景 3：测试页面导航

```bash
# 1. 切换到 Tab 页面
mrc switchTab /pages/community/index --port 9420

# 2. 点击某个元素
mrc click view --port 9420

# 3. 查看页面栈
mrc stack --port 9420

# 4. 返回上一页
mrc back --port 9420
```

---

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| `Connection refused` | 开发者工具未启动自动化 | [查看初始化配置](./setup/SETUP.md) |
| `Failed to connect` | 端口被占用或错误 | 检查 `lsof -i :9420`，更换端口 |
| `Element not found` | 选择器错误或元素未加载 | 先截图确认，使用 `wait` 等待 |
| `Screenshot timeout` | 文件路径权限问题 | 使用相对路径或检查目录权限 |
| 命令无响应 | WebSocket 连接断开 | 重新启动开发者工具自动化 |

---

## 参考

- [miniprogram-automator 官方文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/auto/automator.html)
- [微信开发者工具文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/cli.html)
- [GitHub: miniprogram-remote-control](https://github.com/LSTM-Kirigaya/miniprogram-remote-control)
