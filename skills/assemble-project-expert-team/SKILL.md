---
name: assemble-project-expert-team
description: "项目专家团编排器。用于读取远端专家团索引，根据目标项目和任务要求动态选择最小充分的专家团，覆盖需求澄清、架构、实现、测试、调试、审查、发布和质量验证。 Project expert-team assembler. Use it to read the remote expert-team catalog and dynamically select the smallest sufficient team for a target project and task, including requirements clarification, architecture, implementation, testing, debugging, review, release, and quality verification."
metadata:
  source: "https://github.com/whyzsm/tiny-agents/tree/main/indexes"
  catalog: "expert-team-file-list.md"
  team_type: "dynamic-router"
---

# 项目专家团编排器 / Project Expert-Team Assembler

Use this skill as the dynamic expert-team entry point for project work. 使用本 Skill 作为项目工作的动态专家团入口。

It reads the remote expert-team catalog, inspects the target repository, and composes a small capability-based team instead of using a fixed persona bundle. 它读取远端专家团目录、检查目标代码仓库，并按能力组合小型专家团，而不是使用固定人格包。

## 工作流 / Workflow

1. Read `references/guide.md` to separate the target project from the remote capability catalog and classify the delivery mode. 读取 `references/guide.md`，区分目标项目与远端能力目录，并判断交付模式。
2. Inspect repository instructions, manifests, affected code, tests, CI, and runtime constraints. 检查仓库规则、项目清单、受影响代码、测试、CI 和运行时约束。
3. Run `scripts/discover_skills.py` from this skill directory to rank expert-team entries in the remote catalog. 从本 Skill 目录运行 `scripts/discover_skills.py`，对远端目录中的专家团入口排序。
4. Read shortlisted router and child `SKILL.md` files before selecting capabilities. 选择能力前，完整读取入选的专家团入口和子 `SKILL.md`。
5. Follow `references/workflow.md` to create a blueprint, coordinate execution, or generate a reusable team package. 按 `references/workflow.md` 生成蓝图、协调执行或生成可复用团队包。
6. Return the roster, phase dependencies, handoff contracts, exclusions, verification evidence, and remaining gaps. 返回成员清单、阶段依赖、交接契约、排除项、验证证据和剩余缺口。

## 能力来源 / Source Capability Modules

- `requirements-analysis` — clarify goals, scope, stakeholders, and acceptance criteria. 澄清目标、范围、利益相关者和验收标准。
- `test-patterns` — unit, integration, mocking, coverage, and test-runner workflows. 提供单元测试、集成测试、Mock、覆盖率和测试运行器流程。
- `e2e-testing-patterns` — browser journeys, stable selectors, network isolation, and flaky-test control. 提供浏览器流程、稳定选择器、网络隔离和不稳定测试治理。
- `qa-api-tester` — HTTP contract checks, response validation, auth cases, and executable API test plans. 提供 HTTP 契约检查、响应校验、认证场景和可执行 API 测试计划。

These are bootstrap capabilities for common requests, not a fixed roster. 这些是常见请求的启动能力，不是固定成员名单。

Select only the indexed capabilities required by the target task. 只选择目标任务实际需要、且已登记在索引中的能力。

## 输出 / Output

Produce only the deliverables required by the request. 只产出请求所需的交付物。

A blueprint contains the objective, roster, phased workflow, input/output dependencies, exclusions, assumptions, and verification gates. 蓝图包含目标、成员、分阶段流程、输入输出依赖、排除项、假设和验证门。

An execution result additionally contains changed artifacts, commands, evidence, and residual risks. 执行结果还要包含变更产物、执行命令、证据和残余风险。

A reusable package must follow `references/team-package-spec.md`. 可复用团队包必须遵循 `references/team-package-spec.md`。
