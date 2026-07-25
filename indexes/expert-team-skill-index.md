# Expert-Team Skill Index

本索引登记本仓库自建或适配、且需要单独说明职责边界的能力 Skill：包括专家团路由、动态编排、项目质量门禁、项目创建、提示词生成和 Skill 工作台。它不是固定专家团清单，也不是所有普通 Skill 的总目录；固定专家团入口统一登记在 `expert-team-file-list.md`。

普通 Skill 查找请先看 `indexes/skill-registry.md` / `indexes/skill-registry.json`；本文件只保留需要参与专家团路由、项目交付或 Skill 生命周期管理的自建/适配能力。

For ordinary Skill lookup, start with `indexes/skill-registry.md` / `indexes/skill-registry.json`; this file only keeps repository-authored or adapted capabilities whose routing, project-delivery, or Skill-lifecycle boundaries need to be documented here.

| 能力类型 / Capability type | Skill | 位置 / Location | 准确职责与边界 / Responsibility & boundary | 实现与依赖 / Implementation & sources |
|---|---|---|---|---|
| 鸿蒙专家团 / HarmonyOS expert team | [`harmony-expert-team`](../skills/harmony-expert-team/SKILL.md) | `skills/harmony-expert-team/` | HarmonyOS/OpenHarmony 任务入口；按任务类型选择问答、实现、UI 生成或服务卡片子 Skill，混合任务按阶段串联，不替代子 Skill / Routes HarmonyOS/OpenHarmony work to the Q&A, implementation, UI-generation, or service-widget child Skills; sequences mixed work by phase and does not replace the child Skills | 本地 router；子能力：`harmony-os-ask`、`harmony-os-act`、`generate-ui-code`、`service-widget` / local router with four child Skills |
| 鸿蒙项目质量门禁 / HarmonyOS project quality gate | [`harmonyos-app-store-self-check`](../skills/harmonyos-app-store-self-check/SKILL.md) | `skills/harmonyos-app-store-self-check/` | 对 HarmonyOS 工程和 `.app/.hap` 做本地发布预检；可读取登录后的 AGC 上架自检结果，也可基于历史报告做保守模拟，但本地通过不等于 AGC 通过 / Runs local release preflight for HarmonyOS projects and `.app/.hap`; can read logged-in AGC self-check results and conservatively simulate from historical reports, but a local pass is never an AGC pass | 本地 Skill、AGC 控制台和 `check_harmony_release.py` / local Skill, AGC console, and `check_harmony_release.py` |
| React企业级空白项目创建 / Enterprise React blank project creator | [`create-enterprise-react-app`](../skills/create-enterprise-react-app/SKILL.md) | `skills/create-enterprise-react-app/` | 为新建或明确要求适配的 React 项目生成企业级空白壳层；覆盖 React 19、Ant Design 6、React Router 7、TanStack Query、Zustand、Axios、Tailwind CSS 4、Storybook、Vitest 和 Playwright，并要求验证构建质量 / Scaffolds a new or explicitly adapted React project shell using React 19, Ant Design 6, React Router 7, TanStack Query, Zustand, Axios, Tailwind CSS 4, Storybook, Vitest, and Playwright, then verifies the quality gates | 本地模板与 `scripts/create_project.py`；不覆盖非空目录、不默认提交或发布 / local template and `scripts/create_project.py`; refuses non-empty targets and does not commit or publish by default |
| 根据截图生成UI提示词 / Screenshot-to-UI prompt generator | [`screenshot-ui-prompt`](../skills/screenshot-ui-prompt/SKILL.md) | `skills/screenshot-ui-prompt/` | 需要视觉输入时，将截图判定为组件、区块、页面或非前端元素；先确认功能、异常和控制，再处理设计令牌/配色，输出中文优先、英文补充的可复制提示词 / With visual input, classifies a screenshot as a component, section, page, or non-front-end element; confirms behavior, exceptions, and controls before design tokens/colors, then emits a Chinese-first, English-follow-up copyable prompt | 本地 Skill、`references/prompt_templates.md` 和可选 `scripts/extract_colors.py` / local Skill, prompt templates, and optional color extractor |
| 根据现有的技能（skill）手搓专家团 / Assemble an expert team from existing Skills | [`assemble-project-expert-team`](../skills/assemble-project-expert-team/SKILL.md) | `skills/assemble-project-expert-team/` | 优先检查目标仓库和本机 Skill/Agent；能力不足时依次读取远端专家团目录、SkillHub 和 find-skills，并只纳入通过 `SKILL.md` 校验的能力 / Inspects project and local Skills/Agents first; when a capability is missing, queries the remote expert-team catalog, SkillHub, and find-skills in order, admitting only sources whose `SKILL.md` verifies | 本地 router/编排脚本；远端数据源：`expert-team-file-list.md`、`https://skillhub.cn/`、`https://skills.sh/` / local router and composer; remote sources: expert-team index, SkillHub, and skills.sh |
| skill生成器 / Skill generator | [`skill-generation-workbench`](../skills/skill-generation-workbench/SKILL.md) | `skills/skill-generation-workbench/` | 写入前先用 find-skills 查找，再用 SkillHub 查询可复用能力；然后从想法、现有 Skill、外部提示词或专家卡片设计、生成、升级和验证 Skill 包，默认不安装、提交或发布 / Searches find-skills first and SkillHub second before writing; then designs, generates, upgrades, and validates Skill packages from ideas, existing Skills, external prompts, or expert cards without installing, committing, or publishing by default | 本地工作台、find-skills、`https://skillhub.cn/` 及其 `references/`、`scripts/` / local workbench, find-skills, SkillHub, references, and scripts |
| 拆解现有的skill / Break down existing Skill | [`skill-breakdown-workbench`](../skills/skill-breakdown-workbench/SKILL.md) | `skills/skill-breakdown-workbench/` | 读取可见的 `SKILL.md`/Agent manifest，生成必须落盘为 `.md` 的中英双语拆解、写作教学、公式和模板；不猜隐藏 Prompt / Reads visible Skill/Agent manifests and writes a required bilingual Markdown teardown with writing lessons, formulas, and templates; never guesses hidden prompts | 本地工作台及其 `references/guide.md` / local workbench and `references/guide.md` |
| 外部专家团转换成Codex专家团 / External expert-team to Codex expert-team converter | [`expert-team-converter`](../skills/expert-team-converter/SKILL.md) | `skills/expert-team-converter/` | 将 WorkBuddy、CodeBuddy、插件或提示词包转换为仓库 Skill/专家团格式；复用已有能力并区分顶层 Skill、混合映射和 router 内部标签，按转换结果更新对应索引 / Converts WorkBuddy, CodeBuddy, plugin, or prompt packages into repository Skill/expert-team format; reuses existing capabilities, classifies top-level Skills versus hybrid or internal router labels, and updates the relevant indexes | 本地转换工作台及其 `references/`；不提取隐藏 Prompt、不默认安装或发布 / local converter and references; no hidden-prompt extraction, installation, or publication by default |

