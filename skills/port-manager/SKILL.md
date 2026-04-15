---
name: port-manager
description: "Manage and allocate network ports across multiple local projects to prevent port conflicts. Use when: (1) Starting a new development server and needing a free port, (2) Configuring multi-service projects (frontend/backend/devtools), (3) Avoiding collisions with other projects already using common ports like 3000 or 8080, (4) Reading or updating the global ~/.port-man registry."
---

# Port Manager

Manage project service ports globally via `~/.port-man` to avoid conflicts between multiple projects on the same machine.

## Quick Start

### Allocate a port for a service

```bash
python3 skills/port-manager/scripts/portman.py get <project_path> <service_name>
```

Example:
```bash
python3 skills/port-manager/scripts/portman.py get /Users/me/project-a frontend
# Output: 3001
```

If the service already has a port assigned, it returns the existing port. Otherwise it allocates the next available port and records it.

### View all allocated ports

```bash
python3 skills/port-manager/scripts/portman.py list
```

### Free a port allocation

```bash
python3 skills/port-manager/scripts/portman.py free <project_path> <service_name>
```

## Workflow for New Projects

When configuring a new project (or a new service in an existing project):

1. **Check existing allocations**:
   ```bash
   python3 skills/port-manager/scripts/portman.py list
   ```

2. **Allocate ports for each service**:
   ```bash
   python3 skills/port-manager/scripts/portman.py get $(pwd) web
   python3 skills/port-manager/scripts/portman.py get $(pwd) api
   python3 skills/port-manager/scripts/portman.py get $(pwd) websocket
   ```

3. **Write the returned ports into the project's config files** (e.g., `.env`, `vite.config.ts`, `docker-compose.yml`).

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

- Always use the **absolute path** of the project as the key.
- The script automatically skips commonly reserved ports (e.g., 80, 443, 8080) to reduce collisions with system or hard-coded defaults.
- If a service already has a recorded port, `get` returns it without modification.
- Keep `~/.port-man` in version control only if it is machine-specific; do not commit it to shared repositories.
