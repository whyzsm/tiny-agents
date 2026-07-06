# 学霸 Eval 断言

Use these assertions when reviewing `evals/evals.json` outputs.

## Obsidian Save Assertions

- Final saved note path must be inside a resolved Obsidian vault.
- Final saved note path must include `/88-学习/`.
- If the resolved vault contains `docs/xueba/`, final saved note path must include `/docs/xueba/88-学习/` and must not create a root-level sibling `/88-学习/`.
- Study notes should use the simplified taxonomy:
  - `88-学习/AI/skills/` for Agent Skills, skill creation, skill eval, and skill runtime topics.
  - `88-学习/AI/智能体/` or `88-学习/AI/harness/` for agent architecture and harness topics.
- Final user-facing response must not expose `/private/tmp`, `/tmp`, or other temporary draft paths when the final vault write succeeded.
- The current Codex workspace must not be treated as the Obsidian vault unless it contains `.obsidian` or the user explicitly provides it as the vault.
- If Obsidian is not detected, the workflow must install Obsidian from `https://github.com/obsidianmd/obsidian-releases`, rerun vault resolution, and must not claim a successful Obsidian save before a real vault is resolved.
- A Chinese download-page hint alone is not sufficient for the not-installed case.

## Single Note Assertions

- The note must be one coherent Markdown file unless the user explicitly asks for a multi-file asset package.
- Default single-file notes should not contain `[[...]]` links unless the target note already exists or is created in the same task.
- Unresolved double links must be converted to plain text and marked as `可拆卡` instead of creating empty Obsidian note targets.
- The main headings should be concise and limited to:
  - `## 1. 全景`
  - `## 2. 概念`
  - `## 3. 正文`
  - `## 4. 练习`
  - `## 5. 来源`
- `## 3. 正文` should cover Why / What / How / Limits.
- `## 4. 练习` should include answers, scoring rules, or expected outputs.
- `## 5. 来源` should include source access method, source list, confidence, limitations, and quality checks.

## Frontmatter Assertions

- Frontmatter must include:
  - `title`
  - `tags`
  - `source`
  - `created`
- Tags must include:
  - `status/*`
  - `type/system-note`
  - `domain/*`
  - `source/*`
  - `access/*`
  - `confidence/*`

## Authenticated Source Assertions

- Login pages, SSO pages, no-permission pages, and empty app shells must not be summarized as if they were source content.
- If no authorized content can be read, output must use `access/blocked` and explain the next action.
- The output must not ask for passwords, 2FA codes, cookies, bearer tokens, or session storage.
- The output must not print credentials or authorization headers.

## Dynamic Web Source Assertions

- If normal HTML contains only navigation, placeholders, mount nodes, or a documentation-center shell, the workflow must try `references/dynamic-web-sources.md` and `scripts/extract_web_source.py` before declaring the source unreadable.
- Decoded CMS/script-state/API text may be used only when it is public and comes from the requested source origin.
- Meta descriptions and navigation-only text are not enough for detailed learning claims.
- If detailed article/API content remains unreadable, the note must state the access limitation and avoid fabricated details.

## Classification Assertions

- Do not use combined personal directory names such as `AI与智能体` or `产品与需求`.
- Prefer direct subject hierarchy, for example:
  - `AI/skills`
  - `AI/智能体`
  - `AI/RAG`
  - `产品/PRD`
  - `管理/OKR`
- ArkUI, ArkTS, HarmonyOS UI, and mobile UI framework topics should save under `88-学习/技术/前端/` or an equally direct frontend/mobile UI folder.
- If classification confidence is low, save under `88-学习/待分类/` and mark the domain conservatively.
