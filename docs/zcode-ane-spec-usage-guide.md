# zcode 与 ane-spec 集成使用指南

## 文档契约

本文档面向第一次接入 zcode 与 ane-spec 的前端开发者，也适合项目维护者、代码评审者和团队负责人检查项目是否已经完成 AI + spec 工作流落地。

本文档根据内部 KDocs 资料《前端ai落地 zcode 与 ane-spec 集成》整理。为避免把私有仓库地址、内网 IP、本机路径或个人信息写入可复用仓库，示例命令使用占位符。内部分发时请由维护者将占位符替换为真实地址。

| 占位符 | 含义 |
|---|---|
| `<project-root>` | 需要接入 ane-spec 的前端项目根目录 |
| `<ane-spec-ssh-url>` | ane-spec 仓库 SSH 地址 |
| `<ane-spec-http-url>` | ane-spec 仓库 HTTP 地址 |
| `<internal-approval-channel>` | 内部 Git 仓库权限申请入口 |

### 验收标准

- Given 开发者已获得 ane-spec 仓库权限，When 在项目根目录执行脚手架安装，Then 项目应生成 `.zcode/`、`openspec/`、规则文档和必要的项目说明文件。
- Given ZCode 已重启并打开项目根目录，When 在对话框输入 `/spsx:next`，Then 能进入 super-spec 下一步工作流。
- Given 项目已有一个 OpenSpec 变更，When 执行 verify 或 sync 类命令，Then 能看到结构、漂移、验收覆盖、任务完成度等质量门结果。
- Given 文档面向公开或跨团队分发，When 出现私有地址、内网 IP、本机路径或个人账号，Then 文档应使用占位符替代。

## 核心概念

| 名称 | 作用 |
|---|---|
| zcode | 团队使用的 AI 编程编辑器或命令运行环境，负责加载插件、命令和项目级规则。 |
| ane-spec | 团队沉淀的前端 spec 脚手架，向项目写入 ZCode 命令、OpenSpec 目录、规则文档和质量门。 |
| OpenSpec | 以需求、设计、任务、规格和验证为中心的变更管理目录，用来把 AI 编程过程变成可追踪的工程流程。 |
| superpowers | zcode 插件能力包，提供 brainstorm、plan、apply 等强化工作流能力。 |
| `/spsx:*` | super-spec 快捷命令族，用于推进下一步、评估当前状态等高层流程。 |
| `/opsx:*` | OpenSpec 操作命令族，用于探索、新建、应用、验证、同步、归档或继续变更。 |

## 权限和前置条件

在安装前确认以下事项。

| 项目 | 要求 | 验证方式 |
|---|---|---|
| Git 权限 | 已获得 ane-spec 仓库访问权限 | 到 `<internal-approval-channel>` 申请并确认可 clone |
| Node.js | 建议 Node.js 22+ | `node -v` |
| OpenSpec CLI | 已安装并可执行 | `openspec --version` |
| uvx | 已安装并可执行 | `uvx --version` |
| jq | 已安装并可执行 | `jq --version` |
| ZCode | 能打开目标项目根目录 | 在 ZCode 中打开 `<project-root>` |

安装命令必须在目标项目根目录执行。先进入项目根目录：

```bash
cd <project-root>
```

## 安装方式

### 方式一：远程拉取脚手架并执行

适合 SSH 权限和网络都已经准备好的场景。

```bash
git archive --remote=<ane-spec-ssh-url> frontend scaffold.sh | tar -xO scaffold.sh | bash -s -- --branch frontend .
```

说明：

- `frontend` 是 ane-spec 的前端分支。
- 命令只从远端取出 `scaffold.sh` 并在当前项目执行。
- 最后的 `.` 表示安装到当前项目根目录。

### 方式二：先 clone 仓库再执行脚本

适合远程 archive 不可用，或需要先检查脚本内容的场景。

```bash
git clone <ane-spec-http-url> /tmp/ane-spec
bash /tmp/ane-spec/scaffold.sh --branch frontend -d ./
```

说明：

- `/tmp/ane-spec` 只是临时目录，不应提交到业务项目。
- `-d ./` 表示把脚手架内容安装到当前目录。
- 如需复用临时目录，先确认它来自最新的 `frontend` 分支。

