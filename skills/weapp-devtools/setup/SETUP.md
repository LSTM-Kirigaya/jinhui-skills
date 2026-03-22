# WeApp DevTools - 初始化配置

> ⚠️ **这是必看文档**  
> 如果你是第一次使用 WeApp DevTools，必须完成以下配置，否则无法正常连接。

---

## 安装工具

### 方式一：全局安装（推荐）

```bash
npm install -g miniprogram-remote-control
```

安装完成后，验证是否成功：
```bash
mrc --version
# 输出: v1.0.0
```

### 方式二：npx 使用（无需安装）

```bash
npx miniprogram-remote-control <命令> [选项]
```

---

## 微信开发者工具 CLI 路径

不同操作系统下，微信开发者工具的命令行工具（CLI）位于不同位置。**必须使用该 CLI 启动自动化服务才能启用 WebSocket 连接。**

### macOS

**默认安装路径：**
```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli
```

**验证文件是否存在：**
```bash
ls -la /Applications/wechatwebdevtools.app/Contents/MacOS/cli
```

**启动自动化服务：**
```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto \
  --project /path/to/your/miniprogram \
  --auto-port 9420
```

**如果安装在其他位置：**
```bash
# 使用 mdfind 查找
mdfind -name "wechatwebdevtools.app"

# 或使用 find 查找
find /Applications -name "cli" -path "*wechatwebdevtools*" 2>/dev/null
```

---

### Windows

**默认安装路径（64位系统）：**
```cmd
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat"
```

**默认安装路径（32位系统）：**
```cmd
"C:\Program Files\Tencent\微信web开发者工具\cli.bat"
```

**验证文件是否存在：**
```cmd
dir "C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat"
```

**启动自动化服务：**
```cmd
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" auto ^
  --project C:\path\to\your\miniprogram ^
  --auto-port 9420
```

**如果安装在其他位置：**
```powershell
# 使用 PowerShell 查找
Get-ChildItem -Path "C:\Program Files*" -Recurse -Filter "cli.bat" -ErrorAction SilentlyContinue | 
  Where-Object { $_.FullName -like "*微信web开发者工具*" }

# 或使用 where 命令
where /r "C:\Program Files (x86)" cli.bat 2>nul
```

**添加到环境变量（可选，方便使用）：**
```powershell
# PowerShell 以管理员身份运行
[Environment]::SetEnvironmentVariable(
  "Path", 
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files (x86)\Tencent\微信web开发者工具", 
  "User"
)
# 重启终端后生效，然后可以直接使用：cli auto --project ...
```

---

### Linux

**注意：** 微信开发者工具官方主要支持 macOS 和 Windows。Linux 版本为社区维护版（如 `wechat-web-devtools-linux`）。

**常见安装路径：**
```bash
# 社区版（如通过 snap 安装）
/snap/bin/wechat-web-devtools

# 或手动安装
/opt/wechat-web-devtools/bin/cli

# 或用户目录
~/apps/wechat-web-devtools/bin/cli
```

**查找安装位置：**
```bash
# 使用 which
which wechat-web-devtools

# 使用 find
find /opt /usr/local ~ -name "cli" -type f 2>/dev/null | grep -i wechat

# 使用 dpkg 查找（Debian/Ubuntu）
dpkg -L wechat-web-devtools-linux 2>/dev/null | grep cli
```

---

## 启动开发者工具自动化

### 坑 1：未启动自动化服务

**错误表现：**
```
[Driver] 连接失败: connect ECONNREFUSED 127.0.0.1:9420
```

**原因：**
没有使用 CLI 启动自动化服务，WebSocket 端口未开启。

**解决方案：**

#### 方式一：CLI 启动（推荐）

请根据你的操作系统使用对应的路径：

**macOS：**
```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto \
  --project /path/to/your/miniprogram \
  --auto-port 9420
```

**Windows：**
```cmd
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" auto ^
  --project C:\path\to\your\miniprogram ^
  --auto-port 9420
```

**参数说明：**
- `--project`：小程序项目根目录（包含 `project.config.json` 的目录）
- `--auto-port`：自动化服务端口（默认 9420）

**CLI 常用命令：**
```bash
# 启动自动化服务（启用 WebSocket）
cli auto --project /path/to/project --auto-port 9420

# 打开项目（不启用自动化）
cli open --project /path/to/project

# 关闭项目
cli close --project /path/to/project

# 构建项目
cli build --project /path/to/project

# 查看帮助
cli --help
```

**验证 CLI 是否可用：**
```bash
# macOS
/Applications/wechatwebdevtools.app/Contents/MacOS/cli --version

# Windows
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" --version
```

#### 方式二：GUI 启动

