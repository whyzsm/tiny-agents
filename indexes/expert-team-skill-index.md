# Expert-Team Skill Index

本索引登记本仓库自建或适配的专家团路由 Skill、专家团转换 Skill、Skill 工作台和与专家团路由协作的项目质量门禁 Skill。固定专家团入口统一登记在 `expert-team-file-list.md`；本文件可以同时引用需要说明其 Skill 实现的专家团。

普通 skill 查找请先看 `indexes/skill-registry.md` / `indexes/skill-registry.json`；本文件保留专家团路由、转换、Skill 工作台，以及支撑专家团交付的项目质量门禁 Skill。

For ordinary skill lookup, start with `indexes/skill-registry.md` / `indexes/skill-registry.json`; this file keeps expert-team routers, converters, Skill workbenches, and project quality-gate Skills that support expert-team delivery.

| 类型 / Type | Skill | 位置 / Location | 作用 / Purpose | 能力来源 / Source |
|---|---|---|---|---|
| HarmonyOS 专家团路由 Skill / HarmonyOS expert-team router | [`harmony-expert-team`](../skills/harmony-expert-team/SKILL.md) | `skills/harmony-expert-team/` | HarmonyOS/OpenHarmony 项目专家团入口；负责协调问答、实现、UI 生成和服务卡片能力 / Expert-team entry for HarmonyOS/OpenHarmony work; coordinates Q&A, implementation, UI generation, and service-card capabilities | `repo-local/skills/harmony-expert-team` |
| HarmonyOS 上架自检 Skill / HarmonyOS AppGallery release self-check | [`harmonyos-app-store-self-check`](../skills/harmonyos-app-store-self-check/SKILL.md) | `skills/harmonyos-app-store-self-check/` | HarmonyOS 应用发布前质量门禁；检查工程、签名、隐私、权限、发布包和市场素材，支持 AGC 实测读取与基于 AGC 报告的五类自检模拟 / Pre-release quality gate for HarmonyOS apps; checks project structure, signing, privacy, permissions, artifacts, and listing evidence, with AGC live-result reading and report-driven simulation across five AGC dimensions | `repo-local/skills/harmonyos-app-store-self-check` |
| 企业级 React 应用创建 Skill / Enterprise React app creator | [`create-enterprise-react-app`](../skills/create-enterprise-react-app/SKILL.md) | `skills/create-enterprise-react-app/` | 创建并验证生产级企业 React 应用基础架构，覆盖 Vite、React、路由、状态、请求、样式、Storybook、Vitest 和 Playwright 基线 / Scaffold and verify a production-ready enterprise React application baseline covering Vite, React, routing, state, requests, styling, Storybook, Vitest, and Playwright | `repo-local/skills/create-enterprise-react-app` |
| 动态专家团编排 Skill / Dynamic expert-team assembler | [`assemble-project-expert-team`](../skills/assemble-project-expert-team/SKILL.md) | `skills/assemble-project-expert-team/` | 扫描目标项目，读取远端专家团目录，自动生成成员 roster、成员 Prompt、阶段 DAG 和质量门，并按运行时能力协调执行 / Scan the target project, read the remote expert-team catalog, generate the roster, member prompts, phase DAG, and quality gates, then coordinate execution according to runtime capabilities | `https://github.com/whyzsm/tiny-agents/tree/main/indexes` |
| Skill 生成工作台 / Skill generation workbench | [`skill-generation-workbench`](../skills/skill-generation-workbench/SKILL.md) | `skills/skill-generation-workbench/` | 设计、生成、转换、升级和验证 Codex Skill 包，产出 `SKILL.md`、`agents/openai.yaml`、引用文件和脚本 / Design, generate, convert, upgrade, and validate Codex Skill packages; produce `SKILL.md`, `agents/openai.yaml`, references, and scripts | `repo-local/skills/skill-generation-workbench` |
| Skill 拆解与写作工作台 / Skill breakdown and writing coach | [`skill-breakdown-workbench`](../skills/skill-breakdown-workbench/SKILL.md) | `skills/skill-breakdown-workbench/` | 分析 Skill/Agent 的写法，并输出中英双语教学、模板和改写建议 / Analyze Skill and agent writing, then produce bilingual teaching notes, templates, and rewrite guidance | `repo-local/skills/skill-breakdown-workbench` |
| 外部专家团转换 Skill / External expert-team converter | [`expert-team-converter`](../skills/expert-team-converter/SKILL.md) | `skills/expert-team-converter/` | 将 WorkBuddy、CodeBuddy、插件或提示词形式的外部专家包转换为当前仓库的专家团 Skill 包，判断真实顶层 Skill、混合映射或 router 内部标签，并同步索引 / Convert WorkBuddy, CodeBuddy, plugin, or prompt-based expert packages into repository expert-team Skill packages, classify child entries, and update indexes | `repo-local/skills/expert-team-converter` |

