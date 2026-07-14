# 团队选择模型 / Team Selection Model

Use this model for multi-domain, ambiguous, or high-risk requests. 对于多领域、存在歧义或高风险请求使用本模型。

Keep the final team as small as the work allows. 在满足工作的前提下保持最终团队尽可能精简。

## 目录 / Contents

1. Derive capability slots / 推导能力槽位
2. Score shortlisted skills / 对候选 Skill 评分
3. Apply composition rules / 应用组合规则
4. Build the dependency graph / 构建依赖图
5. Define handoff contracts / 定义交接契约
6. Compare example decisions / 对比示例决策
7. Prune the final roster / 裁剪最终成员

## 1. 推导能力槽位 / Derive Capability Slots

Create slots from required outputs and gates, not from generic software job titles. 根据必需产出和质量门创建槽位，不要按通用软件职位堆角色。

| 证据 / Evidence | 添加槽位 / Add a slot for | 典型产出 / Typical owned output |
|---|---|---|
| 目标、范围、行为或验收未确定 / Goal, scope, behavior, or acceptance is unresolved | 需求澄清 / Requirement clarification | 可决策的需求和验收标准 / Decision-ready requirements and acceptance criteria |
| 变更跨越模块、服务、数据或部署边界 / Change crosses module, service, data, or deployment boundaries | 架构 / Architecture | 设计决策、接口和迁移路径 / Design decision, interfaces, and migration path |
| 必须修改代码或配置 / Code or configuration must change | 实现 / Implementation | 符合仓库规范的工作变更 / Working change aligned with repository conventions |
| 行为改变或存在回归风险 / Behavior changes or regression risk exists | 测试 / Testing | 测试策略、测试代码和执行证据 / Test strategy, test code, and execution evidence |
| 涉及认证、密钥、支付、个人数据或信任边界 / Auth, secrets, payments, personal data, or trust boundaries change | 安全与隐私 / Security and privacy | 威胁发现及阻断/非阻断结论 / Threat findings and blocking/non-blocking verdict |
| 面向用户的 UI 发生变化 / User-facing UI changes | UX 与无障碍 / UX and accessibility | 交互方案与 WCAG 验收证据 / Interaction and WCAG acceptance evidence |
| 公开 API、运维或交接发生变化 / Public API, operations, or handoff changes | 文档与运维 / Documentation and operations | 更新后的契约、运行手册或发布门 / Updated contract, runbook, or release gate |

Merge slots when one Skill clearly owns both outputs and separation creates no independent quality gate. 当一个 Skill 明确同时负责两个产出且拆分不会形成独立质量门时合并槽位。

Keep slots separate when one member must independently review another. 如果一个成员必须独立审查另一个成员，则保留分离槽位。

## 2. 对候选 Skill 评分 / Score Shortlisted Skills

Shortlist team entries from `https://github.com/whyzsm/tiny-agents/tree/main/indexes`. 从远端索引中筛选专家团入口。

Read each shortlisted router and considered child Skill's complete remote `SKILL.md`, then score it. 完整读取入选入口及候选子 Skill 的远端 `SKILL.md` 后再评分。

| 因素 / Factor | 分值 / Score | 判断问题 / Question |
|---|---:|---|
| 项目适配度 / Project fit | 0 to 3 | 是否支持检测到的技术栈、框架和仓库规范？ / Does it support the detected stack, framework, and repository conventions? |
| 任务适配度 / Task fit | 0 to 3 | 触发条件和流程是否直接覆盖能力槽位？ / Do its trigger and workflow directly cover the required slot? |
| 产出适配度 / Output fit | 0 to 2 | 是否能产出下游需要的工件或结论？ / Does it produce the artifact or verdict consumed downstream? |
| 验证适配度 / Verification fit | 0 to 2 | 能否使用项目真实工具验证成功？ / Can it verify success with the project's real tools? |
| 能力重叠 / Capability overlap | 0 to -2 | 其他已选 Skill 是否已经负责相同结果？ / Does another selected Skill already own the same result? |
| 不可用依赖 / Unavailable dependency | 0 to -3 | 是否依赖不可用的工具、服务、凭据或运行时？ / Does it require an unavailable tool, service, credential, or runtime? |

Prefer the highest-scoring candidate per slot. 每个槽位优先选择得分最高的候选。

Treat a total below 6 as a weak fit and disclose the gap instead of disguising it with a role name. 总分低于 6 视为适配较弱，应披露缺口，不要用角色名称掩盖问题。

