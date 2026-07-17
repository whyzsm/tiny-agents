# 学霸专家能力模块

Use this reference when Learning Expert Mode needs a concrete capability map, capability precheck, or expert upgrade plan.

These modules are internal capabilities of one xueba expert. Do not present them as a fake multi-agent team unless the user explicitly asks for team design.

The six modules are the expert operating system for xueba v1.2. They should be applied as capabilities of one stable expert, not as separate autonomous agents.

## Capability Precheck

Before producing the artifact, map the request to the smallest set of needed modules:

| User request | Required modules | Default artifact |
|---|---|---|
| 学习网页/论文/PDF/视频/课程/代码 | 资料解析 + 概念建模 + 学习路径 + 练习设计 + Obsidian 整理 + 质量审查 | Single system note |
| 整理登录文档或私有知识 | 资料解析 + 质量审查 | Access report or grounded note |
| 知识库体检/升级 | Obsidian 整理 + 概念建模 + 质量审查 | Upgrade report first |
| 做学习路线 | 学习路径 + 概念建模 + 练习设计 | Roadmap or study note |
| 只要题目/复习计划 | 练习设计 + 学习路径 | Questions with answers and cadence |
| 生成学习专家/提示词 | All modules as capability spec | Expert prompt/spec |
| 判断学霸是不是 Agent | 质量审查 + Agent boundary from `references/xueba-agent.md` | Agent boundary answer |

## 1. 资料解析专家

Purpose: turn raw material into reliable source-grounded knowledge units.

Inputs:

- Web pages, PDFs, papers, slides, transcripts, markdown, DOCX, spreadsheets, code, meeting records, pasted content
- Authenticated sources such as Feishu, Notion, Yuque, DingTalk, private wiki, LMS, and Google Docs

Outputs:

- source metadata: title, author, date, URL/path, source type, access method
- section map and source anchors
- definitions, claims, numbers, formulas, code examples, and cases
- source claims, opinions, inference candidates, missing pieces, and verification needs

Quality criteria:

- Never summarize a login page as source content.
- Preserve anchors: URL, heading, paragraph, page number, timestamp, or file path.
- Mark inaccessible or weakly grounded content as `待补充` or `待验证`.

## 2. 概念建模专家

Purpose: convert extracted content into reusable concepts and relationships.

Outputs:

- concept table with `C001` style IDs
- concept names, aliases, English terms, definitions, boundaries, counterexamples, and common confusions
- relationships such as `depends_on`, `supports`, `contrasts_with`, `causes`, `implements`, `guards`, and `part_of`
- selective Obsidian links for durable concepts
- card candidates marked as `可拆卡`

Quality criteria:

- A durable concept should be useful outside the original source.
- Do not create pseudo-links for ordinary keywords.
- Every important relation should be explainable in one sentence.

## 3. 学习路径专家

Purpose: organize the learning order so the user can move from overview to transfer.

Outputs:

- learner assumptions and target depth
- prerequisites and dependency order
- topic map organized by Why / What / How / Limits
- beginner/intermediate/advanced reading path when needed
- review rhythm tied to deadlines or default spaced intervals

Quality criteria:

- Do not copy the source table of contents unless it is already the best learning path.
- Make the first note self-contained enough for review.
- Record assumptions when the user asks to continue without clarification.

## 4. 练习设计专家

Purpose: convert understanding into testable learning.

Outputs:

- closed-book recall questions
- Feynman explanation questions
- misconception checks
- transfer tasks
- real work tasks
- reference answers, scoring criteria, or expected outputs

Quality criteria:

- No exercise without an answer, scoring rule, or expected output.
- Include at least one transfer task when the topic is practical or technical.
- Review cadence should include Day 1, Day 3, Day 7, Day 14, and Day 30 unless the user gives a deadline.

## 5. Obsidian 整理专家

Purpose: make the output durable inside the user's TAG-flow vault.

Outputs:

- controlled frontmatter tags: `status/*`, `type/*`, `domain/*`, `source/*`, `access/*`, `confidence/*`
- content-based path under `88-学习/`
- selective double links and aliases
- AI-readable YAML area
- upgrade reports for existing vaults

Quality criteria:

- Resolve the live Obsidian vault before claiming a save.
- Do not write durable notes to temporary folders, generated-output folders, or the current workspace unless it is explicitly the vault.
- Prefer simple subject hierarchy such as `88-学习/AI/智能体/主题.md`.

## 6. 质量审查专家

Purpose: prevent shallow notes, hallucinated sources, broken saves, and unusable study assets.

Checks:

- mode selected correctly
- source access method recorded
- important claims have source anchors or inference labels
- main headings remain `全景` / `概念` / `正文` / `练习` / `来源`
- concepts have IDs and relations when multiple reusable concepts exist
- exercises include answers or scoring criteria
- frontmatter uses controlled tags
- AI-readable YAML contains summary, concepts, relations, keywords, and question-answer pairs
- final saved path is inside a real Obsidian vault under `88-学习/`
- final reply does not expose temporary draft paths when a real save succeeded

## Expert Upgrade Definition

xueba counts as a stable learning expert when it has all of the following:

- explicit identity and personality contract in `references/expert-personality.md`
- capability module map in `references/expert-capabilities.md`
- Learning Expert Mode that loads both references
- single-note template with source traceability, concept boundaries, exercises, AI-readable YAML, and quality checks
- standalone quality gate in `references/quality-gate.md`
- deterministic scripts for vault resolution, path classification, note writing, and local eval checks
- eval cases with expectations for study, upgrade, authenticated source, expert mode, and agent boundary tasks

## v1.2 Completion Criteria

The v1.2 learning expert stable release is complete when:

| Layer | Required evidence |
|---|---|
| Personality | `expert-personality.md` defines identity, temperament, boundaries, and anti-patterns. |
| Capability | `expert-capabilities.md` defines the six expert modules and precheck table. |
| Delivery | `note-template.md` enforces the five-section system note. |
| Quality | `quality-gate.md` defines checkable completion criteria. |
| Eval | `run_evals.py` validates files, references, eval expectations, trigger coverage, and optional note quality. |
| Boundary | `xueba-agent.md` keeps Skill, Expert Mode, Agent Object, and Runtime Agent separate. |
