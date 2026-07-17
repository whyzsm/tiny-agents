# 学霸 TAG 与分类规范

Use this reference when choosing frontmatter tags, folder categories, and Obsidian double links.

## Frontmatter Tags

Use YAML frontmatter tags without `#`.

```yaml
tags:
  - status/seed
  - type/system-note
  - domain/unknown
  - source/text
  - access/pasted
  - confidence/medium
```

Every Study Mode note should include these dimensions:

- `status/*`
- `type/system-note`
- `domain/*`
- `source/*`
- `access/*`
- `confidence/*`

## Controlled Values

### Status

- `status/seed`: newly generated, not yet reviewed.
- `status/processing`: actively being studied or refined.
- `status/reviewed`: checked against sources and useful enough to keep.
- `status/mastered`: user completed recall and transfer tasks.

### Type

- `type/moc`
- `type/overview`
- `type/system-note`
- `type/concept`
- `type/question`
- `type/exercise`
- `type/source`
- `type/qa`

### Source

- `source/web`
- `source/feishu`
- `source/notion`
- `source/yuque`
- `source/dingtalk`
- `source/private-wiki`
- `source/pdf`
- `source/paper`
- `source/video`
- `source/markdown`
- `source/text`
- `source/alidoc`
- `source/file`
- `source/multi`

### Access

- `access/public`: source was readable without authentication.
- `access/authenticated`: source was read through an approved logged-in browser, connector, API, or user-authorized session.
- `access/exported`: source came from a user-provided export file.
- `access/pasted`: source came from pasted text.
- `access/blocked`: source could not be read because authentication, permission, or export was unavailable.

### Confidence

- `confidence/low`
- `confidence/medium`
- `confidence/high`

## Domain Tags

Prefer lowercase English domain tags for search stability.

Common domains:

- `domain/ai/agent`
- `domain/ai/skills`
- `domain/ai/harness`
- `domain/ai/rag`
- `domain/ai/mcp`
- `domain/ai/prompting`
- `domain/ai/eval`
- `domain/ai/llm`
- `domain/product/prd`
- `domain/management/okr`
- `domain/business/crm`
- `domain/tech/frontend`
- `domain/tech/backend`
- `domain/tech/devops`
- `domain/operations/store`
- `domain/tools/obsidian`

If the domain is unclear, use `domain/unknown`. Do not force second or third level classification when the source does not support it.

## Folder Classification

Default note path:

```text
88-学习/[大学科]/[章节或知识要点]/[主题].md
```

Use short, direct folders:

| 大学科 | Examples |
|---|---|
| `AI` | 智能体, skills, harness, RAG, MCP, prompting, eval, LLM |
| `产品` | PRD, 需求, 用户研究, 产品设计 |
| `管理` | OKR, 组织, 复盘, 协作 |
| `技术` | 前端, 后端, 架构, 数据库, DevOps |
| `业务` | CRM, 门店, 回款, 供应链, 财务, 运营 |
| `读书` | 书籍学习, 章节精读 |
| `论文` | 论文精读, 研究综述 |
| `工具` | Obsidian, CLI, 工作流 |

Rules:

- Do not use combined personal folder names such as `AI与智能体` or `产品与需求`.
- Do not follow a user's existing personal taxonomy if it conflicts with the simple `大学科/章节` structure.
- If classification confidence is low, use `88-学习/待分类/` and `domain/unknown`.

## Double Links

Use `[[double links]]` only for durable concepts, models, methods, people, technologies, or recurring questions.

Avoid pseudo-links:

- Do not link ordinary nouns just to increase link count.
- Do not link a concept if it is unlikely to be reused outside the current note.
- Mark concept candidates as `可拆卡`, but do not create separate concept files unless the user asks for asset-package mode.
