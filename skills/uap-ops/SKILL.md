---
name: uap-ops
description: UAP（统一授权平台）运维技能：菜单/功能点登记、用户角色绑定、角色权限赋权。不经 @ane/uap-mcp npm 包，用零依赖 Node 脚本经 AgentForge MCP Gateway（Streamable HTTP + JSON-RPC）直连 UAP 白名单接口。用于：页面交付后在 UAP 建菜单、登记功能点、给角色赋权、给用户绑角色、查应用 appId、按名/路由/resCode 找资源。当用户提到「对接 UAP」「UAP 登记」「登记菜单」「功能点」「赋权」「角色权限」「天象 appId」时使用。读命令即查即用；写命令必须先展示拟变更并取得用户当前消息确认后才加 --yes 执行。
---

# UAP Ops

本技能负责公司 UAP（统一授权平台：菜单、功能点、赋权）的登记与赋权操作。它替代 `npx @ane/uap-mcp`（依赖内网 Nexus 的 stdio MCP 壳），直接以零依赖 Node 脚本（仅 Node 内建模块，Node 18+）经网关调 UAP 白名单接口，命令与原 11 个 MCP 工具语义一致。

## 首次使用（配置网关）

网关地址与 appKey 属内网凭据，不随仓库分发。二选一配置：

1. 环境变量 `UAP_GATEWAY_URL` + `UAP_GATEWAY_APP_KEY`（二者须同时提供）；
2. 复制 `scripts/uap-gateway.local.json.example` 为同目录 `uap-gateway.local.json`（已被 gitignore）。example 里已预填网关端点与 appKey（与 @ane/uap-mcp 源码同源的内网共享值），复制即用；若失效则取值来源：`@ane/uap-mcp` 源码 `dist/infra/uap-config.js`（`UAP_GATEWAY` 常量），或找网关平台组。配置细节与排障见 `references/uap-gateway-protocol.md`。

配置好后先跑连通性自检：

```bash
node scripts/uap.mjs ping
```

## 何时使用

- 页面交付后的 UAP 登记：建菜单、登记功能点（`create-menu` / `create-function`）。
- 赋权：给用户绑角色（`assign-user-roles`）、给角色增删菜单/功能点权限（`preview-role-permissions` → `update-role-permissions`）。
- 查询定位：应用中文名→appId、按名/路由/resCode 找资源、查用户已绑角色。

## 安全边界

- 所有写命令（create-* / update-* / assign-user-roles / update-role-permissions）必须先向用户展示拟变更并取得**当前消息**确认，才允许加 `--yes` 执行；缺 `--yes` 时脚本自身拒绝执行。
- 资源整树、角色权限整树、应用全量、全量角色列表不得贴进对话；脚本只回小结果与候选/相似项。
- 网关地址与 appKey 不入库：走环境变量或 gitignored 的 `scripts/uap-gateway.local.json`。
- 本技能只做 UAP 平台操作，不承担 git 提交、发布部署等交付动作。

## 使用方式

在 `skills/uap-ops/` 目录下执行（脚本按自身所在目录解析配置与快照，不依赖 cwd）：

```bash
node scripts/uap.mjs ping                                   # 连通性自检
node scripts/uap.mjs app-info --uap-name 天象                # 应用中文名 → appId（本地快照）
node scripts/uap.mjs find-resource --app-id max --res-name 页面名 --parent-res-name 目录名
node scripts/uap.mjs preview-role-permissions --json '{…}'    # 赋权先预览
node scripts/uap.mjs update-role-permissions --json '{…}' --yes
```

完整命令表、字段语义、典型流程与铁律见：

- `references/uap-tool-recipes.md`（命令 ↔ 字段 ↔ 铁律速查）
- `references/uap-gateway-protocol.md`（网关协议、配置、排障）

## References

- `references/uap-tool-recipes.md`
- `references/uap-gateway-protocol.md`
- `scripts/uap.mjs`
- `scripts/data/application-all.json`

## 输出

- command / argsEcho
- result（脚本 stdout JSON：matched/created/preview/saved 等）
- writeConfirmed（写命令是否经用户当前消息确认）
- blockedReasons（配置缺失、网关不可达、用户未确认、入参校验失败等）
