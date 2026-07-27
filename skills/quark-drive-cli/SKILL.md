---
name: quark-drive-cli
description: Use the unofficial i-sync/quark-cli command line client to inspect, upload, resume, download, move, rename, delete, and verify files in Quark Drive. Apply when a user asks about 夸克网盘 CLI, terminal or NAS transfers, batch migration, resumable uploads/downloads, JSON automation, or safe post-upload cleanup.
rootUrl: https://raw.githubusercontent.com/LSTM-Kirigaya/jinhui-skills/refs/heads/codex/quark-drive-cli-20260727/skills/quark-drive-cli/SKILL.md
---

# Quark Drive CLI

Use `quark` for Quark Drive file operations while treating its browser Cookie as a password. Read [references/cli-reference.md](references/cli-reference.md) before composing commands or performing a migration.

## Workflow

1. Run `command -v quark && quark --version` and require a supported installed binary.
2. Run `quark auth show-source` without printing the Cookie. If authentication is absent or expired, ask the user to authenticate with `quark auth set-cookie --from-stdin`.
3. Inspect both local and remote trees before writing. Use `quark ls <remote> --json` and `quark stat <remote> --json` for machine-readable checks.
4. Identify exact name collisions. Do not assume that `--overwrite` merges directories safely.
5. Upload to the intended parent directory with `quark put <local-path> <remote-directory>`.
6. Use `--continue` only when the matching `.quark.task` state exists from an interrupted transfer. Preserve task state until verification finishes.
7. Verify remote paths, file counts, sizes, and—where available—hashes or archive integrity. Retry transient failures at low concurrency.
8. Delete local source data only when the user explicitly authorized deletion and verification has succeeded. Resolve the exact target first and report what was removed.

## Safety Rules

- Never display, log, commit, or upload a Quark Cookie.
- Prefer `--json`, `--quiet`, and `--no-progress` in scripts.
- Treat `rm --yes`, local deletion, and overwriting as destructive operations.
- Do not use `--continue` as a generic retry switch; it expects an existing task file.
- Do not claim success from the upload command alone. Compare the completed remote inventory with the local manifest.
- The tool uses unofficial web interfaces and can be affected by Cookie expiry, Quark service policies, and transient API errors.

## Usage Examples

“请用夸克网盘命令行查看远端目录，把 NAS 备份目录断点续传到指定位置，核对数量和大小后再清理本地文件。”
