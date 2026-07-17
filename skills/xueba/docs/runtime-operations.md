# Xueba Runtime Operations

Use this guide when operating the v2.0 local runtime harness.

## Runtime Boundary

The runtime harness manages local task state. It can create task JSON, move tasks across status folders, append events, and build a memory-index scaffold from Obsidian note metadata.

Do not claim autonomous execution. The harness does not call an LLM, does not run forever in the background, does not bypass source permissions, and does not edit Obsidian notes by itself.

## Initialize

```bash
python3 scripts/xueba_runtime.py init --runtime .xueba-runtime
```

Creates:

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

## Create a task

```bash
python3 scripts/xueba_runtime.py create \
  --runtime .xueba-runtime \
  --type study_note \
  --title "Agent memory" \
  --source-kind web_url \
  --source-value https://example.com/agent-memory
```

Supported task types:

- `study_note`
- `vault_upgrade`
- `review_plan`
- `expert_spec`

## List tasks

```bash
python3 scripts/xueba_runtime.py list --runtime .xueba-runtime
python3 scripts/xueba_runtime.py list --runtime .xueba-runtime --status queued
```

## Start a task

```bash
python3 scripts/xueba_runtime.py update \
  --runtime .xueba-runtime \
  --task-id xueba-... \
  --status running
```

## Complete a task

```bash
python3 scripts/xueba_runtime.py update \
  --runtime .xueba-runtime \
  --task-id xueba-... \
  --status completed \
  --quality-gate passed \
  --final-path "88-学习/AI/智能体/Agent memory.md"
```

## Append an event

```bash
python3 scripts/xueba_runtime.py event \
  --runtime .xueba-runtime \
  --task-id xueba-... \
  --type quality.checked \
  --message "quality gate passed" \
  --data '{"gate":"passed"}'
```

Recommended event types are defined in `references/agent-object.md`.

## Build memory index

```bash
python3 scripts/xueba_runtime.py memory-index \
  --runtime .xueba-runtime \
  --vault /path/to/obsidian-vault
```

The memory index reads Markdown files under `88-学习/`, extracts frontmatter, tags, aliases, concept IDs, and whether the note contains `AI 读取区`.

## Verification

```bash
python3 scripts/run_evals.py --report-dir .xueba-eval-report
```

Expected stable release result:

```text
PASS: 258 passed, 0 failed
```

The report directory contains:

- `summary.json`
- `summary.md`
