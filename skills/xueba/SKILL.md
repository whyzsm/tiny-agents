---
name: xueba
description: Use this skill whenever the user wants to deeply study, digest, restructure, and save learning materials into an Obsidian vault using a tag-first knowledge system, or wants to inspect an existing Obsidian vault to find notes, concepts, tags, links, or knowledge areas that can be upgraded. Trigger for requests like “帮我学习这个资料/网站/论文/视频”, “系统学习后整理到 Obsidian”, “生成学习笔记、概念卡、费曼自测、练习题、复习计划”, “沉淀成 TAG 流知识资产”, “看看 Obsidian 里哪些知识可以升级”, “帮我体检知识库”, “找出过时/重复/薄弱/可合并的笔记”, “优化我的标签和双链”, or learning from login-required sources such as Feishu, Notion, Yuque, DingTalk, private wiki, internal docs, and authenticated web pages. This skill should be used even when the user only says “整理/消化/学习/沉淀/升级/改善/体检” and mentions Obsidian, 标签, 双链, 费曼, 复习, 知识库, existing notes, 飞书, 私有文档, 登录, 权限, 授权, or 内部资料.
---

# 学霸

Use this skill in two modes:

1. Study Mode: turn dense or fragmented learning material into one coherent Obsidian study note by default, with optional asset-package expansion only when requested.
2. Upgrade Mode: inspect an existing Obsidian vault or selected notes and identify knowledge that can be improved, merged, split, linked, retagged, verified, or turned into learning assets.

The goal is not to summarize a source. The goal is to create and maintain notes that support understanding, retrieval, review, transfer, and long-term knowledge growth. The first learning output should usually be one complete Markdown note that explains the topic end to end in the style of a "systematic topic note"; many files are useful only after the user wants long-term decomposition.

The user's preferred knowledge style is TAG flow: light folders, strong tags, strong search, selective bidirectional links.

## Core Principles

- Optimize for learning, not note volume. A large MOC or many files does not mean the user has learned the topic.
- Keep every important claim traceable to a source, or mark it as an inference.
- Use tags as controlled metadata. Do not invent near-duplicate tags.
- Default to no Obsidian double links in Study Mode. Use `[[...]]` only when the target note already exists in the vault or is created in the same task. Otherwise write the concept as plain text and mark it as `可拆卡`.
- Distinguish source claims, AI synthesis, and user-context inference.
- Produce exercises that force recall, explanation, transfer, and real work.
- Default to report-first when upgrading existing notes. Do not rewrite the user's notes unless they explicitly ask you to apply changes.
- Default to one-file output in Study Mode. The single note should resemble a polished Obsidian system topic note: abstract, mental map, concept network, Why/What/How, boundaries, Feynman loop, exercises, sources, and QA. Do not split into MOC, concepts, questions, and exercises as separate files unless the user explicitly asks for a knowledge asset package, concept cards, or long-term vault decomposition.
- Treat authenticated sources as a normal input class. Try safe authorization paths before giving up, but never bypass access controls, scrape cookies/tokens, ask for passwords, or fabricate content from a login page.
- Save durable learning notes into the resolved Obsidian learning root, not into machine-specific folders, existing personal taxonomies, or a generated-output scratch area. The learning root is usually `88-学习/`; when the resolved vault contains a docs site such as `docs/xueba/`, use `docs/xueba/88-学习/` and never create a sibling `88-学习/` at the vault root. Use generated-output folders only for drafts, tests, failure reports, or intermediate artifacts when the user explicitly wants them.
- Saving to Obsidian means writing into the user's actual Obsidian vault, not merely the current Codex workspace. Resolve the live vault before saving.
- Do not hard-code machine-specific vault paths or Obsidian deep links in this skill. Treat Obsidian as local software plus a set of vault directories that must be discovered or provided at runtime.

## Supported Inputs

Accept these source types:

- Web URL: read the page when network/browser access is available. If inaccessible, ask for pasted content or a local export.
- Dynamic web URL: if a page is rendered by JavaScript, CMS data, a documentation-center shell, or encoded script state, read and follow `references/dynamic-web-sources.md` before declaring the source empty or inaccessible.
- Authenticated URL: Feishu, Notion, Yuque, DingTalk, private wiki, LMS, Google Docs, and internal docs may require a login session. Use the Authenticated Source Workflow before declaring failure.
- PDF or paper: extract title, author, date, abstract, section structure, page references, and formulas when available.
- Markdown, text, DOCX, slides, or spreadsheet notes: read with the appropriate local tool.
- Video transcript or meeting transcript: preserve timestamps when available.
- Pasted content: treat the pasted text as source and preserve user-provided context.
- Multiple sources: synthesize when they address the same topic; otherwise create one source note plus one synthesis index.

