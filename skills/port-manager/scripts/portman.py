#!/usr/bin/env python3
"""Manage project port allocations in ~/.port-man"""

import json
import os
import sys
from pathlib import Path

PORT_MAN_FILE = Path.home() / ".port-man"
DEFAULT_MIN_PORT = 3000
DEFAULT_MAX_PORT = 8999
COMMON_RESERVED = {80, 443, 8080, 3000, 5173, 8000, 5000}


def load_db():
    if PORT_MAN_FILE.exists():
        try:
            with open(PORT_MAN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"version": "1.0", "projects": {}}


def save_db(db):
    PORT_MAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PORT_MAN_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def get_used_ports(db):
    used = set()
    for proj in db.get("projects", {}).values():
        for port in proj.get("services", {}).values():
            used.add(port)
    return used


def find_available_port(db, preferred=None, min_port=DEFAULT_MIN_PORT, max_port=DEFAULT_MAX_PORT):
    used = get_used_ports(db)
    if preferred is not None:
        if preferred not in used and min_port <= preferred <= max_port:
            return preferred
    for port in range(min_port, max_port + 1):
        if port not in used and port not in COMMON_RESERVED:
            return port
    raise RuntimeError(f"No available port found in range {min_port}-{max_port}")


def get_port(project_path, service_name, preferred=None):
    db = load_db()
    abs_path = str(Path(project_path).resolve())
    projects = db.setdefault("projects", {})
    proj = projects.setdefault(abs_path, {"services": {}})
    services = proj.setdefault("services", {})

    if service_name in services:
        print(services[service_name])
        return services[service_name]

    port = find_available_port(db, preferred=int(preferred) if preferred else None)
    services[service_name] = port
    save_db(db)
    print(port)
    return port


def list_all():
    db = load_db()
    print(json.dumps(db, indent=2, ensure_ascii=False))
    return db


def free_port(project_path, service_name):
    db = load_db()
    abs_path = str(Path(project_path).resolve())
    projects = db.get("projects", {})
    if abs_path in projects and service_name in projects[abs_path].get("services", {}):
        del projects[abs_path]["services"][service_name]
        if not projects[abs_path]["services"]:
            del projects[abs_path]
        save_db(db)
        print(f"Freed {service_name} from {abs_path}")
    else:
        print(f"Not found: {service_name} in {abs_path}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: portman.py <get|list|free> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "get":
        if len(sys.argv) < 4:
            print("Usage: portman.py get <project_path> <service_name> [preferred_port]", file=sys.stderr)
            sys.exit(1)
        get_port(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "list":
        list_all()
    elif cmd == "free":
        if len(sys.argv) < 4:
            print("Usage: portman.py free <project_path> <service_name>", file=sys.stderr)
            sys.exit(1)
        free_port(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
