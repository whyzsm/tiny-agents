# Skill Team Router Index

本索引登记“负责动态编排专家团的 Skill”，不登记固定专家团、Agent 成员或具体业务专家。

| 类型 / Type | Skill | 位置 / Location | 作用 / Purpose | 能力来源 / Source |
|---|---|---|---|---|
| 动态专家团编排 Skill / Dynamic expert-team assembler | [`assemble-project-expert-team`](../skills/assemble-project-expert-team/SKILL.md) | `skills/assemble-project-expert-team/` | 扫描目标项目，读取远端专家团目录，自动生成成员 roster、成员 Prompt、阶段 DAG 和质量门，并按运行时能力协调执行 / Scan the target project, read the remote expert-team catalog, generate the roster, member prompts, phase DAG, and quality gates, then coordinate execution according to runtime capabilities | `https://github.com/whyzsm/tiny-agents/tree/main/indexes` |

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

## 使用边界

`expert-team-file-list.md` 只登记固定专家团入口；本文件登记能够动态选择或协调专家团的 Skill。具体被选中的专家团和子技能，必须以任务上下文和远端目录读取结果为准，不在本索引中预先固定成员名单。

`assemble-project-expert-team` 运行后应返回成员 ID、选中 Skill、来源校验、成员 Prompt、阶段依赖、交接契约、前置条件和剩余缺口。没有团队或多 Agent 原语时，只能标记为协调式能力执行，不得声称已经创建真实成员。

After execution, `assemble-project-expert-team` should return member IDs, selected Skills, source verification, member prompts, phase dependencies, handoff contracts, prerequisites, and remaining gaps. When team or multi-agent primitives are unavailable, it must label the run as coordinated capability execution instead of claiming that real members were created.