## 安装后会生成什么

脚手架安装完成后，项目通常会得到以下内容。实际结果以安装日志为准。

| 路径或文件 | 用途 |
|---|---|
| `.mcp.json` | MCP 相关配置，通常应按项目安全策略处理，不建议直接提交敏感配置。 |
| `.zcode/settings.local.json` | ZCode 本地设置。 |
| `.zcode/commands/spsx/next.md` | 进入 super-spec 下一步流程。 |
| `.zcode/commands/spsx/eval.md` | 评估当前 spec 或执行状态。 |
| `.zcode/commands/opsx/explore.md` | 探索需求、代码和上下文。 |
| `.zcode/commands/opsx/new.md` | 新建 OpenSpec 变更。 |
| `.zcode/commands/opsx/propose.md` | 生成或完善 proposal。 |
| `.zcode/commands/opsx/apply.md` | 应用变更。 |
| `.zcode/commands/opsx/verify.md` | 执行验证。 |
| `.zcode/commands/opsx/sync.md` | 同步 spec 与实现状态。 |
| `.zcode/commands/opsx/archive.md` | 归档已完成变更。 |
| `.zcode/commands/opsx/bulk-archive.md` | 批量归档变更。 |
| `.zcode/commands/opsx/continue.md` | 继续已有变更。 |
| `.zcode/commands/opsx/onboard.md` | 项目或 spec 工作流上手引导。 |
| `.zcode/commands/opsx/ff.md` | 快速推进或 fast-forward 类流程，按团队命令说明使用。 |
| `.zcode/skills/openspec-*.md` | OpenSpec 相关技能说明。 |
| `.zcode/skills/sdd-requirement-doc/SKILL.md` | SDD 或需求文档相关技能。 |
| `openspec/config.yaml` | OpenSpec 配置。 |
| `openspec/changes/` | 当前或未来变更的工作区。 |
| `openspec/schemas/super-spec/` | super-spec schema、模板和验证门。 |
| `docs/business/` | 业务词汇、业务上下文等文档。 |
| `docs/arch/` | 架构地图、外部依赖等文档。 |
| `rules/` | 前端编码、组件、埋点、文档维护等项目规则。 |
| `AGENTS.md` | Agent 在本项目内工作的规则入口。 |

如果项目已有 `README.md`，脚手架可能会跳过覆盖。这是正常行为，避免覆盖项目已有说明。

## 第一次启动

安装完成后，必须重启 ZCode 一次，确保 superpowers 插件和新写入的命令被加载。

1. 关闭并重新打开 ZCode。
2. 在 ZCode 中打开 `<project-root>`，不要只打开子目录。
3. 打开对话框，输入：

```text
/spsx:next
```

如果命令可用，说明 ZCode 已识别 `.zcode/commands` 和相关插件能力。若提示命令不存在，先看本文 FAQ。

## OpenSpec / spec 工作流

ane-spec 的关键价值不是只安装几个文件，而是把 AI 编程变更纳入 spec 生命周期。推荐把每个中大型需求都当成一个 OpenSpec change 来推进。

### 变更生命周期

```text
探索上下文
  -> 新建变更
  -> 编写 proposal / requirements
  -> 编写 design
  -> 拆解 tasks
  -> 实施 apply
  -> verify 质量门
  -> sync 同步文档和实现
  -> archive 归档完成变更
```

### spec 产物关系

| 产物 | 作用 | 质量要求 |
|---|---|---|
| `proposal.md` | 描述为什么要做、做什么、不做什么 | 范围清晰，有非目标 |
| `requirements.md` | 写用户故事和验收标准 | 验收条件可测试，推荐 EARS 或 Given-When-Then |
| `design.md` | 描述技术方案、边界、数据、风险 | 能指导实现和评审 |
| `tasks.md` | 拆成可执行任务 | 每项可检查，能回链到需求 |
| `spec.md` | 记录最终规格或变更后的能力说明 | 与实现保持一致 |
| `verify.md` | 记录验证方式和结果 | 区分通过、失败、跳过和环境阻塞 |
| `retrospective.md` | 复盘变更结果和后续动作 | 记录经验和遗留问题 |