If the source cannot be parsed, return a structured failure with:

```markdown
## 无法处理
- 输入类型：
- 失败原因：
- 需要用户补充：
- 可替代方案：
```

Do not fabricate content to cover missing source text.

## Authenticated Source Workflow

When a source returns a login page, no-permission page, SSO page, empty shell, or JavaScript app without document text, read and follow `references/authenticated-sources.md`.

Never ask for passwords, 2FA codes, cookies, bearer tokens, authorization headers, or session storage. Never summarize a login page as if it were the learning source.

## Controlled Tag System

Use YAML frontmatter tags without `#`. In body text, use `#tag/path` only when necessary.

When choosing tags, domain labels, folder categories, or double-link candidates, read and follow `references/tag-taxonomy.md`.

Every Study Mode note should include these tag dimensions: `status/*`, `type/system-note`, `domain/*`, `source/*`, `access/*`, and `confidence/*`.

## Double-Link Safety

Do not create unresolved Obsidian links by default. Empty `[[...]]` targets create confusing blank notes for the user.

Before the final write:

1. Prefer plain text concept names in the default single-file note.
2. If using `[[...]]`, verify the target `.md` exists in the resolved vault or is one of the files created in the same task.
3. Run `scripts/check_obsidian_links.py` when local script execution is available.
4. If any link is unresolved, convert it to plain text and keep `可拆卡` in the concept table instead of leaving the link.

## Study Mode Output

Default output for Study Mode is a single Markdown file saved under the resolved learning root in the resolved Obsidian vault. First locate the vault, then resolve the learning root:

- use `docs/xueba/88-学习/` when the vault has `docs/xueba/`
- otherwise use `88-学习/`

Choose content-based subfolders under that learning root.

## Obsidian Vault Resolution

Before writing files, resolve Obsidian and the target vault at runtime.

Prefer this script path when local script execution is available:

1. Resolve vault with `scripts/resolve_obsidian_vault.py --json`. Use `--vault` if the user provided an explicit vault path.
2. If `obsidian_installed` is false, install Obsidian from the official GitHub releases repository by running `scripts/install_obsidian.py --json`, then rerun `scripts/resolve_obsidian_vault.py --json`. Request the required host/network/system approval instead of only giving a download link.
3. Classify the note with `scripts/classify_learning_path.py`.
4. Check double links with `scripts/check_obsidian_links.py` if the draft contains `[[...]]`.
5. Write the note with `scripts/write_obsidian_note.py`, which maps `88-学习/...` to the resolved learning root.

If scripts are unavailable, read and follow `references/obsidian-workflow.md`.

Saving to Obsidian means writing a Markdown file into the resolved vault directory under the resolved learning root. Do not use current workspaces, generated-output directories, `/tmp`, `obsidian://` links, or a download prompt as save destinations.

Use one coherent note that contains the full learning experience. When writing the default single-file note, read and follow `references/note-template.md`.

Use Obsidian double links only after link-safety verification. If a concept deserves a future card but no target note exists, keep it as plain text and mark it as "可拆卡"; do not create the separate card unless requested. Avoid making the output look like many small disconnected notes pasted together; the note must read as one complete explanation.

## Optional Asset Package

Only create a multi-file asset package when:

- the user explicitly asks for concept cards, MOC, or a full Obsidian asset package
- the source set is too large for one readable note and the user accepts splitting
- the task is upgrading an existing vault and separate reports/cards are safer

When needed, create this package:

```text
学霸/[topic]/
  index.md
  overview.md
  notes.md
  concepts/
    [concept].md
  questions/
    feynman.md
    recall.md
  exercises/
    transfer.md
  review-plan.md
  sources.md
  qa.md
```

Avoid creating empty files.

Use readable Chinese titles for user-facing note titles. Use stable concept filenames that do not include course names, source names, or dates unless needed for disambiguation.

## Mode Selection

Choose Study Mode when the user provides new material or asks to learn a topic from sources.

Choose Upgrade Mode when the user asks to:

- inspect an Obsidian vault or folder
- find notes that can be upgraded
- improve tags, links, MOCs, concept cards, or sources
- detect weak, stale, duplicate, isolated, or overgrown notes
- convert messy notes into reusable learning assets
- build a learning roadmap from existing notes

