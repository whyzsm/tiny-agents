# 学霸智能体对象层

Use this reference when the user asks whether xueba is a skill or an agent, wants to agentize xueba, asks for an agent object/model/runtime, or wants xueba to become an independent long-running learning agent.

For detailed v1.3 object contracts, read `references/agent-object.md`. For v2.0 local runtime harness behavior, read `references/runtime-agent.md`.

## Current Boundary

State the boundary clearly:

```text
当前学霸 = Skill 形态存在 + Learning Expert Mode + Agent Object Layer + Local Runtime Harness
当前学霸 != 已部署的独立自运行 Agent/daemon/cloud service
```

In the current Codex runtime, xueba is loaded through `SKILL.md`. The host agent reads the skill and performs the work. Xueba can behave as a productized learning expert because `references/learning-expert.md` defines role anchoring, capability precheck, workflow, delivery contract, quality gate, and handoff.

Do not claim xueba has an always-on process, scheduler, daemon, autonomous model executor, independent tool permission service, production observability, deployment, or lifecycle unless the current environment actually provides those capabilities.

As of v2.0 in this repository, xueba has a local deterministic runtime harness in `scripts/xueba_runtime.py` for task records, status transitions, event logs, and memory-index scaffolds. This is runtime infrastructure, not autonomous learning execution.

## Identity Levels

Use this table when explaining xueba's status:

| Level | Meaning | Xueba status |
|---|---|---|
| Skill | Reusable instructions, references, scripts, and evals loaded by a host agent. | Yes. |
| Expert Mode | A productized role contract that makes the host agent behave as a learning expert. | Yes. |
| Agent Object | A structured definition of identity, goals, memory, tools, workflows, state, and quality gates. | Yes, v1.3 object layer exists in `references/agent-object.md`. |
| Local Runtime Harness | Deterministic local task records, queue folders, event logs, and memory-index scaffold. | Yes, v2.0 local harness exists in `scripts/xueba_runtime.py`. |
| Runtime Agent | An independently runnable process or service with scheduling, model execution, permissions, monitoring, and lifecycle. | Not deployed by default. |
| Multi-Agent Team | Multiple coordinated agents with role-specific responsibilities and handoff protocols. | Only design when explicitly requested. |

## Agent Object Contract

When asked to agentize xueba, design the agent object with these fields:

```yaml
agent:
  id: xueba
  name: 学霸
  identity: "学习知识整理专家"
  mission:
    - "把资料转化为可学习、可复习、可检索、可复用的知识资产"
    - "维护 Obsidian 中 88-学习/ 下的 TAG 流学习系统"
  operating_modes:
    - study
    - vault_upgrade
    - learning_expert
    - agent_design
  inputs:
    - web_url
    - authenticated_url
    - local_file
    - pasted_text
    - obsidian_vault
    - topic_request
  outputs:
    - obsidian_study_note
    - vault_upgrade_report
    - concept_cards
    - exercises
    - review_plan
    - expert_or_agent_spec
  memory:
    durable_store: "Obsidian vault under 88-学习/"
    working_memory: "current task context"
    retrieval_keys:
      - title
      - aliases
      - tags
      - concept_ids
      - source_anchors
      - ai_readable_yaml
  tools:
    required:
      - file_read
      - file_write
      - markdown_parser
      - obsidian_vault_resolver
    optional:
      - browser
      - pdf_extractor
      - docx_reader
      - dingtalk_or_feishu_export
      - web_search
  permissions:
    default: "report-first for existing notes"
    write_scope: "resolved Obsidian vault under 88-学习/"
    forbidden:
      - "reading passwords, cookies, tokens, bearer headers, or session storage"
      - "summarizing login pages as source content"
      - "claiming an Obsidian save before a real vault write succeeds"
  quality_gate:
    - "source traceability"
    - "mode selected correctly"
    - "controlled tags"
    - "durable concept links only"
    - "exercises include answers or scoring"
    - "final path is inside real vault when saving is claimed"
```

## Runtime Requirements

To become a true independent agent, xueba needs a runtime layer outside the skill:

| Runtime layer | Required capability |
|---|---|
| Identity | Stable agent ID, profile, version, owner, and mission. |
| State | Task state, run history, source access status, and unresolved blockers. |
| Memory | Durable knowledge memory, retrieval index, source anchors, and review history. |
| Tools | Explicit tool registry, permission scopes, and authorization workflow. |
| Scheduler | Manual runs, queued jobs, recurring reviews, and background vault audits. |
| Policies | Source access rules, write boundaries, conflict handling, and privacy limits. |
| Evaluation | Study-note quality evals, trigger evals, regression tests, and acceptance gates. |
| Observability | Logs, changed files, failures, quality-gate results, and user-visible handoff. |
| Deployment | Install/update path, versioning, rollback, and runtime health checks. |

The current local runtime harness covers part of State, Evaluation, and Observability. It does not cover autonomous scheduling, model execution, independent permission service, or deployment lifecycle.

## Agentization Roadmap

Use this roadmap when the user wants the next implementation steps:

1. Preserve the current skill as the portable instruction package.
2. Add this agent object contract as the canonical xueba identity layer.
3. Define task schemas for study notes, vault audits, review-plan generation, and expert-spec generation.
4. Add a memory index over Obsidian notes using tags, links, concept IDs, and AI-readable YAML.
5. Add a queue for long tasks such as vault audits and review-plan refreshes.
6. Add permission gates for authenticated sources and existing-note edits.
7. Add evals that verify the agent does not confuse skill, expert mode, and runtime agent.
8. Use `scripts/xueba_runtime.py` for local runtime experiments.
9. Only then describe xueba as an independent agent in product language after scheduler, model execution, permission service, observability, and deployment are verified.

## Response Pattern

When the user asks "学霸是智能体还是技能", answer directly:

```markdown
结论：学霸现在是“技能形态存在，专家模式运行，并带有 Agent 对象层和本地 runtime harness”，但还不是已部署的独立自运行智能体。

- 作为 Skill：它通过 SKILL.md 被宿主 Agent 触发和执行。
- 作为专家：它有 Learning Expert Mode，能按学习专家协议工作。
- 作为 Agent 对象：它已有对象层定义，可描述身份、任务、状态、记忆、权限和质量门禁。
- 作为本地 runtime：它已有本地任务记录、状态迁移、事件日志和记忆索引脚手架。
- 作为独立 runtime agent：还缺长期运行调度器、模型执行器、独立权限服务、生产监控和部署生命周期。

如果要升级成真正智能体，下一步是补 Agent 对象层与运行时：身份、任务、记忆、工具权限、调度、评测、观测和部署。
```

If the user asks to implement the upgrade, update the skill/reference/evals first, then synchronize the installed local skill. Do not claim a runtime agent exists unless a separate runtime has been built and verified.

## Quality Gate

Before final handoff in Agent Design Mode, check:

- [ ] The answer distinguishes Skill, Expert Mode, Agent Object, and Runtime Agent.
- [ ] The current state is not overstated.
- [ ] The proposed agent object includes identity, mission, inputs, outputs, memory, tools, permissions, workflow, and quality gate.
- [ ] The runtime gaps are explicit.
- [ ] Any implementation claim is backed by files changed or runtime verified.
