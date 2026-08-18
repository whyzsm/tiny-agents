# T-MAX 后端架构专家团使用指南

## Routing Table

| Request | Required tracks | Primary evidence |
|---|---|---|
| 技术栈或架构分析 | `repo-intake` -> `architecture-design` -> `verification-handoff` | parent/module POM, application classes, package/module graph, config keys |
| 新增或修改接口 | `repo-intake` -> `api-data-contract` -> `implementation-diagnosis` -> `verification-handoff` | Controller, Service, DAO, Mapper XML, models, tests, paired client contract |
| 接口无数据或字段不对 | `repo-intake` -> `api-data-contract` -> `implementation-diagnosis` | request payload, predicates, driving table, joins, resultMap, response binding |
| 分页异常 | `api-data-contract` -> `implementation-diagnosis` -> `verification-handoff` | `AnePageHelper.startPage`, mapper call order, `DataGridResult`, page fields |
| UEP 或 Excel 导出 | `api-data-contract` -> `implementation-diagnosis` -> `quality-security-review` | export Controller, `ExportBaseVo`, `choiceColumns`, SQL/resultMap paths, export VO |
| Feign 或外部依赖 | `repo-intake` -> `architecture-design` -> `api-data-contract` | client interface, provider contract, configuration placeholders, fallback/error path |
| Apollo/Nacos/profile 配置 | `repo-intake` -> `quality-security-review` -> `verification-handoff` | profile config keys, POM, application/bootstrap loading, runtime evidence if authorized |
| 性能、容量、高可用 | `architecture-design` -> `quality-security-review` | query plan evidence, call graph, cache/MQ behavior, retry/timeout, capacity assumptions |
| 代码或架构评审 | `repo-intake` -> relevant design/contract track -> `quality-security-review` | diff, repository rules, callers, tests, configuration, migration and rollout impact |
| 完整需求交付 | all tracks in `references/workflow.md` | requirements, code chain, validation evidence, delivery boundary |

Use only the smallest track set that can answer the request. A focused mapper issue does not require a full architecture package. A cross-module or public-contract change does.

## Repository Intake Checklist

Collect evidence in this order:

1. Resolve the target Git root. Do not run Git commands from an outer frontend or workspace container.
2. Read repository instructions and task-relevant linked rules.
3. Record branch, upstream, dirty state, and whether concurrent changes overlap the task.
4. Inspect the root and module POMs, declared modules, Java level, parent framework version, and internal starters.
5. Locate application classes, mapper scanning, resource profiles, mapper XML directories, and tests.
6. For API work, search the exact URL suffix or method name and trace the full contract chain.
7. For paired frontend work, inspect the real service request and response binding without treating the frontend model as backend authority.
8. Record what was observed, inferred, unavailable, or blocked before proposing changes.

## Contract Trace

Trace API and data behavior in this order when each layer exists:

```text
client request
  -> Controller mapping and validation
  -> Service interface and implementation
  -> Manager/domain orchestration
  -> DAO/Mapper interface
  -> MyBatis XML SQL and resultMap
  -> PO/DTO/Query/VO/export VO
  -> ResponseResult/DataGridResult or Feign response
```

For every request and response field, record its source-of-truth name, type, optionality, transformation, SQL alias, resultMap binding, and consumer. Do not add compatibility aliases without a confirmed contract need.

## Evidence Ladder

Use the strongest status actually proved:

- `source_observed`: the relevant source/configuration was inspected.
- `static_validated`: syntax, XML, diff, schema, or deterministic static checks passed.
- `build_validated`: an authorized targeted compile or build passed.
- `test_validated`: authorized focused or broader tests passed.
- `runtime_verified`: the real endpoint, export, data path, or service behavior succeeded in the named environment.
- `runtime_blocked`: runtime proof was required but unavailable because of environment, auth, data, dependency, or authority.
- `delivery_verified`: the intended commit/ref is confirmed at every authorized remote target.

Never collapse these statuses into a single `done` claim.

## Decision Gates

- **Design gate**: confirm breaking contracts, module boundaries, new dependencies, schema changes, and migrations before implementation.
- **Data gate**: require the concrete environment, date range, organization scope, and payload before concluding data is absent or wrong.
- **Validation gate**: do not run broad tests or builds merely because a change exists; follow repository rules and current authority.
- **Live gate**: database/API/MQ/config-center access requires the correct environment and explicit scope.
- **Delivery gate**: commit, push, deploy, and release are separate actions and are never inferred from implementation authority.

## Response Template

```markdown
# T-MAX 后端任务结果

## 范围与证据
- 仓库/分支：
- 目标接口或模块：
- 已读取规则：
- 证据边界：

## 当前链路
- 请求入口：
- Service/DAO/Mapper：
- 数据、分页、导出或外部依赖：
- 响应绑定：

## 结论或变更
- 根因/架构决策：
- 变更文件：
- 未采用方案及原因：

## 风险
- 兼容性/事务/幂等：
- 性能/安全/配置：
- 发布与回滚：

## 验证与交付状态
- source_observed：
- static_validated：
- build/test/runtime：
- commit/push/deploy：
- 剩余阻塞：
```