If the user asks for both, run Upgrade Mode first to understand the existing knowledge base, then run Study Mode for new material and connect it to existing notes.

## Workflow

This workflow describes Study Mode. Use the Upgrade Mode workflow below when the user asks to improve existing Obsidian content.

### 1. Establish Learning Intent

Before generating notes, infer or ask for:

- Topic
- User goal: overview, work application, exam prep, research, or decision support
- Target difficulty: beginner, intermediate, advanced
- Prior knowledge
- Desired output location if saving files; if not provided, save under `88-学习/` and infer content-based subfolders from the topic

If the user wants you to continue without clarification, make conservative assumptions and record them in the single output note.

### 2. Parse And Normalize Sources

Extract:

- Title, author, source URL/path, publication date if available
- Source type
- Core thesis
- Section map
- Important definitions, claims, numbers, formulas, code, and examples
- Source anchors: URL, page number, heading, paragraph, timestamp, or file path

Remove ads, navigation, repeated boilerplate, and low-value filler. Preserve technical details.

For Web URLs, if normal HTML extraction returns only navigation, placeholders, mount nodes, or a thin SPA shell, read `references/dynamic-web-sources.md` and run `scripts/extract_web_source.py --url [url] --json` when available. Use decoded public CMS/API/script-state text as source content only when it comes from the requested origin. If only metadata or navigation can be read, state that limitation in the note and do not invent article/API details.

### 3. Build The Learning Model

Reconstruct the material using this order:

1. Why: problem, motivation, constraints, historical or business context
2. What: definitions, mechanisms, components, models, assumptions
3. How: procedure, examples, SOP, implementation pattern
4. Limits: boundary conditions, failure modes, common misconceptions, explicit "熔断条件"
5. Transfer: what the learner can do with this knowledge

Do not copy the original table of contents unless it is already the best learning structure.

### 4. Handle Concepts

In default one-file mode, include concepts in a table inside the note. Do not create separate concept files.

Create separate concept cards only in optional asset-package mode or when the user explicitly asks for cards.

When creating separate cards, create them only for durable concepts.

Each concept card should include:

```markdown
---
title: "[概念名]"
aliases: []
tags:
  - status/seed
  - type/concept
  - domain/[domain]
  - confidence/[level]
---

# [概念名]

## 一句话定义

## 边界
- 它是什么：
- 它不是什么：

## 反例

## 常见误区

## 应用场景

## 关联
- 前置：[概念名；仅在目标笔记已存在时使用双链]
- 后续：[概念名；仅在目标笔记已存在时使用双链]
- 易混：[概念名；仅在目标笔记已存在时使用双链]

## 来源
- [source-anchor]
```

Avoid concept cards that only restate a paragraph. A concept card should be reusable outside the original source.

### 5. Generate Learning Tests

Create questions at four levels, preferably inside the single note:

- Recall: closed-book facts, definitions, steps.
- Explanation: Feynman-style explanation and misconception checks.
- Transfer: apply the idea to a new case.
- Real task: a practical output the user can produce.

Every question needs a reference answer, scoring criteria, or expected output. Do not create exercises without answers.

### 6. Build A Review Plan

Use spaced review intervals by default:

- Day 1: recall core concepts and explain the MOC from memory.
- Day 3: answer Feynman questions and correct weak concepts.
- Day 7: complete transfer exercise.
- Day 14: solve a real task or write a one-page synthesis.
- Day 30: decide whether to mark notes as `status/reviewed` or `status/mastered`.

Adapt the plan if the user has an exam date, project deadline, or weekly cadence.

### 7. Run Quality Gate

In default one-file mode, include the quality checklist from `references/note-template.md` under `## 5. 来源`. In asset-package mode, create `qa.md` with the same checks adapted to the generated package.

If an item cannot pass, explain the gap and how to fix it.

## Upgrade Mode Workflow

Use Upgrade Mode to evaluate and improve existing Obsidian knowledge. This mode is a knowledge-base audit, not a destructive rewrite.

When auditing or upgrading a vault, read and follow `references/upgrade-mode.md`.

Default to report-only. Do not rewrite existing notes unless the user explicitly asks you to apply changes.

## Markdown Templates

Default single-file notes use `references/note-template.md`. Upgrade reports use `references/upgrade-mode.md`.

## Final Response

When done, report:

- Saved paths
- Source access limitations
- Main generated assets
- Quality gate status
- Next recommended review action

Keep the response concise. The files should carry the detail.