1. 打开微信开发者工具
2. 导入或打开你的小程序项目
3. 点击菜单栏：**工具 → 自动化**
4. 确认端口设置（默认 9420）

---

## 验证连接

启动自动化服务后，验证连接是否正常：

```bash
# 方法 1：使用 mrc 命令
mrc where --port 9420

# 成功输出：
# [Driver] 连接成功！
# ✅ 当前页面: pages/index/index
# 📦 数据: {"path":"pages/index/index",...}

# 方法 2：检查端口占用
lsof -i :9420

# 输出示例：
# COMMAND    PID     USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# wechatweb 8806 kirigaya   30u  IPv6 ... TCP *:9420 (LISTEN)
```

---

## 项目路径配置

### 检查项目结构

确保你的小程序项目包含以下文件：

```
miniprogram-project/
├── project.config.json      # 项目配置文件（必需）
├── app.json                 # 小程序全局配置
├── app.js                   # 小程序逻辑
├── pages/                   # 页面目录
│   └── index/
│       ├── index.wxml
│       ├── index.js
│       └── index.wxss
└── ...
```

### project.config.json 示例

```json
{
  "description": "项目配置文件",
  "packOptions": {
    "ignore": []
  },
  "setting": {
    "urlCheck": true,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "preloadBackgroundData": false,
    "minified": true,
    "newFeature": false,
    "coverView": true,
    "nodeModules": false,
    "autoAudits": false,
    "showShadowRootInWxss": true,
    "scopeDataCheck": false,
    "uglifyFileName": false,
    "checkInvalidKey": true,
    "checkSiteMap": true,
    "uploadWithSourceMap": true,
    "compileHotReLoad": false,
    "lazyloadPlaceholderEnable": false,
    "useMultiFrameRuntime": true,
    "useApiHook": true,
    "useApiHostProcess": true,
    "babelSetting": {
      "ignore": [],
      "disablePlugins": [],
      "outputPath": ""
    },
    "enableEngineNative": false,
    "useIsolateContext": false,
    "userConfirmedBundleSwitch": false,
    "packNpmManually": false,
    "packNpmRelationList": [],
    "minifyWXSS": true,
    "disableUseStrict": false,
    "minifyWXML": true,
    "showES6CompileOption": false,
    "useCompilerPlugins": false
  },
  "compileType": "miniprogram",
  "libVersion": "2.19.4",
  "appid": "your-app-id",
  "projectname": "your-project-name",
  "condition": {}
}
```

---

## 端口配置

### 默认端口

- **9420**：微信开发者工具自动化服务默认端口

### 自定义端口

如果 9420 被占用，可以使用其他端口：

```bash
# 启动时使用自定义端口
cli auto --project /path/to/project --auto-port 9421

# 命令中指定端口
mrc where --port 9421
```

### 检查端口占用

```bash
# macOS/Linux
lsof -i :9420

# Windows
netstat -ano | findstr :9420
```

---

## 验证配置清单

- [ ] 安装 `miniprogram-remote-control` 工具
- [ ] 确认小程序项目包含 `project.config.json`
- [ ] 启动微信开发者工具自动化服务
- [ ] 验证端口 9420 正在监听
- [ ] 运行 `mrc where --port 9420` 测试连接

---

## 常见问题

**Q: 为什么提示 "Connection refused"？**  
A: 开发者工具自动化服务未启动。请按上述步骤启动自动化服务。

**Q: 为什么提示 "command not found: cli" 或 "'cli' 不是内部或外部命令"？**  
A: 需要使用微信开发者工具的完整路径。请参考上方的【微信开发者工具 CLI 路径】章节，根据你的操作系统找到正确的 CLI 位置。

**Q: 提示 "No such file or directory" 找不到 cli？**  
A: 
- **macOS**: 确认应用安装在 `/Applications` 目录，或使用 `mdfind -name "wechatwebdevtools.app"` 查找实际位置
- **Windows**: 确认安装路径，或使用 `where cli.bat` 查找，注意安装路径可能有空格需要用引号包裹
- **Linux**: 微信开发者工具官方不支持 Linux，需要使用社区版

**Q: 如何停止自动化服务？**  
A: 关闭微信开发者工具即可，或按 `Ctrl+C` 停止 CLI 进程。

**Q: 可以同时连接多个小程序吗？**  
A: 可以，使用不同端口启动多个开发者工具实例。

**Q: 支持真机调试吗？**  
A: 不支持。miniprogram-automator 只能在开发者工具模拟器中使用。

**Q: 启动 CLI 后显示端口被占用？**  
A: 使用其他端口启动：
```bash
# 使用 9421 端口
cli auto --project /path/to/project --auto-port 9421

# mrc 命令也要对应修改
mrc where --port 9421
```
