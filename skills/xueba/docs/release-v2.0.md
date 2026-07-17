# xueba v2.0 Release Note

Release date: 2026-07-09

## Release Boundary

xueba v2.0 is:

```text
Codex Skill + Learning Expert Mode + Agent Object Layer + Local Runtime Harness
```

xueba v2.0 is not a deployed autonomous agent. It has no always-on daemon, autonomous scheduler, model executor, independent permission service, cloud deployment, or production lifecycle manager.

## What Changed

- Added `VERSION` with `2.0.0`.
- Added `CHANGELOG.md`.
- Added `references/agent-object.md`.
- Added `references/runtime-agent.md`.
- Added `scripts/xueba_runtime.py`.
- Added `docs/runtime-operations.md`.
- Added `docs/model-eval-workflow.md`.
- Added `scripts/prepare_model_eval_workspace.py`.
- Added SKILL-level safety checkpoints and anti-pattern boundaries.
- Expanded `scripts/run_evals.py` to validate release docs and write eval reports.
- Expanded eval coverage to include Agent Object Layer and Runtime Harness Mode.

## Verification Commands

Run from the skill root:

```bash
python3 scripts/run_evals.py --report-dir .xueba-eval-report
python3 scripts/prepare_model_eval_workspace.py --workspace ../xueba-workspace
python3 -m py_compile scripts/*.py
python3 - <<'PY'
import json
from pathlib import Path
for p in ['evals/evals.json', 'evals/cases.json', 'evals/trigger-evals.json']:
    json.loads(Path(p).read_text(encoding='utf-8'))
    print(p, 'ok')
PY
git diff --check
```

Expected deterministic eval result:

```text
PASS: 258 passed, 0 failed
```

## Runtime Smoke Coverage

`scripts/run_evals.py` now verifies that the runtime harness can:

- initialize runtime directories
- create a `study_note` task
- list created tasks
- move a task to `running`
- move a task to `completed`
- record a passed quality gate
- append `quality.checked`
- build a memory-index scaffold from an Obsidian-like vault

## Known Non-Goals

- No autonomous LLM execution.
- No background daemon.
- No filesystem watcher.
- No production scheduler.
- No independent permission service.
- No deployment lifecycle or rollback system beyond git.

## Release Checklist

- [x] Skill metadata identifies v2.0.
- [x] Runtime references exist.
- [x] Runtime script exists.
- [x] Release docs exist.
- [x] Model-output eval workspace generator exists.
- [x] Safety checkpoints and anti-pattern boundaries are checked.
- [x] Deterministic eval passes.
- [x] Installed local skill can be synced and checked with the same eval runner.
- [ ] Model-output comparison and human review viewer should be run before calling a future release behaviorally stable.
