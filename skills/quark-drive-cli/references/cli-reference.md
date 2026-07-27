# 夸克网盘 CLI 使用手册

本文对应开源项目 [`i-sync/quark-cli`](https://github.com/i-sync/quark-cli)，本机核对版本为 `quark 0.4.2`。Cargo 包名是 `quarkcli`，安装后的可执行命令是 `quark`。该工具依赖夸克网页端接口，不是夸克官方客户端。

## 1. 安装

优先从项目的 [GitHub Releases](https://github.com/i-sync/quark-cli/releases) 下载当前平台的二进制文件。也可以从源码安装：

```bash
cargo install --git https://github.com/i-sync/quark-cli quarkcli
quark --version
quark --help
```

## 2. 登录与凭据安全

`quark` 使用浏览器 Cookie 代表账号访问网盘。Cookie 等同密码，不要发送给他人、提交到 Git、写入公开脚本或打印到日志。

推荐从标准输入保存：

```bash
quark auth set-cookie --from-stdin
# 粘贴 Cookie 后按 Ctrl+D
quark auth show-source
```

也可以导入权限受限的文件：

```bash
chmod 600 ./cookie.txt
quark auth import-cookie --from-file ./cookie.txt
```

临时调用可使用 `QUARK_COOKIE` 或全局参数 `--cookie-file`，但应避免 shell 历史和进程列表泄漏凭据。

## 3. 浏览与查询

```bash
quark ls /
quark ls /备份 --long
quark ls /备份 --json
quark stat /备份/archive.tar.zst --json
```

`ls` 只列当前层；递归盘点时应逐层读取目录，保存每个相对路径、类型和大小，再汇总文件数量与总字节数。

## 4. 创建、移动与删除

```bash
quark mkdir /备份/NAS
quark mv /备份/old.bin new.bin
quark mv /备份/old.bin /归档/new.bin
quark rm /备份/old.bin            # 交互确认
quark rm /备份/old.bin --yes      # 非交互，谨慎使用
```

删除前先用 `stat --json` 再次解析精确目标。不要对未解析的变量、通配符、根目录或宽泛目录执行删除。

## 5. 上传

将单个文件或整个目录上传到远端父目录：

```bash
quark put ./backup.tar.zst /备份/
quark put ./photos /备份/NAS/
```

适合脚本的写法：

```bash
quark put ./backup.tar.zst /备份/ --quiet --no-progress
```

覆盖同名目标必须明确指定：

```bash
quark put ./backup.tar.zst /备份/ --overwrite
```

`--overwrite` 不是通用的目录合并策略。上传目录前先比较远端同名路径；若双方都有内容，逐项确认冲突或上传到临时目录后再校验、移动。

### 断点续传

上传中断后保留工具生成的 `.quark.task` 文件，再对同一源路径和同一目标运行：

```bash
quark put ./backup.tar.zst /备份/ --continue --quiet --no-progress
```

不要在没有对应任务文件时随意加 `--continue`，否则会出现 `upload task file not found`。完成校验之前不要删除任务文件。

已知 FID 时也可使用底层形式：

```bash
quark upload --file ./file.bin --pdir-fid 0
quark upload-dir --dir ./photos --pdir-fid 0
```

## 6. 下载

```bash
quark get /备份/archive.tar.zst ./archive.tar.zst
quark get /备份/NAS ./NAS --continue --retry auto
```

下载会使用 `.part` 和 `.quark.task` 保存恢复状态。网络不稳定时：

```bash
quark get /备份/big.bin ./big.bin \
  --continue --retry infinite --retry-delay 2 --retry-max-delay 60
```

默认 `--verify auto` 在服务端 MD5 与实际内容不一致时告警但继续；`--verify always` 强制把不一致视为错误；只有另有可靠校验手段时才考虑 `--no-verify`。

## 7. 安全迁移与验证流程

1. 生成本地清单：记录相对路径、文件大小、总文件数、总字节数；重要压缩包另做校验和或运行完整性测试。
2. 用 `quark ls ... --json` 生成远端清单，识别同名文件和目录。
3. 先建目标目录；冲突不明确时上传到带日期的暂存目录。
4. 上传大文件时保留 `.quark.task`；遇到短暂 API 错误应退避重试，批量任务并发建议保持在 2–4。
5. 上传结束后再次递归盘点远端，逐项比较相对路径和大小，并核对总文件数、总字节数。
6. 对压缩包执行可用的完整性测试；对关键文件比较可获得的哈希。
7. 发现自动重试产生的 `(1)` 等重复项时，只删除已确认与目标重复的远端文件。
8. 只有全部验证通过且用户明确授权时，才删除本地源目录；删除后检查磁盘空间并报告结果。

## 8. 自动化模板

```bash
set -euo pipefail

local_source='/absolute/path/to/backup.tar.zst'
remote_parent='/备份/NAS'

test -f "$local_source"
quark stat "$remote_parent" --json >/dev/null
quark put "$local_source" "$remote_parent" --quiet --no-progress
quark stat "$remote_parent/backup.tar.zst" --json
```

脚本只把普通数据写到 stdout；调试和进度信息放在 stderr。需要诊断时使用全局 `--debug`，但不要把包含敏感下载 URL 或 Cookie 的日志公开。

## 9. 常见问题

- `401`、登录失效：重新获取 Cookie，并用 `auth set-cookie --from-stdin` 更新。
- `upload task file not found`：去掉 `--continue` 开始新任务，或恢复原任务文件。
- 同名文件出现 `(1)`：先比较大小和内容，确认重复后再删除；不要盲目批量清理。
- 上传命令成功但不确定完整：成功退出不等于迁移验证完成，必须复查远端清单。
- 大文件受限或失败：这可能来自夸克服务端策略，CLI 无法绕过所有限制。

上游说明与最新发行版以项目仓库为准：<https://github.com/i-sync/quark-cli>。