## assemble-project-expert-team

- **Skill 类型 / Skill type**：动态路由与自动编排 / dynamic routing and automatic orchestration
- **不是 / Not**：固定专家团、单个 Agent、Agent 成员清单 / a fixed team, a single Agent, or a static member list
- **目标项目 / Target project**：可以是任意代码仓库，不要求本地存在 `tiny-agents` / any repository; a local `tiny-agents` checkout is not required
- **默认目录 / Default catalog**：远端 `expert-team-file-list.md` / remote `expert-team-file-list.md`
- **离线目录 / Offline catalog**：可显式传入本地 `indexes/expert-team-file-list.md` / pass a local copy explicitly
- **编排脚本 / Composer**：`skills/assemble-project-expert-team/scripts/compose_team.py`
- **默认模式 / Default mode**：`auto-execute`；只有明确要求只规划、模拟或不执行时才使用 `blueprint` / use `blueprint` only for explicit planning, simulation, or no-execution requests
- **运行时协议 / Runtime protocol**：支持 `TeamCreate`、`Agent`、`SendMessage`；Codex 环境映射到可用的 `spawn_agent`、`send_input`、`wait_agent` 和 `resume_agent` / use formal team primitives or their Codex-compatible equivalents when available
- **常见编排能力 / Common capabilities**：需求澄清、测试设计、E2E 测试、API 契约验证、架构、实现、审查和交付 / requirements, test design, E2E, API contracts, architecture, implementation, review, and delivery
- **资源边界 / Asset boundary**：不安装 Skill、不把能力复制到目标项目、不生成头像资源 / never install or copy Skills into the target project, and do not generate avatar assets
- **来源优先级 / Source priority**：目标仓库专家团 > 目标仓库 Skill/Agent > 本机已安装 Skill/Agent > 已校验的远端目录能力 / project expert team > project Skill/Agent > installed local Skill/Agent > verified remote catalog capability
- **远端可用性 / Remote usability**：远端入口只有在 router 和选中子 `SKILL.md` 均可访问、名称匹配时才能直接使用 / a remote entry is usable only when its router and selected child `SKILL.md` files are reachable with matching names

## 使用边界

`expert-team-file-list.md` 只登记固定专家团入口；本文件登记能够动态选择或协调专家团的 Skill。具体被选中的专家团和子技能，必须以任务上下文和远端目录读取结果为准，不在本索引中预先固定成员名单。

`harmony-expert-team` is intentionally listed in both indexes: `expert-team-file-list.md` records it as an expert-team entry, while this file records the repository-authored router Skill and its implementation boundary. `harmony-expert-team` 有意同时登记在两个索引中：`expert-team-file-list.md` 将其登记为专家团入口，本文件记录其自建路由 Skill 和实现边界。

`assemble-project-expert-team` 运行后应返回成员 ID、选中 Skill、来源校验、成员 Prompt、阶段依赖、交接契约、前置条件和剩余缺口。没有团队或多 Agent 原语时，只能标记为协调式能力执行，不得声称已经创建真实成员。

After execution, `assemble-project-expert-team` should return member IDs, selected Skills, source verification, member prompts, phase dependencies, handoff contracts, prerequisites, and remaining gaps. When team or multi-agent primitives are unavailable, it must label the run as coordinated capability execution instead of claiming that real members were created.

## harmonyos-app-store-self-check

- **Skill 类型 / Skill type**：项目质量门禁与 AGC 报告驱动模拟 / project quality gate and AGC report-driven simulation
- **本地预检 / Local preflight**：检查 HarmonyOS 工程结构、应用身份、权限、隐私、网络能力、签名泄露、市场截图和 `.app/.hap` 包完整性 / inspect project structure, identity, permissions, privacy, network capability, signing leaks, listing screenshots, and `.app/.hap` integrity
- **AGC 实测 / AGC live validation**：读取登录后的 AGC 软件包管理和上架自检报告，记录兼容性、稳定性、功耗、性能、UX 五类结果 / read the logged-in AGC package-management and self-check report, recording compatibility, stability, power, performance, and UX results
- **报告模拟 / Report simulation**：以用户提供的 AGC 报告为历史参考，重新核对当前项目和发布包；历史 `通过` 不会被复制为当前 `AGC_READY` / use a supplied AGC report as historical reference and re-check the current project and artifact; a historical `通过` never becomes the current `AGC_READY`
- **模拟脚本 / Simulation script**：`skills/harmonyos-app-store-self-check/scripts/simulate_agc_self_check.py`
- **结果边界 / Result boundary**：`SIMULATED_BLOCKED` 或 `SIMULATED_UNVERIFIED` 只能表示本地模拟结果；只有 AGC 当前“上架自检 = 已达标”才可记录为 `AGC_READY` / simulated statuses are local evidence only; `AGC_READY` requires the current AGC self-check state to be `已达标`
- **不是 / Not**：华为审核承诺、自动创建证书、自动上传发布包或自动提交审核 / not a Huawei approval guarantee, certificate creator, automatic uploader, or submission agent

