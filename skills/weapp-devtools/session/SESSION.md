# 连接管理

管理与微信开发者工具的连接。所有调试功能都依赖活跃的连接。

---

## 检查连接状态

### 方法 1：使用 mrc 命令

```bash
mrc where --port 9420
```

**成功输出：**
```
[Driver] 正在连接到 ws://localhost:9420 ...
[Driver] 连接成功！
✅ 当前页面: pages/index/index
📦 数据: {
  "path": "pages/index/index",
  "query": {},
  "url": "pages/index/index?"
}
```

**失败输出：**
```
[Driver] 连接失败: connect ECONNREFUSED 127.0.0.1:9420
```

### 方法 2：检查系统端口

```bash
# 检查 9420 端口是否被占用
lsof -i :9420
```

**正常状态输出：**
```
COMMAND    PID     USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
wechatweb 8806 kirigaya   30u  IPv6 0x62b02e26226f6c8b      0t0  TCP *:9420 (LISTEN)
```

---

## 连接生命周期

### 1. 启动自动化服务

**根据操作系统使用对应的 CLI 路径：**

**macOS：**
```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto \
  --project /path/to/project \
  --auto-port 9420
```

**Windows：**
```cmd
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" auto ^
  --project C:\path\to\project ^
  --auto-port 9420
```

> 📖 找不到 CLI？请参考 [setup/SETUP.md](../setup/SETUP.md) 查看详细路径说明

### 2. 验证连接

```bash
# 获取当前页面信息
mrc where --port 9420

# 获取系统信息
mrc sysinfo --port 9420
```

### 3. 保持连接

连接是**无状态**的，每次命令执行时会自动建立 WebSocket 连接，执行完成后断开。

### 4. 断开连接

关闭微信开发者工具或停止 CLI 进程即可断开。

---

## 多项目连接

### 使用不同端口

如果有多个小程序项目需要同时调试：

```bash
# 项目 A - 端口 9420
cli auto --project /path/to/project-a --auto-port 9420
mrc where --port 9420

# 项目 B - 端口 9421
cli auto --project /path/to/project-b --auto-port 9421
mrc where --port 9421
```

### 快捷命令设置

可以为常用端口设置别名：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias mrc-a='mrc --port 9420'
alias mrc-b='mrc --port 9421'

# 使用
mrc-a where
mrc-b screenshot ./shot.png
```

---

## 连接问题排查

### 问题 1：Connection refused

**症状：**
```
[Driver] 连接失败: connect ECONNREFUSED 127.0.0.1:9420
```

**原因：**
- 开发者工具未启动
- 自动化服务未开启（**必须使用 CLI 启动，而非直接打开应用**）
- 端口错误

**解决方案：**

**Step 1: 确认使用正确的 CLI 路径启动**

**macOS:**
```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto \
  --project /path/to/project --auto-port 9420
```

**Windows:**
```cmd
"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" auto ^
  --project C:\path\to\project --auto-port 9420
```

**Step 2: 检查开发者工具是否运行**
```bash
# macOS
ps aux | grep wechatwebdevtools

# Windows
tasklist | findstr wechatdevtools
```

**Step 3: 检查端口是否监听**
```bash
# macOS
lsof -i :9420

# Windows
netstat -ano | findstr :9420
```

**Step 4: 确认 CLI 文件存在**
```bash
# macOS
ls -la /Applications/wechatwebdevtools.app/Contents/MacOS/cli

# Windows
dir "C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat"
```

### 问题 2：Upgrade Required

**症状：**
```bash
curl http://localhost:9420/json
# 输出: Upgrade Required
```

**说明：**
这是**正常现象**！开发者工具使用的是 WebSocket 协议，curl 使用 HTTP 访问时会返回此提示。使用 `mrc` 命令即可正常连接。

### 问题 3：连接超时

**症状：**
```
[Driver] 连接超时
```

**原因：**
- 开发者工具卡死
- 端口被防火墙拦截

**解决方案：**
```bash
# 1. 重启开发者工具
# 2. 检查防火墙设置
# 3. 尝试更换端口
cli auto --project /path/to/project --auto-port 9421
```

---

## 典型工作流

```bash
# 1. 启动开发者工具自动化
cli auto --project /path/to/project --auto-port 9420

# 2. 验证连接
mrc where --port 9420

# 3. 执行调试操作...
mrc screenshot ./shot.png --port 9420
mrc sysinfo --port 9420

# 4. 完成后关闭开发者工具或停止 CLI
```

---

## 故障排除速查表

| 问题 | 检查项 | 解决方案 |
|------|--------|---------|
| Connection refused | 开发者工具是否启动 | 重新启动自动化服务 |
| Connection refused | 端口是否正确 | 检查 `--auto-port` 参数 |
| 连接超时 | 开发者工具是否卡死 | 重启开发者工具 |
| 命令无响应 | WebSocket 是否正常 | 检查网络/防火墙设置 |
