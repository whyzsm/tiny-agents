# Skill Contract

Use this contract to turn an idea into a Skill package without adding persona or
unbounded automation.

## Blueprint

```yaml
name: example-skill
purpose: One sentence describing the capability
triggers:
  - User asks for a concrete task
inputs:
  - Files, text, project state, or user decisions
outputs:
  - Files, commands, or a decision with evidence
workflow:
  - Inspect context
  - Execute the smallest valid change
  - Validate the result
guardrails:
  - Ask before destructive or external side effects
validation:
  - Structural validator
  - Relevant unit or integration tests
```

## Package Contract

| File | Requirement |
|---|---|
| `SKILL.md` | Valid frontmatter with `name` and `description`; imperative workflow; no TODOs or persona. |
| `agents/openai.yaml` | Quoted UI fields; matching name in `$default_prompt`; no unrequested dependencies. |
| `references/` | Only detailed material loaded conditionally from `SKILL.md`. |
| `scripts/` | Deterministic helpers with explicit arguments, safe failure, and tests. |
| `assets/` | Only files copied or consumed by the generated output. |
| `source.json` | Optional sanitized provenance with relative or public paths only. |

## Description Formula

Use this shape for frontmatter descriptions:

```text
[Verb] [capability]. Use when [trigger 1], [trigger 2], or [trigger 3], especially when [important boundary or file type].
```

The description is the primary trigger. Do not hide trigger conditions in a
body section called "When to use".

## Decision Rules

- Reuse an existing Skill when it already owns the capability and the request is an extension.
- Create a separate Skill when the workflow, triggers, outputs, or safety boundary are materially different.
- Convert personas into capability instructions; omit identity, personality, soul, and role-play language.
- Prefer a short `SKILL.md` plus one-level references over a large monolithic prompt.
- Treat screenshots and marketplace cards as partial evidence. Mark missing details as assumptions.
- Keep installation, publication, commit, push, deployment, and deletion outside the default path.
