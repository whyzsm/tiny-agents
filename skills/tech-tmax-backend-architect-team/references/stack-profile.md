# T-MAX Backend Stack Profile

This profile is sanitized and repository-portable. It records common T-MAX patterns, not credentials, hosts, repository URLs, or proof that every service uses every dependency. Confirm the target repository before applying a pattern.

## Common Baseline

- Java 8 and Maven multi-module parent projects.
- Spring Boot 2.1.x in verified services; confirm the exact parent and dependency-management versions.
- Kylin web/API/RPC starters, authentication or user context, and shared response types.
- Spring MVC Controllers, Service interfaces/implementations, optional Manager/domain layers, DAO/Mapper interfaces, and MyBatis XML.
- Druid datasource, MySQL Connector/J, TiDB/MySQL-compatible SQL, PageHelper, and business pagination through `AnePageHelper`.
- Apollo configuration, Nacos discovery/config surfaces, OpenFeign or Kylin RPC, Redis, RabbitMQ, Swagger 2, Log4j2, Lombok, Jackson, Bean Validation, Fastjson, Caffeine, EasyExcel, and UEP export in services that declare them.

## Repository Shape

Expect a parent POM plus one or more application, common, API/Feign, or domain modules. Determine boundaries from the actual `<modules>` and inter-module dependencies.

Typical source surfaces:

```text
controller/
service/ and service/impl/
manager/ or domain/ when present
dao/ or mapper interfaces
resources/**/mapper/*.xml
model/dto, model/query, model/vo, entity or po
feign/ or a dedicated *-feign module
resources/<profile>/bootstrap.yml
```

Do not assume module names or package roots from another T-MAX repository.

## Contract Types And Layering

- Requests commonly use DTO or Query objects and may inherit shared page types.
- HTTP and Feign results commonly use `ResponseResult`.
- Paginated tables commonly use `DataGridResult` and `AnePageHelper`.
- Controller code should validate and delegate; it should not bypass Service boundaries to call DAO/Mapper directly.
- Database entities should not leak through public Controller contracts when a VO is the established boundary.
- Request/response fields must remain aligned across Java types, SQL aliases, resultMap entries, export columns, and client binding.

## MyBatis And TiDB/MySQL

For mapper changes:

1. Identify the driving table in `FROM`; joined or summary tables do not prove the endpoint should return a row.
2. Expand dynamic `<if>`, `<choose>`, collection, organization, date, and status predicates for the concrete request.
3. Keep table aliases explicit after joins.
4. Update the SELECT expression, resultMap, Java field, response model, and export model together when the contract requires all of them.
5. Check nullable values, type conversions, decimal/date precision, grouping, duplicate multiplication, and TiDB/MySQL dialect behavior.
6. Parse changed XML and inspect the final SQL shape before claiming correctness.

For data incidents, separate these questions:

- Does any database row exist?
- Does a row exist in the driving table?
- Does it satisfy every endpoint predicate?
- Do joins, grouping, or result binding remove or alter it?
- Does the response serializer and client read the same field path?

## Pagination

Confirm that `AnePageHelper.startPage(page, pageSize)` or the repository equivalent runs immediately before the intended mapper query. Verify page field names, total/list construction, generic types, and whether any intervening query consumes the pagination context.

Do not infer a correct page response merely because PageHelper is declared in the POM.

## UEP And Excel Export

UEP exports may construct `ExportBaseVo`, provide `choiceColumns`, serialize the query, and reference an existing mapper SQL/resultMap rather than a dedicated export method.

Check:

- Controller export endpoint and export service invocation.
- SQL path, resultMap path, export function name, query serialization, and selected columns.
- Alignment between UI column keys, export VO fields, SQL aliases, and resultMap properties.
- Whether the export engine rewrites the SELECT list.
- Expressions containing commas, including JSON functions and decimal casts, because naive column splitting can corrupt rewritten SQL.
- Real export runtime separately from list-query correctness.

EasyExcel or direct file exports require their own row model, memory/streaming, file-name, content-type, and error-path checks. Do not apply UEP assumptions to them.

## Feign And External Services

Inspect the provider contract or shared API artifact when available. Verify method, path, request wrapper, response wrapper, timeout, retry, fallback, error propagation, configuration placeholders, and version compatibility.

Do not invent a remote endpoint from a client name or configuration key. A declared Feign interface is source evidence, not proof that the provider is deployed or reachable.

## Configuration And Infrastructure

- Inspect the target module's active profile loading and profile-specific `bootstrap.yml` or equivalent.
- Report configuration keys and ownership, not secret values or private hosts.
- Distinguish Apollo configuration, Nacos discovery/configuration, and any legacy registry surface by actual runtime wiring.
- A dependency or configuration block can be unused. Search application code and runtime evidence before claiming Redis, MQ, cache, scheduler, or registry behavior.

## Architecture Questions That Must Be Closed

- Module ownership and allowed dependency directions.
- Transaction boundary and propagation, especially across Service calls.
- Idempotency for imports, exports, retries, messages, jobs, and write APIs.
- TiDB/MySQL compatibility and lock/consistency assumptions.
- Organization and permission filtering.
- Pagination, batch, export, and large-result capacity limits.
- Feign timeout/retry/fallback and partial-failure behavior.
- Cache invalidation, MQ delivery semantics, and replay handling when those components are actually used.
- Logs, metrics, traces, alert ownership, rollback, and compatibility during deployment.