## 3. 应用组合规则 / Apply Composition Rules

1. Select capabilities before naming members. 先选择能力，再命名成员。
2. Keep one accountable owner per artifact or verdict. 每个产出或结论只设一个负责成员。
3. Use a separate reviewer only when independence is meaningful. 只有独立性有实际意义时才增加审查者。
4. Prefer a narrow child Skill declared by the shortlisted entry over its broad `*-team` router. 优先使用入选入口声明的窄子 Skill，而不是宽泛的 `*-team` router。
5. Use an existing team router only when it matches the project, outputs, and gates with little modification. 只有现有团队入口几乎无需改造即可匹配项目、产出和质量门时才直接使用它。
6. Reject candidates whose workflow conflicts with repository instructions. 淘汰与仓库规则冲突的候选。
7. Reject candidates whose output has no downstream consumer. 淘汰没有下游消费者的候选。
8. Do not add research, manager, or reviewer roles as decoration. 不要为了装饰增加“研究”“经理”或“审查”角色。

## 4. 构建依赖图 / Build The Dependency Graph

Use parallel phases only when members do not need one another's pending output. 只有成员不依赖彼此尚未完成的输出时，才能并行。

```text
Phase 1: 需求澄清 / requirement clarification
  -> 已批准的行为与验收标准 / approved behavior and acceptance criteria

Phase 2 (经 Phase 1 后并行 / parallel after Phase 1):
  架构/实现规划 / architecture and implementation planning
  测试策略与 fixture 规划 / test strategy and fixture planning

Phase 3: 实现 / implementation
  -> 变更产物 / changed artifacts

Phase 4 (经 Phase 3 后并行 / parallel after Phase 3):
  定向测试 / targeted tests
  条件式安全/无障碍审查 / conditional security and accessibility review

Phase 5: 协调者集成与最终验证 / coordinator integration and final verification
```

Skip phases without required outputs. 没有必需产出的阶段直接跳过。

For a narrow regression fix, debugging plus testing may be the entire team. 对于窄范围回归修复，调试加测试可能就是完整团队。

## 5. 交接契约 / Handoff Contract

For every edge in the graph, record the following. 为依赖图中的每条边记录以下内容：

- Producer and consumer member IDs. 生产者和消费者成员 ID。
- Exact artifact or conclusion transferred. 传递的确切产物或结论。
- Assumptions and unresolved questions. 假设和未解决问题。
- Evidence expected by the consumer. 消费者需要的证据。
- Rejection or retry condition. 拒绝或重试条件。

A phase is complete only when its consumer can proceed without reconstructing hidden context. 只有消费者无需重建隐藏上下文即可继续时，阶段才算完成。

## 6. 示例决策 / Example Decisions

### 不清晰功能且要求测试 / Unclear Feature With Test Requirements

Select requirement clarification first. 首先选择需求澄清。

Add implementation only after behavior and acceptance criteria are settled. 行为和验收标准确定后再加入实现。

Add unit/integration or E2E testing according to the affected boundary. 根据受影响边界加入单元/集成或 E2E 测试。

Do not add architecture unless the feature crosses a meaningful system boundary. 除非功能跨越有意义的系统边界，否则不要加入架构角色。

### 独立回归 / Isolated Regression

Select debugging and the repository-compatible test Skill. 选择调试能力和与仓库兼容的测试 Skill。

Omit product, architecture, and release roles unless evidence reveals broader impact. 除非证据显示影响更广，否则省略产品、架构和发布角色。

### 认证迁移 / Authentication Migration

Select requirements/specification, architecture or migration, implementation, security/privacy, and integration/E2E testing. 选择需求/规格、架构或迁移、实现、安全/隐私和集成/E2E 测试能力。

Keep security independent from implementation because it owns a release verdict. 安全角色应独立于实现角色，因为它负责发布结论。

## 7. 最终裁剪问题 / Final Pruning Questions

Before accepting the roster, ask the following. 接受成员清单前逐项回答：

- What breaks if this member is removed? 移除该成员会导致什么缺口？
- Which exact output does this member own? 该成员具体负责哪个产出？
- Who consumes that output? 谁消费该产出？
- Is another selected Skill already producing it? 是否已有其他 Skill 产出相同内容？
- Can this member operate with available tools and project evidence? 该成员是否能使用现有工具和项目证据工作？

Remove any member without concrete answers. 无法给出具体答案的成员应移除。
