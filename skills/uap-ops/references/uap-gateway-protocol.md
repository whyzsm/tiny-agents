# UAP 网关协议（AgentForge MCP Gateway · Streamable HTTP）

本文件是 uap-ops 技能的底层通信真源：不经 @ane/uap-mcp npm 包、不经 MCP stdio，直接按 JSON-RPC 2.0 over HTTP 调用公司 UAP 白名单接口。`scripts/uap.mjs` 已内置完整实现；本文件供排查、审计或在新环境重实现时使用。

## 调用链路

```
Agent ──node scripts/uap.mjs──► AgentForge MCP Gateway ──► uap-api（白名单工具）
                                   （Streamable HTTP + JSON-RPC 2.0）
```

- 网关本身是一个标准 MCP Streamable HTTP server；一次 CLI 进程内完成「建会话 → 调工具 → 关会话」。
- 旧链路（已废弃）：`npx @ane/uap-mcp`（stdio MCP 壳）内部同样走这个网关。本技能去掉 npm 包层，语义等价。

## 配置

`scripts/uap.mjs` 按以下顺序解析网关地址与 appKey：

1. 环境变量 `UAP_GATEWAY_URL` + `UAP_GATEWAY_APP_KEY`（二者须同时提供）；
2. `scripts/uap-gateway.local.json`：`{ "url": "<网关 mcp 端点绝对地址>", "appKey": "<appKey>" }`（该文件被 gitignore，不入库）。

`scripts/uap-gateway.local.json.example` 已预填可用取值（与 @ane/uap-mcp 源码 `dist/infra/uap-config.js` 的 `UAP_GATEWAY` 常量同源的内网共享值），复制为 `uap-gateway.local.json` 即用；若失效则找网关平台组重新取值。

可选环境变量：`UAP_TIMEOUT_MS`（单请求超时毫秒，默认 30000）、`UAP_APPLICATION_ALL`（应用快照 json 路径覆盖）、`UAP_DEBUG=1`（stderr 打印每个请求/响应摘要，排障用）。

## 三步握手（一次进程内）

所有 POST 都发到网关 URL 本身（无路径追加），公共请求头：

```text
Content-Type: application/json
Accept: application/json, text/event-stream
x-app-key: <appKey>
```

初始化成功后，后续请求还必须携带服务端协商返回的协议版本：

```text
MCP-Protocol-Version: <initialize.result.protocolVersion>
```

### 1. initialize（建会话）

```json
{ "jsonrpc": "2.0", "id": 1, "method": "initialize",
  "params": { "protocolVersion": "2025-06-18", "capabilities": {},
              "clientInfo": { "name": "uap-ops", "version": "1.0.0" } } }
```

- 响应 `200` + `application/json`；**会话 id 在响应头 `mcp-session-id`**（不在 result body，别读错位置）。
- 网关实测接受 `2024-11-05` / `2025-03-26` / `2025-06-18` 并回显请求版本；用 `2025-06-18`（与 MCP SDK 1.30 一致）。

### 2. notifications/initialized（确认会话）

```json
{ "jsonrpc": "2.0", "method": "notifications/initialized" }
```

- 必须带请求头 `Mcp-Session-Id: <上一步拿到的会话 id>`；响应 `202` 无 body。
- 不带会话头会 `400`；后续请求不带会话头会 `500`（实测坑）。

### 3. tools/call（调白名单工具）

```json
{ "jsonrpc": "2.0", "id": 2, "method": "tools/call",
  "params": { "name": "uap-api_tools_uap_resource_tree", "arguments": { "appId": "max" } } }
```

- 响应 `200`，content-type 可能是 `application/json` **或** `text/event-stream`（SSE）。SSE 形态下逐行解析 `data:` 帧（忽略 `event:` / `id:` 行），取 `id` 匹配请求的 JSON-RPC 消息。
- 结果形态：`{ content: [{ type: "text", text: "…" }], isError?: true, structuredContent?: … }`。
- 业务对象解析优先级：`structuredContent` → 拼 text 后 `JSON.parse` → 正则抽末尾 `{…}` 再 parse → `{ raw: 文本 }`（网关常把 JSON 嵌在说明文字末尾）。
- `isError: true` 等价业务失败（按 HTTP 502 语义抛错）。
- 收尾可发 `DELETE` 同 URL + 会话头关会话（best-effort）。

## UAP 文档路径 ↔ 网关工具名映射

| frontend-auth 文档路径 | 网关 tools/call name | 用途 |
| --- | --- | --- |
| `/resource/treeGrid` | `uap-api_tools_uap_resource_tree` | 应用菜单整树 |
| `/resource/getButtonList` | `uap-api_tools_uap_resource_button_list` | 页面菜单下功能点/按钮列表 |
| `/resource/add` | `uap-api_tools_uap_resource_add_menu` | 新增菜单 |
| `/resource/addButton` | `uap-api_tools_uap_resource_add_button` | 新增功能点/按钮 |
| `/resource/edit` | `uap-api_tools_uap_resource_edit` | 编辑资源（全量覆盖） |
| `/role/getUserRoleList` | `uap-api_tools_uap_role_user_roles` | 应用角色列表 + 用户已绑 |
| `/user/saveRole` | `uap-api_tools_uap_user_save_roles` | 用户角色全量保存 |
| `/role/getRoleResourceList` | `uap-api_tools_uap_role_resource_tree` | 角色权限树 + 勾选态 |
| `/role/addRoleRes` | `uap-api_tools_uap_role_save_resources` | 角色资源全量保存 |
| （无文档路径） | `uap-api_tools_uap_application_all` | 全部应用；**经网关返回空 data**（实测），应用名→appId 必须用本地快照 |

入参适配规则（`callUap` 语义）：

- `/role/getUserRoleList` 自动补网关必填 `externalUser=false`。
- `/role/addRoleRes` 的 `checkedKeys` / `halfCheckedKeys` 重复键值对合并为逗号分隔字符串（`checkedKeys=a,b,c`）。
- 数组/重复键 body 按键聚合，多值 `join(",")`；对象 body 只剔除 `undefined`。

## UAP 业务回包语义

`data.code`：`1` 或 `200` 成功；`-11`（或 message 含「非网关」）= 环境禁止非网关直连；`-2`（或 message 含「未登录」）= 需要登录态；其余非 1 值 = 业务失败。写接口回包 `data` 可能为 `null`，新建资源 id 以「写后重查命中」优先、「回包抽 id」兜底。

## 连通性自检

```bash
node scripts/uap.mjs ping
```

输出 `{ ok, gateway, protocolVersion, serverInfo, tools }`；失败按 UAP_DEBUG=1 重跑看逐请求明细。常见故障：500/400 = 会话头丢失（客户端 bug，正常不会出现）；401/403 = appKey 失效；DNS/超时 = 不在内网。

## 原始逃生口

```bash
node scripts/uap.mjs call uap-api_tools_uap_role_user_roles --json '{"appId":"max","uId":"12436","externalUser":false}'
```

`call <gateway-tool> --json '<args>'` 直接透传网关 tools/call，不经过业务编排层；仅用于排障或网关新增工具时的临时调用，不承担去重/合并/勾选重算等安全语义。
