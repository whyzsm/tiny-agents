# 可复用团队包规范 / Reusable Team Package Specification

Read this file only in package mode. 仅在 Package 模式读取本文件。

Follow stricter rules from the target repository when they conflict with this generic specification. 如果目标仓库有更严格规则，以目标仓库规则为准。

## 目录 / Contents

1. Package choice / 团队包选择
2. Router skill package / Router Skill 包
3. Formal expert-team plugin / 正式专家团 Plugin
4. Agent definitions / Agent 定义
5. Team workflow rules / 团队工作流规则
6. Names and avatars / 名称与头像
7. Validation / 校验

## 1. 团队包选择 / Choose The Package Type

Use a router Skill package when the target is a Codex capability repository and the team only coordinates existing Skills. 当目标是 Codex 能力仓库、团队只需协调已有 Skill 时，使用 router Skill 包。

Use a formal expert-team plugin only when the user requests standalone Agents, marketplace metadata, team runtime behavior, or publication artifacts. 只有用户要求独立 Agent、市场元数据、团队运行时行为或发布产物时，才使用正式专家团 Plugin。

Do not duplicate existing Skills. Select from `https://github.com/whyzsm/tiny-agents/tree/main/indexes`, reference exact frontmatter names, and verify every selected remote address returns a valid `SKILL.md`. 不要复制已有 Skill；从远端索引选择，引用准确的 frontmatter 名称，并确认每个选中的远端地址都返回有效 `SKILL.md`。

## 2. Router Skill 包 / Router Skill Package

Prefer this layout when the repository treats `skills/` as capability packages. 当仓库将 `skills/` 视为能力包时，优先使用以下布局：

```text
skills/<team-name>-team/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── manifest.json
    └── workflow.md
```

Require the following. 必须满足以下要求：

- `SKILL.md` frontmatter contains `name` and a trigger-rich `description`; keep extra fields aligned with local conventions. `SKILL.md` frontmatter 必须包含 `name` 和触发条件清晰的 `description`，其他字段遵循本地规范。
- Include a routing table mapping request types to the narrowest selected Skills. 提供将请求类型映射到最窄 Skill 的路由表。
- Define phases with explicit inputs, outputs, dependencies, gates, and exclusions. 定义明确的输入、输出、依赖、质量门和排除项的阶段流程。
- `manifest.json` contains the team slug, display name, summary, and selected Skill names. `manifest.json` 包含团队 slug、展示名称、摘要和选中的 Skill 名称。
- `agents/openai.yaml` contains quoted `display_name`, a 25-64 character `short_description`, and a one-sentence `default_prompt` mentioning `$<team-name>-team`. `agents/openai.yaml` 包含带引号的 `display_name`、25-64 字符的 `short_description` 和提及 `$<team-name>-team` 的单句 `default_prompt`。

Keep identities and personalities out of router Skills. Router Skill 不承载身份和人格。

## 3. 正式专家团 Plugin / Formal Expert-Team Plugin

Use this minimum layout. 使用以下最小布局：

```text
<team-name>/
├── plugin.json
├── settings.json
├── agents/
│   ├── <team-name>-team-lead.md
│   └── <member-id>.md
```

Avatar files are optional and omitted by default. If `plugin.json` needs an `avatar` field, set it to `null` or an empty value; do not create an `avatars/` directory unless publication-ready visuals are explicitly requested. 头像文件是可选的，默认省略；如果 `plugin.json` 必须保留 `avatar` 字段，将其设为 `null` 或空值；除非用户明确要求发布级视觉物料，否则不要创建 `avatars/` 目录。

`settings.json` must contain the following. `settings.json` 必须包含：

```json
{
  "agent": "<team-name>-team-lead"
}
```

Keep `settings.json.agent`, `plugin.json.agentName`, `teamInfo.leadAgent`, and the lead frontmatter `name` identical. `settings.json.agent`、`plugin.json.agentName`、`teamInfo.leadAgent` 和主理人 frontmatter 的 `name` 必须完全一致。

Require these `plugin.json` fields. `plugin.json` 必须包含以下字段：

```text
name, version, description, agents, expertType, agentName,
teamInfo, displayName, profession, displayDescription, avatar,
categoryId, defaultInitPrompt, plugin, tags, quickPrompts, members
```

Enforce the following. 必须执行以下约束：

- `name` and `plugin` use the same kebab-case identifier. `name` 和 `plugin` 使用同一个 kebab-case 标识。
- `expertType` is `"team"`. `expertType` 必须是 `"team"`。
- `agents` lists the lead and every member MD path. `agents` 列出主理人和所有成员 MD 路径。
- `teamInfo.memberAgents` lists members but excludes the lead. `teamInfo.memberAgents` 列出成员但不包含主理人。
- `members` includes the lead with role `"lead"` and every member with role `"member"`. `members` 包含 `role: "lead"` 的主理人和 `role: "member"` 的所有成员。
- Team `profession` equals `displayName` in both languages. 团队中英文 `profession` 必须分别等于 `displayName`。
- `displayDescription.zh` is 40-50 Chinese characters and states the core capability. `displayDescription.zh` 为 40-50 个中文字符并说明核心能力。
- `tags` contains exactly three bilingual entries. `tags` 恰好包含三组双语条目。
- `quickPrompts` contains exactly three bilingual entries. `quickPrompts` 恰好包含三组双语条目。
- `defaultInitPrompt` equals the first quick prompt in each language. `defaultInitPrompt` 在每种语言中都等于第一条 quick prompt。

## 4. Agent 定义 / Agent Definitions

Use this frontmatter for every member. 每个成员使用以下 frontmatter：

