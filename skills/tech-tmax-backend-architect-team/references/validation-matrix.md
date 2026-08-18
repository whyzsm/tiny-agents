# Validation Matrix And Evaluation Scenarios

## Change-To-Check Matrix

| Change or task | Default static checks | Focused checks when authorized | Runtime evidence required for full claim |
|---|---|---|---|
| Architecture analysis | module/POM/source map, dependency direction, config-key scan | architecture tests or module rules if present | only for claims about deployed topology or behavior |
| Java DTO/VO/entity field | diff check, callers/usages, serializer/validation mapping | targeted module compile and focused tests | real request/response for contract verification |
| Controller/Service behavior | mapping, validation, error path, call chain, diff check | Controller/Service unit or integration tests | real endpoint for business behavior |
| MyBatis Mapper XML | XML parse, SQL/resultMap/Java alignment, dynamic predicate review | focused mapper/service test, targeted compile | real query with named environment/payload for data claims |
| Pagination | helper call order, page fields, result wrapper, intervening-query scan | focused pagination test | real page response for total/list correctness |
| UEP export | Controller, `ExportBaseVo`, columns, query, SQL/resultMap paths, expression risk | targeted compile or export integration test | actual exported job/file for runtime success |
| EasyExcel/direct export | row model, streaming/memory, content type/name, error path | focused export test | generated file inspection with real or representative data |
| Feign integration | client/provider/shared contract, config placeholders, error/fallback path | consumer/provider contract or integration test | reachable deployed dependency in the named environment |
| Apollo/Nacos/profile config | key-only inspection, profile loading, property consumers, secret redaction | targeted startup/config test | active environment value and service registration/config behavior |
| Redis/MQ/cache/job | producer/consumer/cache code and configuration wiring | focused component/integration test | actual delivery, replay, invalidation, or scheduling behavior |
| Delivery | Git diff/status, intended files, commit identity | repository-required tests | remote ref parity; deployment/release require separate platform evidence |

## Evidence Vocabulary

Use only these labels in final status summaries:

| Label | Meaning |
|---|---|
| `source_observed` | Source/configuration was inspected; behavior was not executed. |
| `static_validated` | Deterministic syntax, XML, diff, schema, or static checks passed. |
| `build_validated` | An authorized targeted compile or build passed. |
| `test_validated` | Authorized tests passed at the reported scope. |
| `runtime_verified` | The named real endpoint/data/export/service path succeeded. |
| `runtime_blocked` | Runtime proof was required but unavailable; state the blocker. |
| `delivery_verified` | The exact intended ref is confirmed at every authorized destination. |

## Safe Static Recipes

Use repository-local tools and paths. Examples:

```bash
git status --short --branch
rg -n "endpointOrMethod|mapperId|fieldName" .
xmllint --noout --nonet path/to/Mapper.xml
git -c core.whitespace=cr-at-eol diff --check
```

Do not run Maven builds, service startup, database clients, network calls, commit, or push merely because they appear in a recipe elsewhere.

## Security And Privacy Checks

Before reporting or publishing reusable artifacts:

1. Search changed files for local absolute paths.
2. Search for password, token, key, secret, private-key, signing, Sonar credential, database URL, registry, and internal-host values.
3. Report only the configuration key, file category, purpose, and redacted finding when a credential is discovered.
4. Exclude bootstrap values, logs, environment dumps, Maven credential values, private repository addresses, runtime caches, and local reports from Skill/reference content.
5. Confirm examples use placeholders and repository-relative paths.

## Forward Evaluation Scenarios

Use these prompts to evaluate the Skill without revealing the expected answer. Provide a real or sanitized target repository when available.

### Scenario 1: Endpoint Returns No Data

Prompt: `使用 $tech-tmax-backend-architect-team 排查这个列表接口在指定日期和组织范围内为什么没有数据。`

Pass criteria:

- Resolves the real repository and request payload.
- Traces Controller through SQL/result binding.
- Distinguishes row existence, driving table, predicates, joins, and response binding.
- Does not invent database results or run live queries without authority.

### Scenario 2: Add A List And Export Field

Prompt: `使用 $tech-tmax-backend-architect-team 给这个列表和导出增加一个后端字段，并验证契约。`

Pass criteria:

- Locks the field name/type/source before editing.
- Checks Java models, SQL alias, resultMap, response, export columns/VO, and paired client.
- Selects XML/diff checks and keeps runtime export separate.

### Scenario 3: Pagination Total Is Wrong

Prompt: `使用 $tech-tmax-backend-architect-team 排查分页列表 total 和 list 不一致。`

Pass criteria:

- Checks helper call order and intervening queries.
- Checks grouping/join multiplication and response wrapper fields.
- Requires real request/runtime evidence for a final business claim.

### Scenario 4: UEP Export Fails

Prompt: `使用 $tech-tmax-backend-architect-team 排查列表正常但 UEP 导出失败。`

Pass criteria:

- Finds export Controller and SQL/resultMap paths.
- Reviews rewritten SELECT and comma-containing expressions.
- Does not equate list success with export success.

### Scenario 5: Add A Feign Dependency

Prompt: `使用 $tech-tmax-backend-architect-team 设计并实现一个新的内部 Feign 调用。`

Pass criteria:

- Confirms provider/shared contract and ownership.
- Covers timeout, retry, fallback, errors, compatibility, configuration, and rollout.
- Stops at the design gate for a new external dependency when authority is missing.

### Scenario 6: Configuration Incident

Prompt: `使用 $tech-tmax-backend-architect-team 排查 Apollo/Nacos 配置导致的启动或注册异常。`

Pass criteria:

- Reads key names and loading paths without exposing values.
- Distinguishes dependency/config declaration from active runtime behavior.
- Separates static diagnosis, startup verification, and deployed-environment proof.

### Scenario 7: Architecture Upgrade Request

Prompt: `使用 $tech-tmax-backend-architect-team 评估是否需要拆服务、加缓存或引入 MQ。`

Pass criteria:

- Starts from observed constraints rather than preferred technology.
- Compares current-state-preserving and proposed options.
- Covers data ownership, consistency, failure, capacity, security, observability, migration, and rollback.
- Rejects infrastructure additions that lack a proven need.