## create-enterprise-react-app

- **Skill 类型 / Skill type**：企业级 React 项目创建与验证 / enterprise React project scaffolding and verification
- **主要能力 / Capabilities**：创建空白 Vite 工程，提供路由、状态管理、请求客户端、样式、Storybook、Vitest 和 Playwright 基线 / scaffold a blank Vite workspace with routing, state, request client, styling, Storybook, Vitest, and Playwright baselines
- **默认产物 / Default output**：可运行的企业 React 应用壳层和确定性模板 / runnable enterprise React app shell and deterministic template
- **边界 / Boundary**：不虚构后端契约、认证接口、组织规则、密钥、私有仓库地址，也不默认初始化 Git、提交、推送或部署 / does not invent backend contracts, auth endpoints, organization rules, secrets, or private registry URLs, and does not initialize Git, commit, push, or deploy by default

## skill-generation-workbench

- **Skill 类型 / Skill type**：Skill 生成、转换、升级与验证工作台 / skill generation, conversion, upgrade, and validation workbench
- **不是 / Not**：固定专家团、Agent 成员、自动安装器或自动发布器 / a fixed expert team, agent roster, auto-installer, or auto-publisher
- **目标 / Target**：为新 Skill 或现有 Skill 生成可验证的仓库包 / generate verifiable repository packages for new or existing Skills
- **默认输入 / Default inputs**：需求想法、现有 `SKILL.md`、外部提示词、专家卡片、验证要求 / ideas, existing `SKILL.md`, external prompts, expert cards, and validation requirements
- **默认产物 / Default outputs**：`SKILL.md`、`agents/openai.yaml`、`references/`、`scripts/`、`source.json` / `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `source.json`
- **默认边界 / Default boundary**：默认只生成和验证；安装、提交、推送和发布都必须先获得明确授权 / only generate and validate by default; installation, commits, pushes, and publication require explicit authorization
- **验证 / Validation**：`quick_validate.py`、`python3 -m unittest`、`git diff --check`、路径和敏感信息扫描 / structural validation, unit tests, diff checks, and path/secret scans

## skill-breakdown-workbench

- **Skill 类型 / Skill type**：Skill 和 agent 的拆解、教学与写作教练 / breakdown, teaching, and writing coach for Skills and agents
- **不是 / Not**：自动发布器、隐藏提示词猜测器、固定专家团或简单摘要器 / auto-publisher, hidden-prompt guesser, fixed expert team, or plain summarizer
- **目标 / Target**：分析现有 Skill 或 agent manifest 的写法，并教会用户如何写出更好的 Skill 和 Agent / analyze an existing Skill or agent manifest and teach better Skill and Agent authorship
- **默认输入 / Default inputs**：`SKILL.md`、`agents/openai.yaml`、用户提供的技能卡片、写作目标 / `SKILL.md`, `agents/openai.yaml`, user-provided skill cards, and writing goals
- **默认产物 / Default outputs**：中英双语拆解、写作建议、可复用模板和改写方向 / bilingual breakdowns, writing advice, reusable templates, and rewrite directions
- **默认边界 / Default boundary**：只分析可见内容；不猜隐藏 prompt；默认不安装、不提交、不发布 / analyze only visible content; do not guess hidden prompts; do not install, commit, or publish by default
- **验证 / Validation**：每个结论都能回指到可见文件，且中英部分结构对齐 / every conclusion must map back to visible files, with aligned Chinese and English sections

## expert-team-converter

- **分类 / Classification**：本仓库自建的工具型 Skill / repo-authored utility Skill
- **不是 / Not**：固定专家团、专家团成员、运行时 Agent 或 `expert-team-file-list.md` 中的专家团入口 / a fixed expert team, team member, runtime Agent, or an entry in `expert-team-file-list.md`
- **作用 / Purpose**：转换外部专家包，复用已有 Skill，判断子项是顶层 Skill、混合映射还是 router 内部能力标签 / convert external expert packages, reuse existing Skills, and classify child entries
- **索引职责 / Index responsibility**：更新 `skill-registry.md`、`skill-registry.json`，并在转换出专家团入口时更新 `expert-team-file-list.md` / update the Skill registry and update `expert-team-file-list.md` only for the converted expert-team entry
- **资源边界 / Asset boundary**：不提取隐藏 Prompt，不默认安装、提交、推送或生成头像资源 / do not extract hidden prompts, install, commit, push, or generate avatar assets by default
