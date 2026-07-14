# Skill Team Router Index

本索引登记“负责动态编排专家团的 Skill”，不登记固定专家团、Agent 成员或具体业务专家。

| 类型 | Skill | 位置 | 作用 | 能力来源 |
|---|---|---|---|---|
| 动态专家团编排 Skill | [`assemble-project-expert-team`](../skills/assemble-project-expert-team/SKILL.md) | `skills/assemble-project-expert-team/` | 读取远端专家团目录，根据目标项目、任务要求和质量门动态选择最小充分的专家团 | `https://github.com/whyzsm/tiny-agents/tree/main/indexes` |

## assemble-project-expert-team

- **Skill 类型**：动态路由/编排 Skill
- **不是**：固定专家团、单个 Agent、Agent 成员清单
- **目标项目**：可以是任意代码仓库，不要求本地存在 `tiny-agents`
- **默认目录**：远端 `expert-team-file-list.md`
- **离线目录**：可显式传入本地 `indexes/expert-team-file-list.md`
- **常见编排能力**：需求澄清、测试设计、E2E 测试、API 契约验证、架构、实现、审查和交付

## 使用边界

`expert-team-file-list.md` 只登记固定专家团入口；本文件登记能够动态选择或协调专家团的 Skill。具体被选中的专家团和子技能，必须以任务上下文和远端目录读取结果为准，不在本索引中预先固定成员名单。
