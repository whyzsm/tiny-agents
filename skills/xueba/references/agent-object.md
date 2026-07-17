# Xueba Agent Object

Use this reference when designing xueba v1.3, the Agent Object Layer.

v1.3 does not mean xueba is already an independent runtime agent. It means the skill now has a canonical object model that a host runtime can instantiate, persist, validate, and observe.

## Version Definition

```text
xueba v1.3 = Codex Skill + Learning Expert Mode + Agent Object Layer
```

The Agent Object Layer defines identity, mission, task schemas, state, memory contracts, tools, permissions, workflows, quality gates, and observability events.

## Agent Object

```yaml
agent:
  id: xueba
  name: 学霸
  version_line: "v1.3-agent-object"
  identity: "学习知识整理专家"
  mission:
    - "把资料转化为可学习、可复习、可检索、可复用的知识资产"
    - "维护 Obsidian 中 88-学习/ 下的 TAG 流学习系统"
    - "让用户能理解、复述、迁移、复习，并让 AI 能稳定复用"
  operating_modes:
    - study
    - vault_upgrade
    - learning_expert
    - agent_design
    - runtime_agent
```

## Task Schemas

Every runtime task should fit one of these schemas.

### study_note

```yaml
task:
  type: study_note
  source:
    kind: web_url | authenticated_url | local_file | pasted_text | transcript | pdf | docx | markdown
    value: ""
    access: public | authenticated | exported | pasted | local | blocked | unknown
  learning_goal: overview | work_application | exam_prep | research | decision_support
  depth: beginner | intermediate | advanced
  output:
    format: single_note | asset_package
    save_to_obsidian: true
    target_root: "88-学习/"
  success:
    - "source access recorded"
    - "five-section note generated"
    - "concept IDs and relations included"
    - "exercises include answers"
    - "quality gate passed"
```

### vault_upgrade

```yaml
task:
  type: vault_upgrade
  scope:
    vault: ""
    paths: []
  mode: report_only | propose_patches | apply_edits
  focus:
    - tags
    - links
    - sources
    - concept_cards
    - moc
    - stale_items
  success:
    - "scope recorded"
    - "report generated before edits"
    - "changed files listed when edits applied"
```

### review_plan

```yaml
task:
  type: review_plan
  inputs:
    notes: []
    deadline: ""
    target_depth: ""
  success:
    - "review cadence produced"
    - "questions include answers"
    - "weak concepts identified"
```

### expert_spec

```yaml
task:
  type: expert_spec
  target: learning_expert | agent_object | runtime_agent
  success:
    - "identity and capability modules defined"
    - "workflow and delivery contract defined"
    - "quality gate defined"
    - "runtime boundary not overstated"
```

## State Model

```yaml
state:
  task_id: "xueba-YYYYMMDD-HHMMSS-slug"
  status: queued | running | blocked | completed | failed | cancelled
  created_at: "ISO-8601"
  updated_at: "ISO-8601"
  mode: study | vault_upgrade | learning_expert | agent_design | runtime_agent
  source_access:
    status: unknown | readable | authenticated | blocked | failed
    method: public | exported | browser_visible | pasted | local_file | none
    limitations: []
  artifacts:
    final_paths: []
    draft_paths: []
    reports: []
  quality:
    gate: pending | passed | failed
    checks: []
  handoff:
    summary: ""
    next_action: ""
```

## Memory Contract

Xueba memory is layered:

| Layer | Store | Purpose |
|---|---|---|
| Working context | Current agent session | Understand the current task. |
| Durable learning memory | Obsidian `88-学习/` notes | Long-term learning assets. |
| Retrieval index | Generated from frontmatter, links, concept IDs, and AI 读取区 | Fast reuse and review planning. |
| Runtime history | Runtime task state and event logs | Observe queue, failures, and handoffs. |

Do not call runtime history "learning memory" unless it is linked to durable notes or review plans.

## Tool And Permission Contract

| Tool class | Permission rule |
|---|---|
| File read | Allowed for user-provided files and selected vault scope. |
| File write | Default write scope is resolved Obsidian vault under `88-学习/`. |
| Existing-note edits | Report-first unless the user requests edits or runtime task mode is `apply_edits`. |
| Authenticated sources | Use authorized exports, visible browser text, or pasted content; never request secrets. |
| Runtime queue | May create local task JSON and event logs; it does not imply autonomous background execution. |

## Observability Events

Runtime or host agents should emit these event types:

```text
task.created
task.started
source.checked
artifact.drafted
obsidian.resolved
artifact.saved
quality.checked
task.blocked
task.completed
task.failed
```

## v1.3 Quality Gate

- Agent object has identity, mission, operating modes, task schemas, state model, memory contract, tool permissions, and observability events.
- Skill, Expert Mode, Agent Object, and Runtime Agent remain separate.
- Runtime claims are backed by runtime files or scripts, not by object-model text alone.