```yaml
---
name: <member-id>
description: <English activation description>
displayName:
  en: "<English display name>"
  zh: "<中文姓名>"
profession:
  en: "<English profession>"
  zh: "<中文职业>"
maxTurns: 50
skills: [<primary-skill>]
---
```

Omit `skills` only when no repository Skill is assigned. 没有分配仓库 Skill 时才省略 `skills`。

Never add a `tools` field; runtime policy owns tool permissions. 永远不要添加 `tools` 字段；工具权限由运行时策略管理。

Give each member document the following sections. 每个成员文档必须包含以下章节：

1. Role definition. 角色定义。
2. Three to five concrete capability points derived from the selected Skill. 从选中 Skill 提炼的 3-5 个具体能力点。
3. Stepwise analysis or execution framework. 分步骤的分析或执行框架。
4. Project-specific evidence commands or tool calls. 面向项目的证据获取命令或工具调用。
5. Structured output template. 结构化输出模板。
6. Explicit requirement to return results to the lead through `SendMessage`. 明确要求通过 `SendMessage` 向主理人回传结果。

Use a business-specific lead ID such as `<team-name>-team-lead`; never use plain `team-lead`. 使用带业务语义的主理人 ID，例如 `<team-name>-team-lead`，不要使用通用的 `team-lead`。

Set lead `maxTurns` to 150-200 when the runtime supports long orchestration. 运行时支持长流程编排时，将主理人的 `maxTurns` 设为 150-200。

The lead document lists every member's ID, capabilities, direct-question examples, and owned output. Include preset workflows and a direct-routing table. 主理人文档列出每个成员的 ID、能力、典型问法和负责产出，并包含预设工作流与单 Agent 直调路由表。

## 5. 团队工作流规则 / Team Workflow Rules

Encode these rules in the lead document when formal team primitives exist. 运行时提供正式团队原语时，将以下规则写入主理人文档：

1. The lead alone creates the team with `TeamCreate`. 只能由主理人使用 `TeamCreate` 创建团队。
2. The lead spawns members by exact Agent ID and assigns independent outputs. 主理人按准确 Agent ID spawn 成员并分配独立产出。
3. Members return results to the lead through `SendMessage`. 成员通过 `SendMessage` 向主理人回传结果。
4. All cross-member information is relayed by the lead. 所有跨成员信息都由主理人中转。
5. Specialist conclusions come from the responsible member; the lead coordinates and integrates. 专业结论由负责成员产出，主理人只负责协调和集成。
6. Serial phases wait for required upstream results; independent members may run in parallel. 串行阶段等待上游结果，独立成员可以并行。
7. The lead reports progress after each phase and never spawns itself. 主理人每阶段报告进展，且不得 spawn 自己。

Do not claim formal team execution on runtimes that lack these primitives. 在缺少这些原语的运行时，不得声称进行了正式团队执行。

Preserve the workflow as a blueprint or use coordinated capability execution instead. 应保留为蓝图，或改用协调式能力执行。

## 6. 名称与头像 / Names And Avatars

For formal marketplace packages, give each person a natural bilingual name distinct from the profession. 对正式市场团队包，为每个人提供自然的双语姓名，且不能与职业重复。

Avoid random names, function words, repeated syllables, and Agent IDs as English names. 避免随机姓名、功能词、叠词，以及将 Agent ID 当作英文姓名。

Give the lead a business-specific profession instead of `Team Lead` or `主理人`. 主理人的职业应体现业务调度定位，不要使用 `Team Lead` 或 `主理人`。

Do not generate team, lead, or member avatars unless publication-ready visuals are explicitly requested. 本任务默认不生成团队、主理人或成员头像；只有用户明确要求发布级视觉物料时才生成。

Derive each prompt from the corresponding agent document, keep one professional illustration style, and do not use generic role templates. 每个 prompt 必须从对应 Agent 文档提取，保持统一的专业插画风格，不要使用通用角色模板。

If avatar files are present because the user requested them, validate them as square PNG/JPG assets, preferably 512x512 and no larger than 500 KB. 如果用户明确要求头像并且文件存在，应校验其为正方形 PNG/JPG，推荐 512x512，且不超过 500 KB。

If visuals cannot be generated, report the package as incomplete; do not create placeholders or claim publication readiness. 如果无法生成视觉资源，应报告团队包不完整，不要创建占位文件或声称已达到发布标准。

## 7. 交付前校验 / Validate Before Handoff

Check the following. 检查以下内容：

- Every identifier is kebab-case and every referenced file exists. 所有标识均为 kebab-case，所有引用文件都存在。
- Lead identifiers match across all files. 所有文件中的主理人标识一致。
- Member lists match across `agents`, `teamInfo`, and `members`. `agents`、`teamInfo` 和 `members` 中的成员清单一致。
- Every member's selected Skill exists and suits its owned output. 每个成员选中的 Skill 存在且适合其负责的产出。
- No member duplicates another member's output. 没有成员重复负责其他成员的产出。
- Workflows define triggers, phase order, parallel/serial behavior, and input/output dependencies. 工作流定义了触发条件、阶段顺序、串并行行为和输入输出依赖。
- Agent frontmatter contains no `tools` field. Agent frontmatter 不包含 `tools` 字段。
- Generated files contain no local absolute paths, secrets, credentials, caches, or local-only reports. 生成文件不包含本机绝对路径、密钥、凭据、缓存或仅供本地使用的报告。
- JSON and YAML parse successfully. JSON 和 YAML 均能成功解析。
- Router Skills pass the available Skill validator. Router Skill 通过可用的 Skill 校验器。
