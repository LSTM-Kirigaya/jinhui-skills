---
name: port-manager
description: "为本地开发服务器分配并注入唯一端口号，防止同一台电脑上多个项目的端口冲突。启动任何开发服务器前，务必先通过 portman 脚本从 ~/.port-man 获取端口，并以 PORT=<端口> 原命令 的方式注入启动（例如 PORT=3001 npm run dev）。适用于：(1) 启动 Vite、Webpack、Next.js、后端 API 等开发服务器，(2) 配置多服务项目，(3) 避免与已有项目占用 3000、8080 等常用端口冲突，(4) 查看或更新 ~/.port-man 全局端口注册表。"
tags:
  - port
  - development
  - devops
  - cli
model: deepseek-chat
rootUrl: https://cdn.jsdelivr.net/gh/LSTM-Kirigaya/jinhui-skills@main/skills/port-manager/SKILL.md
---

# 端口管理器（Port Manager）

为每个项目服务分配唯一的网络端口，并在启动开发服务器时**通过环境变量注入**，避免同一台机器上不同项目之间的端口冲突。

## 核心规则

当此 skill 被触发时，**必须先通过 `~/.port-man` 获取端口**，然后将 `PORT=<端口>`（或框架对应的端口变量）前置到原启动命令中。

```bash
# 1. 为该服务分配或获取已有端口
PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) frontend)

# 2. 注入端口并启动开发服务器
PORT=$PORT npm run dev
```

大多数前端工具（Vite、Next.js、CRA）都支持 `PORT` 环境变量。若框架使用其他变量，请按需调整：

- `PORT` — Vite、Next.js、Create React App、Express、Fastify
- `VITE_DEV_PORT` / `SERVER_PORT` — 部分自定义配置
- `--port` CLI 参数 — `npm run dev -- --port $PORT`

## 快速开始

### 分配端口并启动服务

```bash
PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) frontend)
PORT=$PORT npm run dev
```

若该服务已有记录端口，脚本会直接返回；否则自动寻找下一个可用端口并持久化记录。

### 查看所有已分配端口

```bash
python3 skills/port-manager/scripts/portman.py list
```

### 释放端口占用

```bash
python3 skills/port-manager/scripts/portman.py free <项目路径> <服务名>
```

## 标准工作流

为项目启动任何开发服务器时：

1. **获取端口**（必要时自动分配）：
   ```bash
   PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) web)
   ```

2. **将端口注入启动命令**：
   ```bash
   PORT=$PORT npm run dev
   ```

   同一项目多个服务可并行启动：
   ```bash
   FRONTEND_PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) frontend)
   BACKEND_PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) backend)
   
   PORT=$FRONTEND_PORT npm run dev:web &
   PORT=$BACKEND_PORT npm run dev:api &
   ```

3. **持久化配置（可选）**：将分配的端口写入 `.env` 或 `docker-compose.yml`，方便团队或 CI 查看，但建议始终保留命令行注入的习惯以确保端口被真正预留。

## 数据格式

`~/.port-man` 为 JSON 文件：

```json
{
  "version": "1.0",
  "projects": {
    "/Users/me/project-a": {
      "services": {
        "frontend": 3001,
        "backend": 5001
      }
    }
  }
}
```

## 注意事项

- **务必通过环境变量注入端口**（`PORT=xxx <命令>`），不要依赖写死的默认端口。
- 脚本会自动跳过常用保留端口（如 80、443、8080），减少与系统默认服务的冲突。
- 始终以项目的**绝对路径**作为键值。
- `~/.port-man` 是机器本地文件，不建议提交到共享仓库。

