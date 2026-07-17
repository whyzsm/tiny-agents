# 学霸 Eval 断言

Use these assertions when reviewing `evals/evals.json` outputs.

These assertions correspond to `references/quality-gate.md`. The Markdown file is the human-readable review guide; `scripts/run_evals.py` implements the deterministic subset.

## Obsidian Save Assertions

- Final saved note path must be inside a resolved Obsidian vault.
- Final saved note path must include `/88-学习/`.
- Study notes should use the simplified taxonomy:
  - `88-学习/AI/skills/` for Agent Skills, skill creation, skill eval, and skill runtime topics.
  - `88-学习/AI/智能体/` or `88-学习/AI/harness/` for agent architecture and harness topics.
- Final user-facing response must not expose `/private/tmp`, `/tmp`, or other temporary draft paths when the final vault write succeeded.
- The current Codex workspace must not be treated as the Obsidian vault unless it contains `.obsidian` or the user explicitly provides it as the vault.
- If Obsidian is not detected, the workflow must install Obsidian from `https://github.com/obsidianmd/obsidian-releases`, rerun vault resolution, and must not claim a successful Obsidian save before a real vault is resolved.
- A Chinese download-page hint alone is not sufficient for the not-installed case.

## Single Note Assertions

- The note must be one coherent Markdown file unless the user explicitly asks for a multi-file asset package.
- The main headings should be concise and limited to:
  - `## 1. 全景`
  - `## 2. 概念`
  - `## 3. 正文`
  - `## 4. 练习`
  - `## 5. 来源`
- `## 3. 正文` should cover Why / What / How / Limits.
- The note should include learning goals, prerequisite knowledge when relevant, and a topic map.
- When there are multiple reusable concepts, the concept table should include stable concept IDs such as `C001`.
- Source-grounded claims, inferred conclusions, missing content, and uncertain content should be marked with labels such as `原文依据`, `推论`, `待补充`, and `待验证`.
- `## 4. 练习` should include answers, scoring rules, or expected outputs.
- `## 5. 来源` should include source access method, source list, confidence, limitations, an AI-readable YAML area, and quality checks.

## Frontmatter Assertions

- Frontmatter must include:
  - `title`
  - `tags`
  - `source`
  - `created`
- Tags must include:
  - `status/*`
  - `type/system-note`
  - `domain/*`
  - `source/*`
  - `access/*`
  - `confidence/*`

## Authenticated Source Assertions

- Login pages, SSO pages, no-permission pages, and empty app shells must not be summarized as if they were source content.
- If no authorized content can be read, output must use `access/blocked` and explain the next action.
- The output must not ask for passwords, 2FA codes, cookies, bearer tokens, or session storage.
- The output must not print credentials or authorization headers.

## Classification Assertions

- Do not use combined personal directory names such as `AI与智能体` or `产品与需求`.
- Prefer direct subject hierarchy, for example:
  - `AI/skills`
  - `AI/智能体`
  - `AI/RAG`
  - `产品/PRD`
  - `管理/OKR`
- If classification confidence is low, save under `88-学习/待分类/` and mark the domain conservatively.

## Learning Expert Assertions

- Requests to generate a learning expert, expert prompt, or productized xueba workflow should use Learning Expert Mode.
- Learning Expert Mode outputs should include role anchoring, mission, capability precheck, workflow, delivery contract, quality gate, and final handoff.
- Ordinary Study Mode should remain single-expert by default; do not simulate a multi-agent team unless the user explicitly asks for team design.

## Agent Design Assertions

- Requests asking whether xueba is a skill or agent should use Agent Design Mode.
- Agent Design Mode outputs should distinguish Skill, Expert Mode, Agent Object, Local Runtime Harness, Runtime Agent, and Multi-Agent Team.
- The output should state that xueba currently exists as a Codex Skill with Learning Expert Mode, Agent Object Layer, and Local Runtime Harness, but not as an independent deployed self-running runtime agent.
- The output should not claim xueba has an always-on process, scheduler, autonomous model executor, independent permission service, production observability, deployment, or lifecycle unless that runtime has been built and verified.
- Agentization proposals should include identity, mission, task schemas, memory, tools, permissions, scheduler, evaluation, observability, and deployment.

## Agent Object Assertions

- Requests for xueba object modeling should use Agent Design Mode and load `references/agent-object.md`.
- The object definition should include identity, mission, operating modes, task schemas, state model, memory contract, tool and permission contract, observability events, and quality gate.
- Task schemas should cover `study_note`, `vault_upgrade`, `review_plan`, and `expert_spec`.
- State should distinguish `queued`, `running`, `blocked`, `completed`, `failed`, and `cancelled`.
- Memory should distinguish working context, durable Obsidian learning memory, retrieval index, and runtime history.
- Object-layer language must not imply background autonomy by itself.

## Runtime Harness Assertions

- Requests to create, list, update, or inspect xueba runtime tasks should use Runtime Harness Mode.
- Runtime Harness Mode should use `scripts/xueba_runtime.py` for deterministic local task state.
- Runtime command examples should include `init`, `create`, `list`, `update`, `event`, and memory-index scaffolding when relevant.
- Runtime state should live under a chosen runtime directory such as `.xueba-runtime/`, with task status folders, `events.jsonl`, and `memory-index.json`.
- The runtime harness may manage task records, status transitions, event logs, and memory-index scaffolds.
- The runtime harness must not be described as calling an LLM, running forever in the background, bypassing access controls, or autonomously completing learning work.
