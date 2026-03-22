# UI 自动化

用于检查、操作小程序 UI 的核心功能集合。

---

## 📸 截图

捕获小程序当前画面。

```bash
# 基础截图（保存到当前目录）
mrc screenshot ./screenshot.png --port 9420

# 保存到绝对路径
mrc screenshot /Users/username/Desktop/shot.png --port 9420

# 保存到临时目录
mrc screenshot /tmp/wxapp.png --port 9420
```

**输出示例：**
```
[Driver] 连接成功！
✅ 截图已保存: ./screenshot.png
📦 数据: {
  "path": "./screenshot.png"
}
```

**常用场景：**
- 记录 UI 状态
- 对比操作前后变化
- 生成测试报告

**⚠️ 注意：**
- 确保保存路径有写入权限
- 相对路径基于当前工作目录
- 截图尺寸与开发者工具模拟器设置一致

---

## 🔍 元素存在检查

检查页面中是否存在指定元素。

```bash
# 基础选择器（元素类型）
mrc exists view --port 9420
mrc exists button --port 9420
mrc exists text --port 9420
mrc exists image --port 9420
mrc exists input --port 9420
mrc exists textarea --port 9420
mrc exists scroll-view --port 9420
mrc exists swiper --port 9420

# 类名选择器
mrc exists ".container" --port 9420
mrc exists ".navbar" --port 9420

# ID 选择器
mrc exists "#submit-btn" --port 9420

# 属性选择器
mrc exists "[class*='friend']" --port 9420
mrc exists "[class*='rank']" --port 9420
```

**输出示例（存在）：**
```
✅ 元素 view 存在
📦 数据: {
  "selector": "view",
  "exists": true
}
```

**输出示例（不存在）：**
```
✅ 元素 .test-class 不存在
📦 数据: {
  "selector": ".test-class",
  "exists": false
}
```

---

## 👆 点击元素

### 单击

```bash
# 点击 view 元素
mrc click view --port 9420

# 使用 tap 别名
mrc tap view --port 9420

# 点击特定类名元素
mrc click ".submit-btn" --port 9420

# 点击 ID 元素
mrc click "#confirm" --port 9420
```

### 双击

```bash
mrc doubleTap view --port 9420
```

### 长按

```bash
mrc longPress view --port 9420
```

**输出示例：**
```
✅ 点击成功: view
📦 数据: {
  "selector": "view"
}
```

---

## ⌨️ 输入文本

在输入框中输入文本。

```bash
# 基础输入
mrc type textarea "测试文本" --port 9420

# 使用 input 别名
mrc input textarea "测试文本" --port 9420

# 输入带空格的文本（使用引号）
mrc type input "Hello World" --port 9420

# 输入多行文本
mrc type textarea "第一行
第二行
第三行" --port 9420
```

**⚠️ 注意：**
- 输入前需确保元素存在
- 建议先使用 `mrc exists` 检查
- 支持 `input` 和 `textarea` 组件

**完整示例：**
```bash
# 1. 检查 textarea 是否存在
mrc exists textarea --port 9420

# 2. 输入文本
mrc type textarea "这是一份测试的早餐记录" --port 9420

# 3. 截图验证
mrc screenshot ./typed.png --port 9420
```

---

## 🎨 获取元素样式

获取元素的 CSS 样式信息。

```bash
# 获取 view 元素样式
mrc style view --port 9420

# 获取特定类名元素样式
mrc style ".container" --port 9420
```

---

## ⏱️ 等待元素

等待元素出现。

```bash
# 等待 view 元素出现
mrc waitFor view --port 9420

# 等待特定类名元素
mrc waitFor ".loading-complete" --port 9420
```

---

## 💤 固定等待

等待指定时间（毫秒）。

```bash
# 等待 1 秒
mrc wait 1000 --port 9420

# 使用 sleep 别名
mrc sleep 500 --port 9420

# 等待 3 秒
mrc wait 3000 --port 9420
```

**输出示例：**
```
✅ 等待了 1000ms
📦 数据: {
  "waited": 1000
}
```

**常用场景：**
- 等待页面加载完成
- 等待动画执行完毕
- 等待网络请求返回

---

## 📜 执行 JavaScript

在小程序上下文中执行任意 JS。

```bash
# 简单表达式
mrc evaluate "wx.getSystemInfoSync()" --port 9420

# 获取当前页面信息
mrc evaluate "getCurrentPages()" --port 9420

# 获取页面数据
mrc evaluate "getCurrentPages()[0].data" --port 9420

# 调用页面方法
mrc evaluate "getCurrentPages()[0].onLoad()" --port 9420
```

**⚠️ 限制：**
- 小程序环境，非完整浏览器环境
- 无法访问 DOM API（如 `document.querySelector`）
- 返回值需为 JSON 可序列化

---

## 🔄 滑动操作

```bash
# 滑动屏幕
mrc swipe --port 9420
```

---

## 📝 设置页面数据

直接设置页面的 data。

```bash
mrc setData '{"key": "value"}' --port 9420
```

---

## 实用技巧

### 技巧 1：检查所有常见元素

```bash
# 检查页面中的主要元素类型
for elem in view text image button input textarea scroll-view; do
  echo "Checking $elem..."
  mrc exists $elem --port 9420
done
```

### 技巧 2：表单自动填写

```bash
#!/bin/bash
# form-fill.sh

PORT=9420

# 检查并填写表单
mrc exists textarea --port $PORT && \
mrc type textarea "自动填写的测试内容" --port $PORT && \
mrc wait 500 --port $PORT && \
mrc click ".submit-btn" --port $PORT && \
mrc screenshot ./form-submitted.png --port $PORT
```

### 技巧 3：操作前后对比

```bash
# 操作前截图
mrc screenshot ./before.png --port 9420

# 执行操作
mrc click view --port 9420
mrc wait 1000 --port 9420

# 操作后截图
mrc screenshot ./after.png --port 9420

# 对比两张截图
```

### 技巧 4：批量检查元素

```bash
# 快速检查多个元素
mrc exists "[class*='friend']" --port 9420
mrc exists "[class*='rank']" --port 9420
mrc exists "[class*='card']" --port 9420
```

---

## 故障排除

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `Element not found` | 选择器错误或元素未加载 | 检查选择器，先用截图确认 |
| `Screenshot timeout` | 文件路径权限问题 | 使用相对路径或检查目录权限 |
| `Input failed` | 元素不是输入框 | 确保元素是 `input` 或 `textarea` |
| `Click no effect` | 元素被覆盖或不可点击 | 截图确认元素位置 |

---

## 参考

- [微信小程序组件列表](https://developers.weixin.qq.com/miniprogram/dev/component/)
- [miniprogram-automator API](https://developers.weixin.qq.com/miniprogram/dev/devtools/auto/automator.html)
