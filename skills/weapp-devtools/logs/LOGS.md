# 日志分析

读取小程序运行时的控制台日志。

---

## 📋 获取控制台日志

读取小程序控制台输出的日志。

```bash
mrc logs [级别] [数量] --port 9420
```

**参数说明：**
- `级别`：可选，日志级别（`log`, `info`, `warn`, `error`, `debug`），默认 `log`
- `数量`：可选，获取的日志条数，默认获取全部

**基础示例：**
```bash
# 获取所有日志
mrc logs --port 9420

# 获取最近 10 条日志
mrc logs 10 --port 9420

# 获取最近 20 条日志（带级别）
mrc logs log 20 --port 9420
```

**输出示例：**
```
✅ 获取到 3 条日志
📦 数据: {
  "count": 3,
  "logs": [
    {"level": "log", "message": "Page onLoad", "timestamp": 1234567890},
    {"level": "info", "message": "User logged in", "timestamp": 1234567891},
    {"level": "warn", "message": "Network slow", "timestamp": 1234567892}
  ]
}
```

---

## ⚠️ 获取错误日志

只获取 `error` 级别的日志。

```bash
mrc errors [数量] --port 9420
```

**示例：**
```bash
# 获取所有错误日志
mrc errors --port 9420

# 获取最近 10 条错误
mrc errors 10 --port 9420
```

**输出示例：**
```
✅ 获取到 2 条错误
📦 数据: {
  "count": 2,
  "logs": [
    {
      "level": "error",
      "message": "TypeError: Cannot read property 'name' of undefined",
      "timestamp": 1234567890
    },
    {
      "level": "error",
      "message": "Network request failed",
      "timestamp": 1234567891
    }
  ]
}
```

---

## ⚡ 获取警告日志

只获取 `warn` 级别的日志。

```bash
mrc warnings [数量] --port 9420
```

**示例：**
```bash
# 获取所有警告
mrc warnings --port 9420

# 获取最近 5 条警告
mrc warnings 5 --port 9420
```

---

## 📊 按级别筛选日志

使用 `logs` 命令指定级别：

```bash
# 获取 info 级别日志
mrc logs info --port 9420
mrc logs info 10 --port 9420

# 获取 debug 级别日志
mrc logs debug --port 9420

# 获取 warn 级别日志
mrc logs warn 20 --port 9420
```

---

## 典型工作流

### 场景 1：调试错误

```bash
# 1. 先清空日志（重启页面）
mrc relaunch /pages/index/index --port 9420

# 2. 执行触发错误的操作
mrc click view --port 9420
mrc wait 1000 --port 9420

# 3. 查看错误日志
mrc errors 20 --port 9420

# 4. 截图记录错误页面
mrc screenshot ./error.png --port 9420
```

### 场景 2：性能分析

```bash
# 1. 启动页面
mrc relaunch /pages/list/index --port 9420

# 2. 等待加载完成
mrc wait 3000 --port 9420

# 3. 查看所有日志
mrc logs 50 --port 9420

# 4. 检查警告（可能的性能问题）
mrc warnings 20 --port 9420
```

### 场景 3：网络请求调试

```bash
# 1. 执行操作触发网络请求
mrc click view --port 9420

# 2. 等待请求完成
mrc wait 2000 --port 9420

# 3. 查看日志中的网络信息
mrc logs info 30 --port 9420
```

---

## 日志格式说明

每条日志包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `level` | string | 日志级别：`log`, `info`, `warn`, `error`, `debug` |
| `message` | string | 日志内容 |
| `timestamp` | number | 时间戳（毫秒） |

**示例日志条目：**
```json
{
  "level": "error",
  "message": "TypeError: Cannot read property 'length' of undefined\n  at pages/index/index.js:45:12",
  "timestamp": 1711036800000
}
```

---

## 日志级别说明

| 级别 | 说明 | 使用场景 |
|------|------|---------|
| `log` | 普通日志 | 一般调试信息 |
| `info` | 信息日志 | 关键流程记录 |
| `warn` | 警告 | 潜在问题提示 |
| `error` | 错误 | 错误和异常 |
| `debug` | 调试 | 详细调试信息 |

---

## 实用技巧

### 技巧 1：实时监控日志

```bash
# 使用 watch 命令定期查看（macOS/Linux）
watch -n 2 'mrc logs error 5 --port 9420'
```

### 技巧 2：日志分析脚本

```bash
#!/bin/bash
# check-errors.sh

PORT=9420

# 获取错误日志
ERRORS=$(mrc errors 10 --port $PORT 2>/dev/null)

# 检查是否有错误
if echo "$ERRORS" | grep -q '"count": 0'; then
  echo "✅ 没有错误"
else
  echo "⚠️ 发现错误："
  echo "$ERRORS"
fi
```

### 技巧 3：操作前后对比日志

```bash
# 1. 记录操作前日志行数
BEFORE=$(mrc logs --port 9420 | grep -o '"count":[0-9]*' | cut -d: -f2)
echo "操作前日志数: $BEFORE"

# 2. 执行操作
mrc click view --port 9420
mrc wait 2000 --port 9420

# 3. 记录操作后日志行数
AFTER=$(mrc logs --port 9420 | grep -o '"count":[0-9]*' | cut -d: -f2)
echo "操作后日志数: $AFTER"

# 4. 计算新增日志
NEW=$((AFTER - BEFORE))
echo "新增日志: $NEW"
```

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 获取不到日志 | 日志已被清除 | 重启页面后重新获取 |
| 日志数量不对 | 日志缓冲区限制 | 增加获取数量或使用更低级别 |
| 时间戳不正确 | 时区问题 | 日志时间戳为相对时间 |
| 日志内容被截断 | 消息过长 | 检查原始控制台输出 |

---

## 日志命令速查表

| 命令 | 作用 | 示例 |
|------|------|------|
| `logs` | 获取所有日志 | `mrc logs 20 --port 9420` |
| `logs <级别>` | 按级别获取 | `mrc logs error 10 --port 9420` |
| `errors` | 获取错误日志 | `mrc errors 5 --port 9420` |
| `warnings` | 获取警告日志 | `mrc warnings 10 --port 9420` |

---

## 参考

- [微信小程序调试指南](https://developers.weixin.qq.com/miniprogram/dev/framework/usability/debug.html)
- [微信开发者工具控制台](https://developers.weixin.qq.com/miniprogram/dev/devtools/debug.html#%E6%8E%A7%E5%88%B6%E5%8F%B0)
