# Changelog

## 2.0.0

Release date: 2026-07-09

This release promotes xueba to the local runtime harness line:

- Adds the v1.3 Agent Object Layer in `references/agent-object.md`.
- Adds the v2.0 Local Runtime Harness boundary in `references/runtime-agent.md`.
- Adds `scripts/xueba_runtime.py` for deterministic local task records, status transitions, event logs, and memory-index scaffolds.
- Extends `scripts/run_evals.py` with runtime smoke checks and report output.
- Adds `scripts/prepare_model_eval_workspace.py` and `docs/model-eval-workflow.md` for real model-output review setup.
- Adds SKILL-level safety checkpoints and anti-pattern boundaries for vault edits, authenticated sources, Obsidian persistence, and runtime autonomy claims.
- Expands eval coverage to 13 output cases and 22 trigger-boundary prompts.
- Documents that xueba is not a deployed autonomous agent, daemon, cloud service, scheduler, model executor, or independent permission service.

## 1.3.0

- Defines xueba as a Skill + Learning Expert Mode + Agent Object Layer.
- Adds task schemas, state model, memory contract, tool permissions, observability events, and quality gate.
- Preserves the boundary between Skill, Expert Mode, Agent Object, Runtime Harness, Runtime Agent, and Multi-Agent Team.

## 1.2.0

- Stabilizes Learning Expert Mode.
- Adds expert personality, expert capabilities, note template, and quality gate references.
- Establishes the five-section study note standard: 全景, 概念, 正文, 练习, 来源.
- Adds deterministic eval scaffolding for skill structure and generated notes.
