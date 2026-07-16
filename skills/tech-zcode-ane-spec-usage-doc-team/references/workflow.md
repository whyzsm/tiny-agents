---
scene: "技术文档 / Technical Documentation"
sub_scene: "zcode-ane-spec-usage-doc"
skills:
  - "requirements-analysis"
  - "spec-workflow"
  - "project-technical-doc-engineer-team"
  - "project-document-generation-team"
  - "tech-test-automation-team"
source: "repo-authored/from-kdocs-zcode-ane-spec"
---

# zcode ane-spec 使用文档工作流

Use this workflow to turn source material about zcode, ane-spec, OpenSpec, and superpowers into a documentation artifact. 按任务范围选择必要步骤，不要机械输出完整包。

## Step 1: 文档契约

Use `requirements-analysis` to define:

- target readers: first-time frontend developers, maintainers, reviewers, or team leads;
- source scope: KDocs text, installation logs, project repository, screenshots, or existing docs;
- distribution boundary: internal-only, sanitized external copy, or local draft;
- acceptance criteria: reader can install, understand generated files, run the first command, and know how to verify.

Output: documentation contract, non-goals, redaction rules, and missing questions.

## Step 2: Source Extraction

Extract source facts into four groups:

| Group | What to capture |
|---|---|
| Setup | repository permission, project-root execution, prerequisites, primary and fallback install paths |
| Generated artifacts | ZCode settings, command files, OpenSpec folders, skills, gates, templates, project rules |
| Spec flow | explore, propose, plan, apply, verify, sync, archive, continue, and first-run command |
| Risks | private source URLs, local paths, missing dependencies, plugin reload, command availability |

Do not store private source commands in reusable Skill files. A generated document may include exact commands only when the audience and distribution boundary allow it.

## Step 3: Spec Workflow Section

Use `spec-workflow` to write the spec-focused part. The section must explain:

1. What `openspec/changes/` is for.
2. How requirements, design, tasks, spec, verify, and retrospective templates relate.
3. Which command family starts or advances a change: `/spsx:*` for super-spec flow and `/opsx:*` for OpenSpec operations.
4. What gates should pass before implementation or archive: structure, drift, spec sync, acceptance coverage, task completion, and verification.
5. How to keep project docs, AGENTS rules, and OpenSpec artifacts synchronized.

Output: a clear spec lifecycle section and a command-to-purpose table.

## Step 4: Developer Guide Structure

Use `project-technical-doc-engineer-team` to design the guide:

```text
# zcode 与 ane-spec 集成使用指南

## 适用对象和前置条件
## 核心概念
## 权限申请和环境准备
## 安装方式
## 安装后生成内容
## 第一次启动和验证
## OpenSpec / spec 工作流
## 常用命令速查
## 维护和升级
## FAQ 与故障排查
## 附录：目录清单和验证检查表
```

For a short quickstart, keep only prerequisites, install, first-run, verification, and troubleshooting.

## Step 5: Long-Form Writing

Use `project-document-generation-team` when the user wants a full document. The writer should:

- preserve source terminology: zcode, ane-spec, OpenSpec, superpowers, `spsx`, `opsx`;
- replace private values with placeholders unless explicitly authorized;
- make commands copyable and label the working directory for every command;
- distinguish source-derived examples from commands actually executed by the agent;
- include a revision log and unresolved questions when source evidence is incomplete.

## Step 6: Verification And Review

Use `tech-test-automation-team` only for verification-oriented requests. Review the document against:

- dependency coverage: Node.js 22+, OpenSpec CLI, uvx, jq, repository permission;
- install coverage: primary path, fallback path, project-root requirement, and restart requirement;
- generated artifact coverage: `.zcode/commands`, `.zcode/skills`, `openspec/`, rules, docs, and AGENTS instructions;
- spec coverage: lifecycle, templates, gates, command table, and archive/sync behavior;
- safety coverage: no unintended local absolute paths, credentials, private hosts in public docs, or unsupported claims.

Classify issues as `blocking`, `important`, or `polish`.

## Final Output Shapes

| User asks for | Return |
|---|---|
| "写使用文档" | Full usage guide with source assumptions and verification checklist |
| "补 spec 部分" | Spec workflow section, command table, and gates |
| "做新人快速开始" | Quickstart with prerequisites, install, first-run, and FAQ |
| "审查文档" | Findings first, then missing sections, redaction risks, and suggested patch |
| "生成文档包" | Outline, full doc, FAQ, checklist, revision notes, and open questions |
