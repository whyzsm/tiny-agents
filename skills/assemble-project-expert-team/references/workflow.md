---
scene: "项目质量 / Project Quality"
sub_scene: "assemble-project-expert-team"
skills:
  - "requirements-analysis"
  - "test-patterns"
  - "e2e-testing-patterns"
  - "qa-api-tester"
source: "https://github.com/whyzsm/tiny-agents/tree/main/indexes"
---

# 项目专家团编排器工作流 / Project Expert-Team Assembler Workflow

Select only the steps required by the task; do not load every bootstrap capability mechanically. 按任务范围选择必要步骤，不要机械加载全部启动能力。

## 步骤 1：任务契约 / Step 1: Task Contract

Clarify the goal, deliverable, target project, affected scope, acceptance criteria, timeline, permissions, environment, test data, and prohibited actions. 明确目标、交付物、目标项目、影响范围、验收标准、时间约束、权限、环境、测试数据和不可执行事项。

Record open questions that could change team composition. 记录会改变团队组成的开放问题。

## 步骤 2：项目扫描 / Step 2: Project Scan

Read repository instructions, stack, routes or entry points, affected modules, services, state management, test configuration, CI, mocks, and existing tests. 读取仓库规则、技术栈、路由或入口、受影响模块、服务接口、状态管理、测试配置、CI、mock 和现有测试。

Output facts, assumptions, risks, and verification boundaries. 输出事实、假设、风险和验证边界。

## 步骤 3：索引路由 / Step 3: Catalog Routing

Use `scripts/discover_skills.py` to query the remote `expert-team-file-list.md`. 使用 `scripts/discover_skills.py` 查询远端 `expert-team-file-list.md`。

Keep relevant expert-team entries and child-skill names, then read complete `SKILL.md` files for shortlisted routers and candidate children. 保留相关专家团入口和子技能名称，再读取入选入口及候选子 Skill 的完整 `SKILL.md`。

Confirm capability, dependencies, expected output, and whether the selected source can actually be reached. 确认能力、依赖、预期输出以及选中的源是否可实际访问。

## 步骤 4：最小编排 / Step 4: Minimal Composition

Give each member one independent output or quality gate. 让每名成员负责一个独立产出或质量门。

```text
Phase 1: 需求/验收澄清 / Requirements and acceptance clarification
  -> 行为、边界和测试数据契约 / behavior, boundary, and test-data contract

Phase 2 (可并行 / parallel):
  组件/状态测试设计 / component and state-test design
  API 契约与 mock 核对 / API contract and mock verification

Phase 3: 浏览器关键流程或实现 / browser journeys or implementation
  -> 可执行产物与环境前置条件 / executable artifacts and environment prerequisites

Phase 4: 验证、风险裁决与交付收口 / verification, risk decision, and handoff
```

Remove members without downstream consumers, with duplicated ownership, or without usable dependencies. 删除没有下游消费者、职责重复或依赖不可用的成员。

For a narrow task, keep only the direct capability. 对于窄任务，只保留直接相关能力。

## 步骤 5：协作执行 / Step 5: Collaborative Execution

With formal team primitives, the coordinator creates the team, dispatches by phase, relays cross-member information, and receives member conclusions. 有正式团队原语时，协调者创建团队、按阶段调度、转交跨成员信息并接收成员结论。

Without formal team primitives, follow the same dependency graph and label the mode explicitly; never fake teammate communication. 没有正式团队原语时，按同一依赖图执行并明确标注模式；不得伪造成员通信。

## 步骤 6：最终输出 / Step 6: Final Output

Return the following items: 返回以下内容：

1. Team objective and definition of done. 团队目标和完成标准。
2. Member IDs, skills, selection evidence, responsibilities, and outputs. 成员 ID、Skill、选择证据、职责和产出。
3. Phase parallelism, inputs, outputs, dependencies, and quality gates. 阶段串并行关系、输入、输出、依赖和质量门。
4. Exclusions, assumptions, unverified dependencies, and open questions. 排除项、假设、未验证依赖和开放问题。
5. In execute mode, changed files, commands, results, coverage, and residual risks. 执行模式下的变更文件、命令、结果、覆盖率和残余风险。
