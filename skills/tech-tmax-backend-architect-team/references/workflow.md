---
scene: "T-MAX Java backend"
sub_scene: "architecture-engineering"
tracks:
  - "repo-intake"
  - "architecture-design"
  - "api-data-contract"
  - "implementation-diagnosis"
  - "quality-security-review"
  - "verification-handoff"
source: "repo-adaptation/tech-backend-architect-team+tmax-backend-stack"
---

# T-MAX Backend End-To-End Workflow

Use the full workflow for cross-layer feature work, recurring incidents, significant refactors, architecture decisions, or complete delivery requests. Use the routing table in `guide.md` for focused work.

## Phase 0: Scope And Authority

1. Resolve the exact backend repository and branch.
2. Capture the requested outcome, endpoint/module/data scope, paired consumers, environment, and acceptance boundary.
3. Separate authority for source edits, static checks, compile, tests, live database/API/MQ/config calls, commit, push, deploy, and release.
4. Stop and request direction only when a missing choice would materially change a public contract, data model, architecture, or external state.

Exit when scope and allowed actions are explicit enough to proceed safely.

## Phase 1: Repository Intake

1. Read repository guidance and relevant linked rules.
2. Inspect Git state without disturbing unrelated work.
3. Read parent/module POMs, module layout, application classes, mapper/resource configuration, and relevant tests.
4. Confirm the target service's actual stack instead of copying another service's profile.
5. Record source evidence and unknowns.

Exit with a current-state map and an evidence boundary.

## Phase 2: Contract And Architecture Trace

For endpoint or data work:

1. Trace client request, Controller mapping/validation, Service, Manager/domain, DAO/Mapper, SQL/resultMap, Java models, response wrapper, and export path.
2. Lock field names, types, success/error semantics, page fields, organization filters, date/time behavior, and consumer binding.
3. For missing data, expand all predicates and identify the driving table.

For architecture work:

1. Map module ownership, data ownership, public APIs, Feign calls, transactions, configuration, cache/MQ/job/export dependencies, and failure paths.
2. Evaluate alternatives with `architecture-method.md`.
3. Define compatibility, migration, observability, rollout, and rollback before implementation.

Exit when the proposed change or diagnosis has a complete evidence chain.

## Phase 3: Design Gate

Require explicit confirmation before crossing any of these boundaries when they were not already authorized:

- Breaking API or response changes.
- Schema or data migration.
- New module, service, shared dependency, remote call, queue, cache, or infrastructure component.
- Framework or dependency upgrade.
- Broad refactor beyond the named behavior.
- Production/live environment mutation.

Narrow bug fixes and contract-preserving changes can proceed under implementation authority.

## Phase 4: Implementation Or Diagnosis

1. Preserve repository naming, layering, mapper style, exception conventions, response wrappers, and existing dependency direction.
2. Make the smallest complete change across every required contract surface.
3. Keep Java fields, SQL aliases, resultMap properties, export columns, and client field names aligned.
4. Address error, null, empty, duplicate, timeout, retry, permission, and organization-scope paths relevant to the change.
5. Do not make speculative compatibility fallbacks or unrelated cleanup.
6. Re-check the diff and worktree immediately after edits.

For diagnosis-only requests, stop after proving the strongest supported root cause and remediation. Do not implement without authority.

## Phase 5: Quality And Security Review

Review the final design or diff for:

- Public-contract compatibility and caller impact.
- Transaction, idempotency, concurrency, duplicate-processing, and rollback behavior.
- SQL correctness, join multiplication, null/type/date handling, pagination context, and TiDB/MySQL compatibility.
- Feign timeout/retry/error behavior and partial failure.
- UEP/Excel export query and column consistency.
- Authorization, organization filters, validation, sensitive configuration, logging, and secret exposure.
- Performance, capacity, observability, deployment ordering, and regression surface.

Resolve in-scope critical findings before validation. Report unresolved findings with impact and evidence.

## Phase 6: Verification

1. Select checks from `validation-matrix.md`.
2. Run deterministic static checks by default when they are safe and relevant.
3. Run compile, tests, live calls, or broader checks only within current authority and repository rules.
4. Never use a broader successful check to hide an unavailable business-runtime check.
5. Label every result with the evidence ladder from `guide.md`.

## Phase 7: Handoff

Return:

- Scope and repository state.
- Current-state chain and decision/root cause.
- Changed files or proposed change set.
- Risks, assumptions, and rejected alternatives.
- Validation results and unverified boundaries.
- Runtime, commit, push, deploy, and release status as separate fields.
- Next action only when it follows directly from the remaining evidence gap.

Do not claim completion while a required track or authorized validation session is still running.
