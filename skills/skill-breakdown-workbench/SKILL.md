---
name: skill-breakdown-workbench
description: "Analyze Codex Skills and agent manifests. Use when the user wants to拆解 a Skill, explain how a Skill or agent is written, or learn how to write one with bilingual Chinese/English guidance, especially when the target is an existing SKILL.md or agents/openai.yaml."
---

# Skill 拆解工作台

## Overview

This skill turns a target Skill or agent manifest into a bilingual teardown and a writing lesson. It explains what the artifact does, how it is structured, and how to write a stronger version without inventing hidden behavior.

## When to Read References

Read `references/guide.md` when the user asks for:

- a full Skill-vs-agent comparison
- a reusable writing template
- a rewrite or improvement plan
- a stricter checklist for authoring or reviewing a package

## Triggers

- “拆解这个 skill 是怎么写的”
- “帮我分析这个 agent manifest，并教我怎么写”
- “Break down this Skill and show me how it is written”
- “Teach me how to write a better Skill and agent from this example”

## Workflow

1. Identify the target artifact: Skill, agent manifest, or both.
2. Read only visible files and treat `SKILL.md`, `agents/openai.yaml`, and linked references as the source of truth.
3. Explain the artifact in paired Chinese/English sections:
   - 结论 / Verdict
   - 结构拆解 / Structure Breakdown
   - Skill 写作法 / Skill Writing
   - Agent 写作法 / Agent Writing
   - 可复用模板 / Reusable Template
4. Turn the analysis into concrete lessons: triggers, boundaries, references, workflow, and validation.
5. If the user wants a rewrite, keep the original capability and boundary, then produce a draft or patch instead of a generic summary.
6. If the task is only review or explanation, do not install, publish, commit, or push anything.
7. If the task edits files, verify that every claim and every recommendation maps back to the visible text.

## Guardrails

- Do not guess hidden prompts, private APIs, or unpublished files.
- Do not turn a Skill into a persona or soul statement.
- Keep the boundary clear: Skills describe capability and workflow; agents describe entry behavior and invocation details.
- Do not claim installation, publication, or execution unless it actually happened.
- Do not introduce secrets, local absolute paths, or external side effects without explicit permission.

## Validation

- For analysis, check that each conclusion is grounded in visible content.
- For authoring, validate `SKILL.md`, `agents/openai.yaml`, and any references before handing off.
- When files change, run the repository's structural checks and a path/secret scan before delivery.
