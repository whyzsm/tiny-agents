# UAP 工具配方（命令 ↔ 字段 ↔ 铁律）

`scripts/uap.mjs` 的命令与原 @ane/uap-mcp 的 11 个 MCP 工具一一对应，业务语义（查树、合并、祖先勾选重算、无变化不写）已原样移植。本文件是命令用法与安全铁律的速查。

通用调用形态（在 `skills/uap-ops/` 目录下执行；脚本按自身目录解析配置与快照）：

```bash
node scripts/uap.mjs <command> [--flag value …] [--json '<JSON 对象>'] [--yes]
```

- 扁平字段用 kebab-case 旗标（`--app-id max`、`--uap-name 天象`、`--res-name 名`）；数组与嵌套对象（`function`、`add`、`remove`、`addRoleNames` 等）必须走 `--json`，`--json` 值优先于旗标。
- 入参 strict 校验：未知字段直接报错并列出允许字段；这与原包 zod `.strict()` 一致，防拼错字段名静默丢参。
- 输出恒为单个 JSON 对象；失败 exit 1 且 `{ error: true, message, payload? }`，`payload` 常带候选/相似项供向用户澄清。

## 典型流程（新增页面登记 UAP）

```bash
# 1. 应用中文名 → appId（读本地快照，不打网关）
node uap.mjs app-info --uap-name 天象            # → { matched: true, appId: "max", … }

# 2. 查目标父目录下是否已有同名菜单（必须带 parent-res-name，只回直接子级）
node uap.mjs find-resource --app-id max --res-name 页面名 --parent-res-name 目录名

# 3. 目录不存在 → similarParents 交给用户确认；确认目录存在且 existsUnderParent=false → 创建菜单
node uap.mjs create-menu --json '{"appId":"max","resName":"页面名","resUrl":"/txmax/pageName","single":0,"parentResId":"<目录id>"}' --yes

# 4. 页面菜单登记功能点（resType 必须显式传 "5"，见下方已知坑；按钮权限走 function.actions）
node uap.mjs create-function --json '{"appId":"max","parentResId":"<页面菜单id>","resName":"页面名","resCode":"/xxx/selectPage","resType":"5","buttonUrls":"/btn/a,/btn/b","function":{"actions":[{"code":"/btn/a","desc":"新增"}]}}' --yes

# 5. 给角色赋权：先预览（读）再执行（写）
node uap.mjs preview-role-permissions --json '{"appId":"max","roleName":"运营","add":[{"resName":"页面名","resType":"1","parentResId":"<目录id>"}]}'
node uap.mjs update-role-permissions --json '{…同上…}' --yes
```

## 命令明细

| 命令 | 写 | 必填 | 常用可选 | 说明 |
| --- | --- | --- | --- | --- |
| `ping` | 否 | — | — | 连通性自检（见协议文档） |
| `app-info` | 否 | `uapName` | — | 应用中文名→appId；读 `scripts/data/application-all.json` 快照 |
| `find-resource` | 否 | `appId` +（`id`/`resName`/`resUrl`/`resCode` 至少其一） | `resType`（1 菜单/5 功能点/4 旧按钮）、`parentResId`、`parentResName` | 指定父目录时只回直接子级；查功能点/按钮须带 `resType` 4/5 + 页面菜单 `parentResId` |
| `create-menu` | **是** | `appId`、`resName`、`resUrl`、`single`(0/1) | `parentResId`（根级省略）、`order`（省略=同级最大+1）、`status`、`visible`、`domain`、`resDesc` 等 | 同级同名去重；回 `created.id` |
| `create-function` | **是** | `appId`、`parentResId`(页面菜单 id)、`resName`、`resCode`、`buttonUrls`、`function` | `interfaceUrls`、`status` | 只建功能列表 resType=5，禁止建按钮列表；回 `created`（id/resCode/parentResId） |
| `update-menu` | **是** | `id`、`appId` | 其余全部可选，只传要改的字段 | server 从现有记录合并成全量后写回；回 `mergedFields` |
| `update-function` | **是** | `id`、`appId`、`parentResId` | `resName`、`resCode`、`buttonUrls`、`function` 等 | 同上 |
| `update-button` | **是** | `id`、`appId`、`parentResId` | `resName`、`resCode`、`status` | 仅存量旧按钮权限（resType=4）；禁止新建 |
| `get-user-roles` | 否 | `appId` | `uId`（默认 12436，测试环境仅授权 admin）、`roleName` | 只回 selectedRoles/adminRoleExists/roleCount，不回全量角色列表 |
| `assign-user-roles` | **是** | `appId` + 四个增删数组至少其一 | `uId` | 先查再合并后保存，禁止直接传全量 roleIds；无变化不写 |
| `preview-role-permissions` | 否 | `appId` +（`roleId` 或 `roleName`）+（`add` 或 `remove` 至少其一） | `uId` | 只读预览：added/removed/unchangedCount/checkedCount/halfCheckedCount |
| `update-role-permissions` | **是** | 同 preview | 同 preview | 重新拉树、合并、重算祖先后全量保存；无变化不写 |
| `call <tool>` | 视工具 | 网关工具名 | `--json` args | 原始 tools/call 逃生口（排障用，无安全编排） |