## assemble-project-expert-team

- **Skill 类型 / Skill type**：动态专家团路由与编排，不是固定专家团 / dynamic expert-team routing and orchestration, not a fixed team
- **不是 / Not**：固定专家团、单个 Agent、Agent 成员清单 / a fixed team, a single Agent, or a static member list
- **目标项目 / Target project**：可以是任意代码仓库，不要求本地存在 `tiny-agents` / any repository; a local `tiny-agents` checkout is not required
- **默认目录 / Default catalog**：从 GitHub 远端读取 `indexes/expert-team-file-list.md`；本地 `tiny-agents` 不是必需依赖 / read `indexes/expert-team-file-list.md` from GitHub; a local `tiny-agents` checkout is not required
- **离线目录 / Offline catalog**：可显式传入本地 `indexes/expert-team-file-list.md` / pass a local copy explicitly
- **编排脚本 / Composer**：`skills/assemble-project-expert-team/scripts/compose_team.py`
- **默认模式 / Default mode**：`auto-execute`；只有明确要求只规划、模拟或不执行时才使用 `blueprint` / use `blueprint` only for explicit planning, simulation, or no-execution requests
- **运行时协议 / Runtime protocol**：有正式团队或多 Agent 原语时才创建/调度成员；否则由当前协调者按同一阶段契约执行，并明确标记为协调式能力执行 / create and dispatch members only when formal team or multi-agent primitives exist; otherwise the coordinator executes the same phase contract and labels it coordinated capability execution
- **常见编排能力 / Common capabilities**：需求澄清、测试设计、E2E 测试、API 契约验证、架构、实现、审查和交付 / requirements, test design, E2E, API contracts, architecture, implementation, review, and delivery
- **资源边界 / Asset boundary**：不安装 Skill、不把能力复制到目标项目、不生成头像资源 / never install or copy Skills into the target project, and do not generate avatar assets
- **来源优先级 / Source priority**：目标仓库专家团 > 目标仓库 Skill/Agent > 本机已安装 Skill/Agent > 已校验的远端专家团目录 > 已校验的 SkillHub > 已校验的 find-skills / project expert team > project Skill/Agent > installed local Skill/Agent > verified expert-team catalog > verified SkillHub > verified find-skills
- **远端可用性 / Remote usability**：远端专家团入口需校验 router 和选中子 `SKILL.md`；SkillHub 需校验包内 `SKILL.md`；find-skills 需解析并校验 GitHub `SKILL.md` / remote expert-team entries require router and selected child `SKILL.md` verification; SkillHub requires package `SKILL.md` verification; find-skills requires a matching GitHub `SKILL.md`

