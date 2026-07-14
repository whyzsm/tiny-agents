# 运行时自动编排 / Runtime Orchestration

This reference turns the JSON from `compose_team.py` into an actual coordinated run. It does not install Skills, create avatars, or pretend that a missing team primitive exists. 本参考将 `compose_team.py` 的 JSON 转换为实际的协作执行；不安装 Skill、不创建头像，也不伪造不存在的团队原语。

## 1. Compose / 编排

1. Resolve the assembler Skill directory from the installed Skill file, not from the target project's working directory. 从已安装的 Skill 文件解析编排器目录，不要从目标项目工作目录解析。
2. Run `compose_team.py` with the target root, complete task, mode, and remote catalog URL. 使用目标根目录、完整任务、模式和远端目录 URL 运行 `compose_team.py`。
3. Treat `roster`, `phases`, `handoff`, `prerequisites`, and `runtime` as the dispatch contract. 将 `roster`、`phases`、`handoff`、`prerequisites` 和 `runtime` 视为调度契约。
4. Read the selected router and child `SKILL.md` files completely before sending a member prompt. 发送成员 Prompt 前，完整读取选中的入口和子 `SKILL.md`。
5. Remove a member only when its output has no downstream consumer; record the exclusion in the final report. 只有当成员产出没有下游消费者时才删除成员，并在最终报告中记录排除。

## 2. Formal Team Runtime / 正式团队运行时

When `TeamCreate`, `Agent`, and `SendMessage` are available, the coordinator follows this exact sequence. 当运行时提供 `TeamCreate`、`Agent` 和 `SendMessage` 时，协调者必须按以下顺序执行：

1. The coordinator is the lead. It alone calls `TeamCreate` with a business-specific team name and the task contract. 协调者就是主理人；只能由它使用业务语义明确的团队名和任务契约调用 `TeamCreate`。
2. Create one member per roster item using the exact roster ID and the generated `prompt`. 按 roster 中的准确 ID 和生成的 `prompt` 为每个成员创建一个成员。
3. Give each member only its assigned output, project evidence, mode, and acceptance contract. 每个成员只接收自己的产出、项目证据、执行模式和验收契约。
4. Spawn all members in the same phase in parallel when they have no dependency on one another. 同一阶段且互不依赖的成员并行 spawn。
5. Members return a structured report to the lead through `SendMessage`; the lead relays cross-member facts instead of letting members coordinate directly. 成员通过 `SendMessage` 向主理人回传结构化报告；跨成员事实由主理人中转，不允许成员直接互相协调。
6. The lead waits for every required member in a phase, classifies failures, and unlocks the next phase only after its gate passes. 主理人等待阶段内所有必需成员，分类失败，并在质量门通过后才解锁下一阶段。
7. The lead integrates the reports, applies or reviews code changes according to mode, runs the final verification, and reports residual risks. 主理人集成报告，按模式应用或审查代码变更，执行最终验证并报告残余风险。

The lead must not spawn itself, claim a member result without receiving it, or hide an unverified remote Skill. 主理人不得 spawn 自己、未收到成员结果就声称成员已完成，也不得隐藏未校验的远端 Skill。

## 3. Codex-Compatible Runtime / Codex 兼容运行时

When the runtime exposes Codex-native multi-agent primitives, map the formal protocol as follows. 当运行时提供 Codex 原生多 Agent 原语时，按下表映射正式协议：

| Formal protocol / 正式协议 | Codex-compatible operation / Codex 兼容操作 |
|---|---|
| `Agent` spawn | `spawn_agent` |
| `SendMessage` | `send_input` or the runtime's agent message operation |
| phase wait | `wait_agent` or `wait` |
| resume after review | `resume_agent` then `send_input` |
| close member | `close_agent` |

Use the actual tool names exposed by the current runtime. If these operations are unavailable, do not claim that subagents were spawned. 使用当前运行时实际暴露的工具名；如果这些操作不可用，不得声称已经 spawn 子 Agent。

The no-primitive fallback is coordinated capability execution: the coordinator reads each selected Skill and executes the generated member prompts itself, preserving the same phase order and report schema. 没有原语时，回退为协调式能力执行：协调者读取每个选中 Skill 并自行执行生成的成员 Prompt，但保留相同的阶段顺序和报告结构。

## 4. Member Report / 成员报告

Every member returns this compact contract to the lead. 每个成员向主理人返回以下紧凑契约：

```text
Member ID / 成员 ID:
Owned output / 负责产出:
Confirmed facts / 已确认事实:
Assumptions / 假设:
Findings / 发现:
Files and commands inspected / 检查的文件与命令:
Changes / 变更:
Verification evidence / 验证证据:
Blockers and environment gaps / 阻塞与环境缺口:
Handoff to lead / 给主理人的交接:
```

An execution member may edit only the files required by its assignment and must report exact paths. 执行成员只能修改职责所需文件，并必须报告准确路径。

## 5. Phase Gates / 阶段质量门

- Contract gate: scope, acceptance criteria, data, and unresolved questions are explicit. 契约门：范围、验收标准、数据和未决问题明确。
- Plan gate: affected paths, dependencies, rollback or containment, and verification route are explicit. 方案门：受影响路径、依赖、回滚或隔离措施和验证路径明确。
- Validation gate: each failure is classified as product defect, test defect, environment blocker, or data issue. 验证门：每个失败归类为产品缺陷、测试缺陷、环境阻塞或数据问题。
- Handoff gate: changed files, commands, results, residual risks, and next actions are recorded. 交付门：记录变更文件、命令、结果、残余风险和后续动作。

## 6. Safety / 安全边界

The composer is read-only. Package mode may write requested text manifests or Agent prompts, but it must never write to the target project unless the user explicitly requests implementation. 编排器是只读的；团队包模式可以写用户要求的文本 manifest 或 Agent Prompt，但除非用户明确要求实现，否则不得写入目标项目。

Remote Skills remain remote references. A source marked `unverified` is a prerequisite to check, not evidence that the capability was executed. 远端 Skill 保持为远程引用；标记为 `unverified` 的源只是待核对前置条件，不是能力已执行的证据。

Avatar resources are omitted by design. 头像资源按设计省略。
