---
name: port-manager
description: "Allocate and inject unique network ports for local development servers to avoid cross-project conflicts. ALWAYS use before starting a dev server: first run the portman script to get a free port from ~/.port-man, then prepend it as PORT=<port> to the original start command (e.g., PORT=3001 npm run dev). Use when: (1) Launching any development server (Vite, Webpack, Next.js, backend API, etc.), (2) Configuring multi-service projects, (3) Avoiding collisions with ports like 3000 or 8080 already used by other projects, (4) Reading or updating the global ~/.port-man registry."
tags:
  - port
  - development
  - devops
  - cli
model: deepseek-chat
rootUrl: https://cdn.jsdelivr.net/gh/LSTM-Kirigaya/jinhui-skills@main/skills/port-manager/SKILL.md
---

# Port Manager

Allocate unique network ports for each project service and **inject them via environment variables** when launching development servers, preventing cross-project conflicts on the same machine.

## Core Rule

When this skill is active, **always obtain a port from `~/.port-man` first**, then prepend `PORT=<port>` (or the framework-specific port variable) to the original start command.

```bash
# 1. Allocate / retrieve the port for this service
PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) frontend)

# 2. Launch the dev server with the port injected
PORT=$PORT npm run dev
```

Most frontend tools (Vite, Next.js, CRA) respect the `PORT` environment variable. For frameworks that use a different variable, adjust accordingly:

- `PORT` — Vite, Next.js, Create React App, Express, Fastify
- `VITE_DEV_PORT` / `SERVER_PORT` — some custom setups
- `--port` CLI flag — `npm run dev -- --port $PORT`

## Quick Start

### Allocate a port and start a server

```bash
PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) frontend)
PORT=$PORT npm run dev
```

If the service already has a port assigned, the script returns the existing port. Otherwise it finds the next available port and records it.

### View all allocated ports

```bash
python3 skills/port-manager/scripts/portman.py list
```

### Free a port allocation

```bash
python3 skills/port-manager/scripts/portman.py free <project_path> <service_name>
```

## Standard Workflow

When starting any development server for a project:

1. **Get the port** (allocating if necessary):
   ```bash
   PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) web)
   ```

2. **Inject it into the start command**:
   ```bash
   PORT=$PORT npm run dev
   ```

   Or for multiple services in the same project:
   ```bash
   FRONTEND_PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) frontend)
   BACKEND_PORT=$(python3 skills/port-manager/scripts/portman.py get $(pwd) backend)
   
   PORT=$FRONTEND_PORT npm run dev:web &
   PORT=$BACKEND_PORT npm run dev:api &
   ```

3. **For persistent configs** (optional): write the returned ports into `.env` or `docker-compose.yml` so teammates or CI can see them, but keep the live command injection habit to guarantee the port is reserved.

## Data Format

`~/.port-man` is a JSON file:

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

## Important Notes

- **Always inject the port via environment variable** (`PORT=xxx <command>`) rather than relying on hard-coded defaults.
- The script skips commonly reserved ports (e.g., 80, 443, 8080) to reduce collisions.
- Use the project's **absolute path** as the key.
- Do not commit `~/.port-man` to shared repositories; it is machine-specific.
