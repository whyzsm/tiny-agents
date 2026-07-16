---
name: tech-zcode-ane-spec-usage-doc-team
description: "zcode 与 ane-spec 使用文档专家团。用于根据 KDocs、内部说明、安装日志或项目仓库资料，撰写、重构或审查 zcode 配置、ane-spec 脚手架安装、OpenSpec/spec 变更流程、superpowers 插件、spsx/opsx 命令、验证门和故障排查相关的使用文档。"
metadata:
  source: "repo-authored/from-kdocs-zcode-ane-spec"
  team_type: "router-skill"
  domain: "technical-documentation/spec-workflow"
---

# zcode ane-spec 使用文档专家团

Use this skill as the routing entry point for usage documentation about zcode, ane-spec, OpenSpec, and spec-driven frontend AI workflows. 使用本 Skill 作为 zcode、ane-spec、OpenSpec 与前端 AI spec 工作流使用文档的专家团入口。

It coordinates existing narrow capabilities instead of duplicating them. 它只编排已有窄能力，不复制底层 Skill。

## When To Use

- 用户要求根据 KDocs、内部文档、安装日志或截图写一份 zcode 与 ane-spec 的使用文档。
- 用户要求补齐 spec / OpenSpec / superpowers / spsx / opsx 相关说明、流程图、命令说明或验收检查。
- 用户要求把零散安装步骤改写成新人可执行的开发者指南、快速开始、FAQ、故障排查或维护文档。
- 用户要求审查这类文档是否覆盖前置依赖、权限申请、安装路径、spec 变更流程、验证门和安全边界。

Do not use this skill for generic API reference docs, generic PRD writing, or unrelated ZCode plugin development. For those, route to a narrower API, PRD, or implementation skill.

## Source Material Contract

For the KDocs source titled `前端ai落地 zcode 与 ane-spec 集成`, treat these as confirmed source themes:

- Scope: editor configuration, zcode, ane-spec, installation configuration, and frontend AI landing workflow.
- Installation: run the ane-spec frontend scaffold from the project root; preserve the source document's exact commands only when the target audience is allowed to see internal hosts.
- Prerequisites: Node.js 22+, OpenSpec CLI, uvx, jq, repository permission, and ZCode restart after plugin installation.
- Installed artifacts: superpowers plugin registration, ZCode plugin enablement, `openspec/changes/`, documentation directories, project rules, AGENTS instructions, `.zcode/commands/spsx`, `.zcode/commands/opsx`, `.zcode/skills/openspec-*`, and OpenSpec schema gates/templates.
- First-run action: restart ZCode, open the target project root, then start from `/spsx:next`.

If the source contains private hosts, IPs, local absolute paths, user names, tokens, or organization-only URLs, keep them out of reusable Skill files. In generated usage docs, either retain them only for authorized internal distribution or replace them with placeholders such as `<ane-spec-git-url>`, `<project-root>`, and `<internal-approval-channel>`.

## Workflow

1. Read `references/manifest.json` to confirm the selected companion skills and team boundary.
2. Read `references/workflow.md` to choose the narrowest route for the requested documentation task.
3. For source extraction and audience definition, use `requirements-analysis`.
4. For spec workflow sections, use `spec-workflow` and make OpenSpec artifacts, phase gates, and `/spsx` or `/opsx` commands explicit.
5. For technical documentation structure and wording, use `project-technical-doc-engineer-team`.
6. For long-form usage guide generation, use `project-document-generation-team`.
7. For verification checklists and release-readiness evidence, use `tech-test-automation-team` only when the document needs executable checks or quality gates.
8. Return only the requested artifact: outline, full usage doc, review comments, FAQ, troubleshooting guide, or documentation package.

## Routing Table

| Request type | Primary route | Output |
|---|---|---|
| Clarify readers, scope, permissions, and acceptance criteria | `requirements-analysis` | Documentation contract and missing-question list |
| Explain ane-spec scaffold installation and ZCode setup | `project-technical-doc-engineer-team` | Quick start, prerequisites, commands, and environment notes |
| Explain OpenSpec/spec change lifecycle | `spec-workflow` | Requirements/design/tasks/change-flow section with gates |
| Turn KDocs material into a full manual | `project-document-generation-team` | Complete usage document with outline, body, FAQ, and revision notes |
| Check whether the document is runnable and safe | `tech-test-automation-team` | Verification checklist, command evidence, and risk classification |

## Documentation Output Standard

A complete usage document should include:

1. Title, target readers, prerequisites, and permission requirements.
2. Concept map for zcode, ane-spec, OpenSpec, superpowers, `spsx`, and `opsx`.
3. Installation path with primary and fallback approaches.
4. Generated file inventory and what each directory or command family is for.
5. Spec workflow: explore, propose, plan, apply, verify, sync, archive, and continue.
6. First-run guide: restart ZCode, open project root, run `/spsx:next`, and confirm available skills.
7. Verification gates: dependency check, scaffold result, plugin availability, OpenSpec structure, and command smoke test.
8. FAQ and troubleshooting for permissions, missing dependencies, plugin not loaded, command not found, and private source redaction.

## Guardrails

- Do not execute installation commands from source material unless the user explicitly asks for environment setup.
- Do not publish internal repository URLs, IP addresses, usernames, local absolute paths, tokens, or credentials into reusable package files.
- Mark unverified commands as source-derived examples, not as executed evidence.
- Keep Skill content capability-focused; do not add persona, avatar, or formal plugin metadata unless requested.

## Validation

- Validate JSON: `python3 -m json.tool skills/tech-zcode-ane-spec-usage-doc-team/references/manifest.json`
- Validate YAML structure with a local parser or a minimal Python check.
- Validate Skill package with `quick_validate.py` when available.
- Run `git diff --check`.
- Scan generated files for local absolute paths and obvious credential markers before delivery.
