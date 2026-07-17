# Xueba Runtime Agent

Use this reference for xueba v2.0 runtime-agent design and local runtime harness behavior.

## Version Definition

```text
xueba v2.0 = Skill + Learning Expert Mode + Agent Object Layer + Local Runtime Harness
```

In this repository, v2.0 means a local deterministic runtime harness exists for task state, queue files, event logs, and memory-index scaffolding. It does not mean there is already a deployed daemon, cloud service, autonomous scheduler, or always-on background worker.

## Runtime Boundary

The local runtime harness can:

- create task records
- validate task schema
- list queued/running/completed/blocked/failed tasks
- update task status
- append event logs
- create a memory-index scaffold from known Obsidian note metadata
- write all runtime state under a user-chosen runtime directory

The local runtime harness cannot:

- call an LLM by itself
- bypass source access controls
- watch the filesystem continuously unless a separate scheduler runs it
- claim autonomous completion of learning work
- edit Obsidian notes without a host agent or explicit command

## Runtime Directory

Default runtime directory:

```text
.xueba-runtime/
  tasks/
    queued/
    running/
    blocked/
    completed/
    failed/
    cancelled/
  events.jsonl
  memory-index.json
```

Use a project-local or user-provided runtime directory. Do not write runtime state into the Obsidian vault unless the user intentionally chooses that location.

## Task Lifecycle

```text
queued
-> running
-> completed

queued
-> running
-> blocked
-> running
-> completed

queued | running
-> failed | cancelled
```

Every status transition should append an event to `events.jsonl`.

## Task Record

```json
{
  "task_id": "xueba-20260704-120000-study-note",
  "type": "study_note",
  "mode": "study",
  "status": "queued",
  "title": "Agent memory design",
  "source": {
    "kind": "web_url",
    "value": "https://example.com/agent-memory",
    "access": "unknown"
  },
  "output": {
    "target_root": "88-学习/",
    "format": "single_note",
    "final_paths": []
  },
  "quality": {
    "gate": "pending",
    "checks": []
  },
  "created_at": "2026-07-04T12:00:00Z",
  "updated_at": "2026-07-04T12:00:00Z"
}
```

## Runtime Commands

The deterministic local harness is `scripts/xueba_runtime.py`.

```bash
python3 scripts/xueba_runtime.py init --runtime .xueba-runtime
python3 scripts/xueba_runtime.py create --runtime .xueba-runtime --type study_note --title "Agent memory" --source-kind web_url --source-value https://example.com/agent-memory
python3 scripts/xueba_runtime.py list --runtime .xueba-runtime
python3 scripts/xueba_runtime.py update --runtime .xueba-runtime --task-id xueba-... --status running
python3 scripts/xueba_runtime.py event --runtime .xueba-runtime --task-id xueba-... --type quality.checked --message "quality gate passed"
python3 scripts/xueba_runtime.py memory-index --runtime .xueba-runtime --vault /path/to/vault
```

## v2.0 Quality Gate

xueba may be described as having a local runtime harness only when:

- `references/runtime-agent.md` exists
- `scripts/xueba_runtime.py` exists
- `run_evals.py` checks runtime files and task lifecycle phrases
- the runtime script can initialize a runtime directory
- the runtime script can create, list, update, and log a task
- the runtime script can build a memory-index scaffold
- README and SKILL state the runtime boundary accurately

Do not describe xueba as a deployed autonomous agent until a long-running scheduler, permission service, tool executor, monitoring, and deployment lifecycle exist and are verified.