字段语义要点：

- `resUrl` 必须与前端路由 path 一致；未指定时可按「父级 resUrl + / + 英文名」拼装。
- `resCode` 是主接口码（如 `/xxx/selectPage`，去掉 `/api` 前缀）。
- `buttonUrls` 与 `function.actions` 的 code 列表必须成对一致；`interfaceUrls` 与 `function.interfaces` 同理。
- `function.actions`/`interfaces` 传 `null` 表示「编辑时不改该子字段」。

## 铁律（与原 MCP 工具描述一致，违反即返工）

1. **写前确认**：所有写命令必须先向用户展示拟变更（update-role-permissions 先跑 preview；create/update 回读参数与目标父目录），取得当前消息确认后才加 `--yes` 执行。
2. **禁止拉整树进对话**：`find-resource` 必须带定位字段；资源树/角色权限树/应用全量只在脚本进程内消化，工具只回小结果（≤20 条命中 + 截断标记）。同理 `get-user-roles` 不回全量角色名。
3. **父目录语义**：用户说「在某目录下创建」时，find 必须一次带 `parentResName + resName`；`existsUnderParent=false` 就必须在该目录 create-menu，禁止改用其它位置的同名项；父目录未命中把 `similarParents` 列给用户确认，禁止擅自挑第一条、禁止把该名称理解成「去 UAP 里配置」。
4. **功能点 parentResId 传页面菜单 id**：权限树分组节点 `{菜单id}function` / `{菜单id}button` 由脚本内部映射，禁止 Agent 自拼分组 id。
5. **无实际变化不写**：assign/update-role-permissions 无变化时直接回 `unchanged: true`，不调写接口。
6. **写接口是全量覆盖**：update-* 的完整字段由脚本从现有记录合并生成，Agent 只传 id + 变更字段，禁止手工拼全量。
7. **新建资源优先复用 `created.id`**：创建返回的 id 是后续 find/赋权的最可靠锚点。

## 已知坑（服务端实测行为，2026-08）

1. **create-function 必须显式传 `"resType":"5"`**：CLI spec 里该字段无默认值（只有枚举校验），透传缺失时下游 500 / 网关 502。
2. **update-function 的合并字段清单不含 `visible`**：编辑功能点会把 visible 重置为 0（功能点 visible 系全 0，属既有约定，无实际影响）。
3. **`buttonUrls` / `interfaceUrls` 独立字段服务端不持久化**（读回恒 null）：权限实际只认 `function` JSON 的 `actions` / `interfaces`，所以两者必须成对一致。
4. **roleId 须传字符串**：`update-role-permissions` 等命令里 roleId 传数字会被拒。

## 与项目规则的衔接

- 目标项目（如 dcm）`.ane/rules-config.yaml` 的 `uapName`（如「天象」）对应 `app-info --uap-name`；赋权范围与页面权限码以项目 `rules/common/frontend-auth.md` 为准。
- UAP 功能点登记约定（参照分拨周转箱流向配置 620052）：每功能点一个动作，resCode 用 add/import/delete/edit/view/export；接口 code 去 /api 前缀（如 /centerBoxTask/selectPage）；查询类功能点无 actions 只有 interfaces。
- 应用快照过期时（app-info 找不到新应用）：从 UAP 管理台「应用管理」接口完整返回更新 `scripts/data/application-all.json`（网关 application_all 实测返回空 data，不能用来刷新）。
