# Skill 与 Agent 写作指南 / Skill and Agent Writing Guide

## 核心区别 / Core Distinction

| 组件 / Component | 作用 / Role | 写作重点 / Writing Focus |
|---|---|---|
| Skill | 能力包与工作流 / capability package and workflow | 触发条件、边界、流程、验证 / triggers, boundaries, workflow, validation |
| Agent manifest | UI/调用入口 / entry prompt and config | `display_name`、`short_description`、`default_prompt`、`policy` / UI name, summary, prompt, policy |

## 分析维度 / Analysis Dimensions

### Skill

- `name`：短、清楚、hyphen-case。
- `description`：一句话说清能力和触发场景。
- `Triggers`：写真实自然语言例句，不写抽象标签。
- `Overview`：解释这是什么，不要写人格。
- `Workflow`：按顺序写发现、执行、验证、交付。
- `Guardrails`：说明边界、外部副作用和禁止项。
- `References`：把长知识放到一层引用里。
- `Validation`：说明如何证明结果可靠。

### Agent

- `display_name`：给人看的名字，简短明确。
- `short_description`：一行说明它做什么。
- `default_prompt`：显式调用对应 skill，并保持边界一致。
- `policy`：只写必要策略，不塞进隐藏 persona。

## 怎么写得更好 / How to Write Better

- 写能力，不写人设 / describe capability, not identity.
- 写可触发请求，不写抽象标签 / use natural-language triggers, not labels.
- 写命令式流程，不写散文 / use imperative workflow steps, not prose.
- 写边界，不写模糊承诺 / state boundaries clearly.
- 写验证，不写“应该可以” / make validation observable.
- 写引用，不把长内容塞进主文件 / move long material into references.
- 对齐 Skill 和 Agent 的命名与职责 / keep the Skill and Agent aligned.

## 可复用回答模板 / Reusable Answer Template

1. 它是做什么的 / What it does.
2. 它是怎么写的 / How it is written.
3. 哪些地方写得好 / What is already strong.
4. 哪些地方可以改 / What to improve.
5. 一个可复用骨架 / A reusable skeleton.

## 常见错误 / Common Mistakes

- 把 Skill 写成角色扮演 / turning a Skill into role-play.
- 把 Agent 写成另一个 Skill / turning the Agent into a duplicate Skill.
- 忽略验证和副作用 / omitting validation and side effects.
- 默认假设隐藏 prompt / assuming hidden prompts or private files.
- 中英文不对齐 / letting the Chinese and English sections drift apart.

## 推荐输出顺序 / Recommended Output Order

1. 结论 / Verdict
2. 结构拆解 / Structure Breakdown
3. Skill 写作建议 / Skill Writing Advice
4. Agent 写作建议 / Agent Writing Advice
5. 可直接复用模板 / Reusable Template

## 可复用骨架 / Reusable Skeleton

### Skill / SKILL.md

```markdown
---
name: example-skill
description: "Do X. Use when ..."
---

# Title

## Overview
...

## Triggers
- "..."

## Workflow
1. ...

## Guardrails
- ...

## Validation
- ...
```

### Agent manifest / agents/openai.yaml

```yaml
interface:
  display_name: "Example Skill"
  short_description: "One-line summary"
  default_prompt: "Use $example-skill to ..."
policy:
  allow_implicit_invocation: true
```