### 命令速查

| 命令 | 使用时机 | 产出或效果 |
|---|---|---|
| `/spsx:next` | 不确定下一步做什么时 | 根据当前状态给出下一步建议 |
| `/spsx:eval` | 想评估当前 spec 或执行状态时 | 输出状态、风险和质量建议 |
| `/opsx:explore` | 需求或代码上下文不清时 | 收集背景、影响范围和证据 |
| `/opsx:new` | 开始一个新变更时 | 创建 change 工作区和基础文件 |
| `/opsx:propose` | 需要写 proposal 或需求草案时 | 生成或完善 proposal / requirements |
| `/opsx:apply` | spec 已准备好，需要进入实现时 | 按计划应用变更 |
| `/opsx:verify` | 实现后或归档前 | 运行验证门并输出结果 |
| `/opsx:sync` | 实现和 spec 可能不一致时 | 同步文档、任务和实现状态 |
| `/opsx:archive` | 单个变更完成并验证后 | 归档 change |
| `/opsx:bulk-archive` | 多个变更需要批量归档时 | 批量归档完成项 |
| `/opsx:continue` | 接续一个已有变更时 | 恢复上下文并继续推进 |
| `/opsx:onboard` | 新成员或新项目初始化时 | 生成上手说明和项目上下文 |
| `/opsx:ff` | 需要快速推进当前流程时 | 按团队定义执行快速推进 |

### 质量门

`openspec/schemas/super-spec/gates/` 中的验证脚本用于防止 spec 和实现脱节。常见质量门如下。

| 质量门 | 检查重点 |
|---|---|
| `structure` | OpenSpec 文件结构是否完整 |
| `arch-map-freshness` | 架构地图是否过期 |
| `drift-check` | 文档与实现是否漂移 |
| `spec-sync` | spec 是否同步到最新状态 |
| `ac-coverage` | 验收标准是否覆盖关键行为 |
| `backend-coding` | 后端或接口相关规范是否满足 |
| `tasks-completion` | tasks 是否全部完成或明确延期 |
| `design-spec-consistency` | design 与 spec 是否一致 |
| `impl-signal` | 是否有足够实现证据 |
| `spec-lock` | spec 是否处于可变更或锁定状态 |
| `deferred-equiv` | 延期项是否有等价说明 |

归档前至少应完成结构、同步、验收覆盖、任务完成度和实现证据检查。无法执行的质量门要标注为环境阻塞，不要写成已通过。

## 推荐日常流程

### 新需求

1. 运行 `/opsx:explore` 收集背景。
2. 运行 `/opsx:new` 创建变更。
3. 运行 `/opsx:propose` 生成 proposal 和 requirements。
4. 补齐 `design.md` 和 `tasks.md`。
5. 确认验收标准后运行 `/opsx:apply`。
6. 实现完成后运行 `/opsx:verify`。
7. 根据结果运行 `/opsx:sync`。
8. 确认无阻塞后运行 `/opsx:archive`。

### 接手已有变更

1. 运行 `/opsx:continue`。
2. 查看当前 change 的 requirements、design、tasks 和 verify。
3. 用 `/spsx:eval` 判断缺口。
4. 补齐缺失文档或验证证据。
5. 继续 apply、verify、sync 或 archive。

### 新成员上手

1. 阅读 `AGENTS.md`、`docs/business/` 和 `docs/arch/`。
2. 在 ZCode 中打开项目根目录。
3. 运行 `/opsx:onboard`。
4. 用 `/spsx:next` 查看下一步建议。
5. 从一个低风险 change 开始练习完整流程。

## 验证检查表

### 安装验证

- [ ] 已在 `<project-root>` 执行安装命令。
- [ ] `node -v` 显示 Node.js 22+。
- [ ] `openspec --version` 可执行。
- [ ] `uvx --version` 可执行。
- [ ] `jq --version` 可执行。
- [ ] `.zcode/commands/spsx/next.md` 存在。
- [ ] `.zcode/commands/opsx/verify.md` 存在。
- [ ] `openspec/config.yaml` 存在。
- [ ] `openspec/schemas/super-spec/gates/` 存在。
- [ ] ZCode 已重启。
- [ ] `/spsx:next` 能被识别。

