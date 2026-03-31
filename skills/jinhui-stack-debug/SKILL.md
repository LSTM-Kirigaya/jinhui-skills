---
name: jinhui-stack-debug
description: 网站和小程序调试的依赖关系排查指南。当调试陷入僵局时，Use this skill to systematically identify which dependency layer is causing the issue: (1) Data dependencies - verify backend before debugging frontend, (2) Environment differences - local vs production issues, (3) Version compatibility - library/framework mismatches, (4) Configuration errors - missing or incorrect configs, (5) State management - component/app state problems, (6) Network layer - CORS, timeouts, connectivity, (7) Permission/authorization - auth and access control, (8) Caching issues - stale code or data, (9) Build process - compilation and bundling problems, (10) Runtime environment - browser/platform differences.
---

# Jinhui Stack Debug

> **Copyright © 锦恢 [kirigaya.cn](https://kirigaya.cn)**

网站和小程序调试的**依赖关系排查指南**。当调试陷入僵局时，按照此指南逐层排查，避免在低层级问题上浪费时间。

> **核心理念**：很多问题表象在前端，根源在依赖层。先验证依赖，再调试本体。

---

## 依赖类型目录

| 类型 | 路径 | 描述 |
|-----|------|-----|
| 数据依赖型 | [./data/DATA.md](./data/DATA.md) | 前端表现依赖于后端数据的正确性。页面显示异常时，先验证接口返回，再排查前端渲染。 |
| 环境依赖型 | [./environment/ENVIRONMENT.md](./environment/ENVIRONMENT.md) | 不同运行环境导致行为差异。本地正常但线上异常时，检查环境变量、域名、协议等差异。 |
| 版本依赖型 | [./version/VERSION.md](./version/VERSION.md) | 依赖库/框架版本不兼容。升级后功能异常时，检查版本变更和 breaking changes。 |
| 配置依赖型 | [./config/CONFIG.md](./config/CONFIG.md) | 配置文件错误或遗漏。白名单、API密钥、路由配置等问题。 |
| 状态依赖型 | [./state/STATE.md](./state/STATE.md) | 组件/应用状态管理问题。刷新后正常、切换页面后数据丢失等。 |
| 网络依赖型 | [./network/NETWORK.md](./network/NETWORK.md) | 网络层通信问题。请求超时、跨域报错、404/500 错误等。 |
| 权限依赖型 | [./permission/PERMISSION.md](./permission/PERMISSION.md) | 用户权限或接口权限不足。功能按钮不显示、接口返回 403 等。 |
| 缓存依赖型 | [./cache/CACHE.md](./cache/CACHE.md) | 各类缓存导致代码不生效。改代码后页面无变化、用户看到旧版本等。 |
| 构建依赖型 | [./build/BUILD.md](./build/BUILD.md) | 构建工具或产物问题。代码没生效、sourcemap 不匹配等。 |
| 运行时依赖型 | [./runtime/RUNTIME.md](./runtime/RUNTIME.md) | 浏览器/宿主环境差异。某浏览器正常某浏览器异常、iOS/Android 表现不一致等。 |