## 使用边界

`expert-team-file-list.md` 只登记固定专家团入口；本文件登记需要说明实现职责的自建/适配 Skill，不代表表内每一项都是专家团。具体被选中的专家团和子技能，必须以任务上下文、目标仓库证据和远端目录读取结果为准，不在本索引中预先固定动态团队成员。

`harmony-expert-team` is intentionally listed in both indexes: `expert-team-file-list.md` records the fixed expert-team entry, while this file records the repository-authored router Skill and its implementation boundary. `harmony-expert-team` 有意同时登记在两个索引中：`expert-team-file-list.md` 登记固定专家团入口，本文件登记自建 router Skill 及其实现边界。

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

## screenshot-ui-prompt

- **Skill 类型 / Skill type**：截图驱动的 UI/UX 提示词生成 / screenshot-driven UI/UX prompt generation
- **四阶段流程 / Four phases**：分类 → 优先确认功能范围与异常/控制要求 → 收集设计令牌和风格约束 → 输出提示词 / classify → confirm functional scope and exception/control requirements first → gather design constraints and style → emit the prompt
- **分类 / Classification**：组件、区块、页面、非前端元素；遇到流程图、照片、文档等非前端内容必须先让用户选择处理方式 / component, section, page, or non-front-end; ask before treating flowcharts, photos, or documents as UI
- **默认输出 / Default output**：中文在前、英文在后的可复制提示词，包含功能、异常、控制、Props、事件、数据交互、生产级工程要求、风格词、布局、配色、排版、交互和技术栈 / copyable Chinese-first and English-second prompts covering functional behavior, exceptions, controls, Props, events, data interaction, production requirements, style words, layout, color, typography, interaction, and stack
- **颜色提取 / Color extraction**：按用户选择运行 `scripts/extract_colors.py`；缺少 Pillow 时报告依赖缺口，不自动安装 / run `scripts/extract_colors.py` when selected; report a missing Pillow dependency instead of installing automatically
- **不是 / Not**：纯代码审查、只要口头描述、无视觉能力时的猜测，或只输出视觉结构而不说明功能边界 / not pure code review, a verbal-only description, guessing without vision, or a visual-only prompt without functional boundaries

## skill-generation-workbench

- **旧名称 / Previous display name**：`Skill 生成工作台`；当前展示名为 `skill生成器` / previous display name: `Skill 生成工作台`; current display name: `skill生成器`
- **Skill 类型 / Skill type**：Skill 生成、转换、升级与验证工作台 / skill generation, conversion, upgrade, and validation workbench
- **不是 / Not**：固定专家团、Agent 成员、自动安装器或自动发布器 / a fixed expert team, agent roster, auto-installer, or auto-publisher
- **目标 / Target**：为新 Skill 或现有 Skill 生成可验证的仓库包 / generate verifiable repository packages for new or existing Skills
- **默认输入 / Default inputs**：需求想法、现有 `SKILL.md`、外部提示词、专家卡片、验证要求 / ideas, existing `SKILL.md`, external prompts, expert cards, and validation requirements
- **默认产物 / Default outputs**：`SKILL.md`、`agents/openai.yaml`、`references/`、`scripts/`、`source.json` / `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `source.json`
- **默认边界 / Default boundary**：默认只生成和验证；安装、提交、推送和发布都必须先获得明确授权 / only generate and validate by default; installation, commits, pushes, and publication require explicit authorization
- **验证 / Validation**：`quick_validate.py`、`python3 -m unittest`、`git diff --check`、路径和敏感信息扫描 / structural validation, unit tests, diff checks, and path/secret scans

## skill-breakdown-workbench

- **旧名称 / Previous display name**：`Skill 拆解与写作工作台`；当前展示名为 `拆解现有的skill` / previous display name: `Skill 拆解与写作工作台`; current display name: `拆解现有的skill`
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