### 文档验证

- [ ] 文档说明了权限申请和前置依赖。
- [ ] 文档明确要求在项目根目录安装。
- [ ] 文档区分了远程执行和本地 clone 两种安装方式。
- [ ] 文档列出了安装后生成的关键目录和文件。
- [ ] 文档解释了 OpenSpec/spec 生命周期。
- [ ] 文档解释了 `/spsx:*` 和 `/opsx:*` 命令族。
- [ ] 文档列出了质量门和归档前检查。
- [ ] 文档没有泄露本机路径、个人账号、私有仓库地址、内网 IP、token 或密码。

## FAQ 与故障排查

### 没有 ane-spec 仓库权限

现象：`git archive` 或 `git clone` 失败，提示无权限、仓库不存在或认证失败。

处理：

1. 到 `<internal-approval-channel>` 申请 ane-spec 仓库权限。
2. 确认 SSH key 或 HTTP 凭据可用。
3. 重新执行安装命令。

### Node.js 版本过低

现象：脚手架检查前置依赖失败，或插件运行时报 Node.js 能力缺失。

处理：

```bash
node -v
```

若低于 22，请按团队 Node 版本管理方式切换到 Node.js 22+ 后重试。

### OpenSpec CLI、uvx 或 jq 不存在

现象：安装阶段提示 `OpenSpec CLI`、`uvx` 或 `jq` 缺失。

处理：

1. 按团队标准安装缺失工具。
2. 重新打开终端，确认命令在 `PATH` 中。
3. 重新执行脚手架。

### `/spsx:next` 不可用

现象：ZCode 对话框提示命令不存在或无法加载。

处理：

1. 确认项目根目录存在 `.zcode/commands/spsx/next.md`。
2. 确认 ZCode 打开的是项目根目录，而不是子目录。
3. 重启 ZCode。
4. 确认 superpowers 插件已安装并启用。

### superpowers 技能不可调用

现象：full mode 的 brainstorm、plan、apply 等能力不可用。

处理：

1. 重启 ZCode。
2. 确认插件缓存和 marketplace 注册成功。
3. 重新打开项目根目录。
4. 再次输入 `/spsx:next`。

### 安装日志显示 README.md 被跳过

这是正常行为。脚手架默认不覆盖已有 `README.md`，避免破坏项目原有说明。需要合并说明时，手工把新说明整理进现有 README 或项目 docs。

### `.mcp.json` 是否应该提交

按项目安全策略决定。若 `.mcp.json` 包含本机路径、私有服务、凭据或 token，不应直接提交。可以提交脱敏模板，或将真实配置加入本机忽略规则。

### 公开文档里能不能放真实仓库地址

不建议。公开或跨团队文档使用 `<ane-spec-ssh-url>`、`<ane-spec-http-url>` 等占位符；仅在受控的内部分发文档中保留真实地址。

## 维护建议

1. ane-spec 脚手架升级后，同步更新本文档的生成文件清单和命令说明。
2. OpenSpec schema 或 gates 变化后，同步更新质量门章节。
3. ZCode 命令命名变化后，同步更新命令速查表。
4. 每次项目归档一个典型 change 后，把经验沉淀到 FAQ 或 `docs/arch/`。
5. 新成员首次使用时记录卡点，定期反向更新快速开始章节。

## 修订记录

| 版本 | 日期 | 说明 |
|---|---|---|
| 0.1 | 2026-07-16 | 根据 KDocs 来源整理首版使用指南，补齐 spec/OpenSpec 工作流、命令速查和验证清单。 |

## 待确认问题

1. `<ane-spec-ssh-url>` 和 `<ane-spec-http-url>` 是否需要在内部分发版中替换为真实地址。
2. `/opsx:ff` 的团队定义是否需要补充更精确的使用说明。
3. `.mcp.json` 在目标团队中是提交模板、提交真实配置，还是始终本地忽略。
4. OpenSpec CLI 的团队标准安装方式是否需要补充到前置条件章节。
