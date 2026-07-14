# 项目专家团编排器 / Project Expert-Team Assembler

`$assemble-project-expert-team` is a project-quality dynamic expert-team entry point. `$assemble-project-expert-team` 是项目质量类动态专家团入口。

It separates target-project evidence from the remote expert capability catalog; the target can be any repository and does not need a local `tiny-agents` checkout. 它将目标项目证据与远端专家能力目录分开处理；目标项目可以是任意代码仓库，不要求本地存在 `tiny-agents`。

## 来源与边界 / Source And Boundaries

- Capability catalog / 能力目录: `https://github.com/whyzsm/tiny-agents/tree/main/indexes`
- Catalog file / 目录文件: `expert-team-file-list.md`
- Target project / 目标项目: the repository the user asks to inspect or deliver / 用户要求检查或交付的代码仓库
- Skill directory / Skill 目录: the installed directory containing this skill's script and rules / 包含本 Skill 脚本和规则的已安装目录

Do not treat the target project as the capability catalog. 不要把目标项目当作能力目录。

Do not scan or install a complete external skill collection merely because the target project lacks `tiny-agents`. 不要因为目标项目没有 `tiny-agents` 就扫描或安装整套外部技能。

## 模式 / Modes

### Blueprint / 蓝图

Use when the user asks to assemble a team, design collaboration, or decide who should participate. 用户要求“组专家团”“设计协作方案”或“判断谁参与”时使用。

Return only a team contract; do not modify the target project, install skills, or perform destructive actions. 只返回团队契约；不要修改目标项目、安装 Skill 或执行破坏性操作。

### Execute / 执行

Use when the user explicitly asks the team to implement, test, review, or deliver. 用户明确要求团队实现、测试、审查或交付时使用。

Compose the team first, then execute by phase. 先完成编排，再按阶段执行。

When formal team primitives exist, the coordinator creates and dispatches the team. 有正式团队原语时，由协调者创建并调度团队。

When they do not exist, never claim that teammates were spawned; label the result as coordinated capability execution. 没有正式团队原语时，不得声称已经 spawn teammate，应标记为协调式能力执行。

### Package / 团队包

Use only when the user asks to persist a reusable team, router, or formal plugin. 只有用户要求沉淀可复用团队、router 或正式 plugin 时使用。

Read `references/team-package-spec.md` first and write only the requested package. 先读取 `references/team-package-spec.md`，只写用户要求的团队包，不复制已有 Skill。

## 远端目录读取 / Remote Catalog Reading

Resolve the script path relative to this file's skill directory, never relative to the target project's current working directory. 从本文件所在 Skill 目录解析脚本路径，不要以目标项目当前工作目录为基准。

```bash
python3 <assemble-project-expert-team-dir>/scripts/discover_skills.py \
  --query "<target project, task, stack, risks, deliverable>" \
  --limit 20
```

The script converts the GitHub `tree` address to the raw `expert-team-file-list.md`, reads only the index, and does not cache or bulk-download all skills. 脚本将 GitHub `tree` 地址转换为 raw `expert-team-file-list.md`，只读取索引，不缓存或批量下载所有 Skill。

It returns expert-team entries, declared child skills, and raw source addresses. 它返回专家团入口、声明的子技能和 raw 源地址。

The remote flow works without a local `tiny-agents` checkout. 远端流程不要求本地存在 `tiny-agents`。

Use a local offline catalog only when the user explicitly requests it or provides a local copy. 只有用户明确要求离线或提供本地副本时，才使用本地目录。

```bash
python3 <assemble-project-expert-team-dir>/scripts/discover_skills.py \
  --catalog-root <catalog-repository> \
  --index indexes/expert-team-file-list.md \
  --query "<task>"
```

## 项目证据 / Project Evidence

Read evidence from low risk to high risk. 按风险从低到高读取证据：

1. `AGENTS.md` and local repository constraints. `AGENTS.md` 与仓库本地约束。
2. Language, framework, build, test, and CI configuration. 语言、框架、构建、测试和 CI 配置。
3. Affected routes, entry points, services, state models, tests, and mocks. 受影响的路由、入口、服务、状态模型、测试和 mock。
4. Deliverables, acceptance criteria, permissions, data, and environment constraints. 交付物、验收条件、权限、数据和环境约束。

Separate confirmed facts, reasonable assumptions, and unresolved questions. 区分已确认事实、合理假设和待确认问题。

Ask only questions that can change team composition, safety, or execution feasibility. 只询问会改变团队组成、安全性或执行可行性的问题。

## 候选读取与选择 / Candidate Reading And Selection

1. Select relevant expert-team entries from the index; do not infer capability from names alone. 从索引选择相关专家团入口，不要只根据名称推断能力。
2. Read each shortlisted router `SKILL.md` completely. 完整读取每个入选入口的 `SKILL.md`。
3. Read only the child skill `SKILL.md` files being compared; verify complete HTTP content and matching frontmatter `name`. 只读取正在比较的子 Skill `SKILL.md`，确认 HTTP 内容完整且 frontmatter 的 `name` 匹配。
4. Prefer narrow capabilities with real paths, usable dependencies, and downstream-consumable outputs. 优先选择路径真实、依赖可用且输出有下游消费者的窄能力。
5. Default to two to five members, with one primary output or quality gate per member. 默认选择 2-5 名成员，每名成员负责一个主要产出或质量门。
6. Add requirements clarification when scope or acceptance is unclear; add testing for behavior changes or requested evidence. 范围或验收不清时加入需求澄清；行为变化或用户要求证据时加入测试。
7. Add architecture, security, accessibility, data, operations, or documentation only when project evidence requires the gate. 只有项目证据要求时，才加入架构、安全、无障碍、数据、运维或文档角色。
8. Do not claim execution for an unverified remote child skill. 未验证的远端子 Skill 不得直接宣称已执行。

Record missing runners, credentials, test data, or service URLs as execution prerequisites. 将缺少的 runner、凭据、测试数据或服务地址记录为执行前置条件。

For complex work, read `references/selection-model.md`, score candidates, and explain rejected candidates in the final report. 复杂任务读取 `references/selection-model.md`，对候选评分，并在最终报告中解释淘汰项。
