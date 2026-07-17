# 学霸 Upgrade Mode

Use this reference when the user asks to inspect, improve, audit, reorganize, retag, relink, merge, split, or upgrade an existing Obsidian vault or selected notes.

## Safety Rule

Default to report-only. Do not rewrite the user's existing notes unless the user explicitly asks to apply changes.

## Workflow

### 1. Establish Scope

Identify:

- vault path or selected folder/files
- audit goal: tag cleanup, concept upgrade, learning quality, source traceability, duplicate detection, MOC creation, review planning, or all
- update permission: `report-only`, `propose-patches`, or `apply-edits`
- safety rule: preserve original wording unless rewriting is requested

If no vault is provided, resolve the vault using `scripts/resolve_obsidian_vault.py` or `references/obsidian-workflow.md`.

### 2. Inventory Notes

Scan Markdown metadata before reading full content:

- file path
- title
- frontmatter tags, aliases, status, source
- outgoing and unresolved links
- headings
- rough size
- source references
- TODOs or stale markers
- last modified date when available

Start with metadata and headings, then inspect high-priority candidates.

### 3. Detect Opportunities

Use these buckets:

- `missing-tags`: missing or inconsistent TAG flow metadata.
- `tag-drift`: same meaning expressed by multiple tags.
- `orphan-note`: few or no meaningful links.
- `weak-source`: important claims lack source anchors.
- `thin-note`: note is too shallow and should become a seed or be merged.
- `overgrown-note`: note covers too many ideas and should be split.
- `duplicate-concept`: multiple notes describe the same concept.
- `concept-candidate`: recurring idea worth extracting into a concept card.
- `moc-candidate`: related cluster deserves an index/MOC.
- `review-candidate`: useful note lacks questions, exercises, or review plan.
- `stale-knowledge`: note may need current verification.
- `broken-link`: unresolved or misleading double link.

Do not assume a note is wrong just because it is old. Mark it as "needs verification" unless current sources have been checked.

### 4. Score Candidates

Score from 1 to 5:

- Impact: how much learning or retrieval improves.
- Confidence: how sure the recommendation is from local evidence.
- Effort: how much work the update likely requires.

Prioritize high-impact, high-confidence, low-effort changes.

## Report Template

Create report inside the resolved Obsidian vault unless the user only wants a chat report:

```text
88-学习/工具/Obsidian/知识库升级报告/YYYY-MM-DD-知识库升级报告.md
```

```markdown
---
title: "知识库升级报告"
tags:
  - status/seed
  - type/qa
  - domain/knowledge-management/obsidian
  - source/file
  - access/pasted
  - confidence/medium
created: "YYYY-MM-DD"
---

# 知识库升级报告

## 审计范围
- 路径：
- 笔记数量：
- 本次目标：
- 模式：report-only | propose-patches | apply-edits

## 总体判断
- 当前知识库最强的地方：
- 最大的知识复利机会：
- 最大风险：

## 优先升级清单
| 优先级 | 文件 | 问题类型 | 建议动作 | 影响 | 置信度 | 工作量 |
|---|---|---|---|---:|---:|---:|

## TAG 流问题

## 双链与 MOC 机会

## 概念卡升级机会

## 来源与可信度问题

## 学习质量升级

## 建议的下一步
```

## Patch Plan Template

In `propose-patches` mode, do not edit files. Produce this for each selected note:

```markdown
## [文件路径]
- 建议动作：
- 原因：
- 预期收益：
- 风险：
- 建议新增标签：
- 建议新增链接：
- 建议拆分/合并：
```

## Apply-Edits Gate

Before editing:

1. Re-read the target note.
2. Preserve original user wording where possible.
3. Add missing frontmatter and sections incrementally.
4. Do not delete content unless the user asks.
5. Record changed files in the final response.

Quality gate:

- [ ] User-selected scope only
- [ ] No accidental deletion of original content
- [ ] Tags use controlled TAG flow vocabulary
- [ ] Added links point to durable concepts
- [ ] Claims are sourced or marked as inference
- [ ] Suggested splits/merges are explained
- [ ] Review tasks are actionable
