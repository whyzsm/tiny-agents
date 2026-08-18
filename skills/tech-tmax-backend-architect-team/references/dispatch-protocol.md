# Single-Agent Dispatch Protocol

Use this protocol for every invocation of `tmax-backend-dispatch-agent`. It controls routing, authority, bounded loops, and evidence. Domain details remain in the other references.

## Runtime Invariants

- Execution model: `single-agent-with-rule-package`.
- Concurrency: one Agent and one active track.
- Delegation: disabled. Do not create or simulate child Agents.
- Tracks: internal rule paths executed sequentially by the same Agent.
- Companion Skills: optional in-process guidance, never member identities.

## Task Envelope

Lock this state before mutation:

```yaml
taskId: ""
goal: ""
repository: ""
branch: ""
moduleOrEndpoint: ""
environment: ""
acceptanceCriteria: []
allowedActions: []
forbiddenActions: []
selectedTracks: []
currentTrack: ""
requiredEvidence: []
knownRisks: []
```

If repository, branch, scope, acceptance, or mutation authority is materially ambiguous, keep the task in intake or request direction.

## State Machine

```text
intake -> route -> gate -> track-loop -> review -> verify -> handoff
                     ^          |
                     |--replan--|
```

Only move forward when the current state has an explicit exit condition:

- `intake`: real Git root, branch, worktree state, instructions, target, and evidence limits recorded.
- `route`: smallest sufficient ordered track list selected from `guide.md`.
- `gate`: required actions are authorized; unauthorized actions remain pending or forbidden.
- `track-loop`: current track has met its acceptance condition or produced a named blocker.
- `review`: in-scope correctness, compatibility, security, and regression risks reviewed.
- `verify`: authorized checks run and evidence levels assigned accurately.
- `handoff`: code, runtime, and delivery states reported separately.

## Authority Ledger

Track each authority independently:

```text
source_read
source_edit
static_check
compile
build
test
live_database
live_api
live_mq
live_config
commit
push
deploy
release
```

An allowed action never grants another action. In particular, source editing does not grant build or test authority, and commit does not grant push or deployment authority.

Pause before crossing these gates:

- `design-gate`: breaking contracts, schema changes, new dependencies, new infrastructure, or module-boundary changes.
- `scope-gate`: work expands outside the locked repository, module, endpoint, or behavior.
- `validation-gate`: compile, build, tests, or materially broader checks are not already authorized.
- `live-gate`: database, API, MQ, configuration-center, or production access is needed.
- `delivery-gate`: commit, push, deploy, or release is needed.

Gate outcomes are only `approved`, `denied`, or `pending`. Treat missing authority as `pending`, never as implicit approval.

## Bounded Small Loop

Run this loop inside one active track:

```text
observe -> hypothesize -> plan-one-step -> act -> verify -> decide
```

Rules:

1. Use one falsifiable hypothesis per iteration.
2. Choose one minimal evidence-producing action or one coherent mutation set.
3. Verify the expected result and relevant regression surface immediately.
4. Re-check the diff and worktree after mutation.
5. Record an evidence delta. An iteration without new evidence, a falsified hypothesis, a smaller search space, or a verified change is not progress.
6. Do not repeat the same failed action unchanged.
7. Allow at most three iterations per track by default. Continue beyond three only with explicit progress and a recorded reason.

Choose one decision after every iteration:

- `continue`: evidence improved and the same track remains correct.
- `replan`: the hypothesis was falsified or the required track sequence changed.
- `wait-authority`: the next action crosses a pending gate.
- `blocked`: required evidence is unavailable after distinct bounded attempts.
- `complete`: the track exit condition is proven.

## Evidence Ledger

Append one record per iteration:

```yaml
iteration: 1
track: ""
hypothesis: ""
action: ""
expected: ""
observed: ""
changedFiles: []
validation: []
evidenceLevel: "source_observed"
decision: "continue"
remainingRisk: []
```

Use only the strongest level actually proved:

- `source_observed`
- `static_validated`
- `build_validated`
- `test_validated`
- `runtime_verified`
- `runtime_blocked`
- `delivery_verified`

## Escalation And Exit

Replan or request direction when a missing choice changes a public contract, data model, architecture, external state, or acceptance boundary. Report a blocker when progress requires unavailable environment, data, credentials, dependency state, or authority.

Do not declare completion while a required track, authorized validation, or required handoff field remains open. A valid blocked handoff names the missing input, evidence already collected, attempts made, and the smallest next action that can unblock the task.
