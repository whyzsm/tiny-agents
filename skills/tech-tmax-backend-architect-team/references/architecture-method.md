# Architecture Decision Method

Use this method for architecture, cross-module, performance, resilience, dependency, or significant refactor work. Skip irrelevant sections for narrow maintenance.

## 1. Define The Decision

Record:

- Business capability and user-visible outcome.
- Current limitation or failure mode.
- In-scope repositories, modules, data, interfaces, and environments.
- Non-functional constraints: latency, throughput, availability, consistency, security, operability, compatibility, schedule, and rollback.
- Facts, assumptions, unknowns, and explicit non-goals.

Do not start from a preferred pattern such as microservices, caching, MQ, or a new module. Start from the observed problem and constraints.

## 2. Map The Current System

Build the smallest useful map:

```text
caller -> Controller -> Service/domain -> DAO/Mapper -> TiDB/MySQL
                           |
                           +-> Feign/internal service
                           +-> Redis/cache
                           +-> MQ/job/export service
```

Annotate module ownership, public contracts, transaction boundaries, data ownership, synchronous/asynchronous calls, configuration sources, and failure points. Mark every unverified edge.

## 3. Evaluate Options

Compare at least the current-state-preserving option and the proposed option. Add a third option when it reveals a meaningful tradeoff.

| Lens | Questions |
|---|---|
| Correctness | Does the option preserve business invariants, field contracts, organization filters, and error semantics? |
| Coupling | Does it respect module/data ownership and avoid cycles or duplicated sources of truth? |
| Consistency | What transaction, idempotency, retry, ordering, and reconciliation model applies? |
| Performance | What are the query shape, index assumptions, call count, payload size, cache behavior, and capacity limits? |
| Resilience | How do timeout, partial failure, fallback, retry amplification, duplicate messages, and degraded dependencies behave? |
| Compatibility | Can old/new callers and data coexist? Is a migration, feature flag, dual read/write, or rollback path required? |
| Security | Are authorization, organization scope, validation, sensitive configuration, audit, and data exposure handled? |
| Operability | Are logs, metrics, traces, alerts, ownership, runbooks, and runtime proof available? |
| Delivery | What code, data, configuration, dependency, test, deployment, and rollback steps are required? |

Prefer the smallest option that satisfies the constraints. Reject speculative abstractions and dependency upgrades not required by the decision.

## 4. Produce The Target Design

For an accepted option, specify:

- Module and class ownership.
- API method/path, request, response, validation, error, pagination, and compatibility contract.
- Data model, SQL/mapper/resultMap changes, indexes, migration, and rollback.
- Transaction, idempotency, concurrency, retry, timeout, and consistency rules.
- Cache/MQ/Feign behavior only where actual dependencies require them.
- Configuration keys and rollout order without secret values.
- Observability signals and runtime acceptance criteria.
- Static, compile, test, integration, runtime, and delivery evidence required.

## 5. ADR Template

```markdown
# ADR: <decision>

## Status
Proposed | Accepted | Superseded

## Context
- Problem:
- Constraints:
- Current evidence:
- Unknowns:

## Options
### Option A
- Design:
- Benefits:
- Costs/risks:

### Option B
- Design:
- Benefits:
- Costs/risks:

## Decision
- Selected option:
- Why:
- Rejected alternatives:

## Consequences
- API/data/module impact:
- Compatibility and migration:
- Security and operations:
- Rollback:

## Verification
- Static:
- Build/test:
- Integration/runtime:
- Delivery:
```

An ADR is not proof of implementation. Keep decision, implementation, validation, and delivery status separate.
