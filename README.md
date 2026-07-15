# tiny-agents

Local CLI for scanning and organizing personal AI agents and skills.

用于扫描和整理个人 AI agents 与 skills 的本地 CLI。

## Commands

Generate a dry-run report:

生成 dry-run 扫描报告：

```bash
python3 -m tiny_agents scan
```

Import confirmed ready items from a report:

从已确认的报告中导入 ready 项：

```bash
python3 -m tiny_agents import reports/scan-2026-07-05.json
```

Refresh the canonical skill registry:

刷新技能主索引：

```bash
python3 scripts/generate_skill_registry.py
```

The first version scans `~/.codex` and `~/.agents`, excludes system, cache, and
sensitive paths, blocks suspected secrets, and imports only ready agents and
skills.

第一版会扫描 `~/.codex` 和 `~/.agents`，排除系统、缓存和敏感路径，阻断疑似密钥，并只导入
ready 状态的 agents 和 skills。

## Indexes

`indexes/skill-registry.md` and `indexes/skill-registry.json` are the canonical
lookup entry points for installable skills in this repository.

`indexes/skill-registry.md` 和 `indexes/skill-registry.json` 是本仓库可安装
skills 的主查找入口。

`indexes/agent-skill-index.md` and `indexes/agent-skill-index.json` are the
local scan inventory for imported agents and skills.

`indexes/agent-skill-index.md` 和 `indexes/agent-skill-index.json` 是导入后的
本地扫描库存。

`indexes/skill-team-router-index.md` and `indexes/expert-team-file-list.md`
are specialized catalogs for orchestration, not the primary install lookup.

`indexes/skill-team-router-index.md` 和 `indexes/expert-team-file-list.md` 是
编排专用目录，不是主安装查找入口。

## Agent And Skill Boundary

A skill is a capability, workflow, or tool instruction. It should not carry an
independent personality, identity, or soul.

Skill 是能力、流程或工具说明。它不应该承载独立人格、身份或灵魂。

An agent is a role-bearing prompt or manifest. A `SKILL.md` with clear identity,
persona, role, personality, or soul settings is reported as a candidate instead
of being imported as a skill automatically.

Agent 是带角色的 prompt 或 manifest。带有明确身份、persona、角色、性格或灵魂设定的
`SKILL.md` 会被报告为 candidate，而不会自动作为 skill 导入。

## Repository Layout

`agents/` stores imported agent prompts and their sanitized `source.json`
metadata.

`agents/` 存放导入的 agent prompts 以及已脱敏的 `source.json` 来源元数据。

`skills/` stores imported skills, references, helper files, and sanitized
`source.json` metadata.

`skills/` 存放导入的 skills、references、辅助文件以及已脱敏的 `source.json` 来源元数据。

`tiny_agents/` contains the Python CLI implementation.

`tiny_agents/` 存放 Python CLI 实现。

## Safety

Generated `source.json` files use public source paths such as `~/.codex/...`,
not local absolute paths.

生成的 `source.json` 使用 `~/.codex/...` 这类公开来源路径，而不是本机绝对路径。

Suspected secrets cause an item to be marked as blocked and skipped during
import.

疑似密钥会让条目被标记为 blocked，并在导入时跳过。
