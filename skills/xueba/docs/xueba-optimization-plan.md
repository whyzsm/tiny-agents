# 学霸技能优化方案

## 1. 目标

把“学霸”从一份较完整的单文件技能，升级为一个符合 Agent Skills 工程实践的可维护技能包。

优化后的学霸应具备：

- 触发更准：学习、整理、Obsidian 沉淀、知识库升级等场景能稳定触发，不误触发普通问答。
- 执行更稳：Obsidian 检测、vault 解析、保存路径、临时文件清理走可验证流程。
- 上下文更轻：常用规则留在 `SKILL.md`，长模板、标签体系、平台授权细节放到 `references/` 按需加载。
- 结果可测：用 eval 验证触发、保存路径、单文件质量、登录页处理和升级模式。
- 多用户通用：不写死本机路径，不依赖某个用户的目录习惯，默认使用 `88-学习/大学科/章节/主题.md`。

## 2. 现状判断

### 已具备

- 已形成 Study Mode 和 Upgrade Mode 两种模式。
- 已明确默认输出为单文件系统化笔记。
- 已确定 Obsidian 写入规则：先检测软件和 vault，再写入真实 vault。
- 已确定学习根目录：`88-学习/`。
- 已改为简洁目录结构：`AI/智能体`、`AI/skills` 这类大学科分层。
- 已加入登录/授权资料处理规则，避免总结登录页或伪造内容。

### 主要短板

- `SKILL.md` 仍偏长，部分规则可拆到 `references/`。
- Obsidian 检测和 vault 解析目前是文字流程，缺少可复用脚本。
- eval 只有提示和预期描述，缺少可执行断言。
- 没有 trigger eval，无法系统验证 description 是否过宽或过窄。
- 临时文件策略不够明确，容易把 `/private/tmp` 中间产物暴露给用户。
- 对多客户端兼容性缺少明确边界，例如 Codex、OpenCode、Claude Code 的技能扫描路径差异。

## 3. 目标结构

建议把技能包调整为：

```text
xueba/
├── SKILL.md
├── README.md
├── docs/
│   └── xueba-optimization-plan.md
├── references/
│   ├── note-template.md
│   ├── tag-taxonomy.md
│   ├── obsidian-workflow.md
│   ├── authenticated-sources.md
│   └── upgrade-mode.md
├── scripts/
│   ├── resolve_obsidian_vault.py
│   ├── install_obsidian.py
│   ├── classify_learning_path.py
│   └── write_obsidian_note.py
└── evals/
    ├── evals.json
    ├── trigger-evals.json
    └── assertions.md
```

原则：

- `SKILL.md` 保留角色、触发、核心流程、何时加载 reference 的指令。
- `references/` 承载长模板和细则。
- `scripts/` 承载确定性高、容易出错的文件系统逻辑。
- `evals/` 承载测试集和断言说明。

## 4. SKILL.md 精简方案

### 保留在 SKILL.md

- Skill 目标和两种模式。
- 触发场景和不触发边界。
- 核心原则。
- 高层工作流。
- 何时加载哪个 reference。
- 安全边界：不读 cookie/token/password，不伪造登录页内容。

### 下沉到 references

- 单文件模板 -> `references/note-template.md`
- 标签规范 -> `references/tag-taxonomy.md`
- Obsidian 检测与保存细则 -> `references/obsidian-workflow.md`
- 飞书/Notion/语雀/钉钉等授权资料处理 -> `references/authenticated-sources.md`
- Upgrade Mode 的扫描、评分、报告模板 -> `references/upgrade-mode.md`

加载规则示例：

```markdown
When writing a study note, read `references/note-template.md`.
When resolving Obsidian, prefer `scripts/resolve_obsidian_vault.py`; if unavailable, read `references/obsidian-workflow.md`.
When the source requires login, read `references/authenticated-sources.md`.
When auditing a vault, read `references/upgrade-mode.md`.
```

## 5. Obsidian 写入流程优化

### 目标行为

保存到 Obsidian 时必须满足：

```text
检测 Obsidian 是否安装
-> 定位真实 vault
-> 确认或创建 88-学习/
-> 根据内容分类
-> 直接写入正式目标文件
-> 清理临时文件
-> 报告最终文件路径
```

### 临时文件规则

- 不把 `/private/tmp`、`/tmp` 等路径作为用户可见结果。
- 如因沙箱限制必须使用临时文件，最终回复只报告正式 Obsidian 路径。
- 成功写入 vault 后清理临时文件。
- 失败时可保留临时文件，但必须说明它是草稿，并给出下一步。

### 脚本规划

#### `resolve_obsidian_vault.py`

输入：

```bash
python scripts/resolve_obsidian_vault.py --json
```

输出：

```json
{
  "obsidian_installed": true,
  "vaults": [
    {
      "path": "/path/to/vault",
      "open": true,
      "source": "obsidian-config"
    }
  ],
  "selected_vault": "/path/to/vault",
  "warnings": []
}
```

错误输出：

```json
{
  "obsidian_installed": false,
  "selected_vault": null,
  "install_required": true,
  "install_source": "https://github.com/obsidianmd/obsidian-releases",
  "installer_command": "python scripts/install_obsidian.py --json",
  "next_action": "Run `python scripts/install_obsidian.py --json` to install Obsidian from https://github.com/obsidianmd/obsidian-releases, then rerun this resolver."
}
```

#### `install_obsidian.py`

输入：

```bash
python scripts/install_obsidian.py --json
```

行为：

- 从官方 GitHub releases 仓库 `obsidianmd/obsidian-releases` 获取最新版本。
- 根据当前 OS 选择 `.dmg`、`.AppImage`、`.deb` 或 `.exe`。
- 安装完成后要求重新运行 `resolve_obsidian_vault.py`。

#### `classify_learning_path.py`

输入：

```json
{
  "title": "Agent Skills 开放技能标准与工程实践",
  "domain_tags": ["domain/ai/skills"],
  "keywords": ["Agent Skills", "SKILL.md", "eval", "scripts"]
}
```

输出：

```json
{
  "relative_dir": "88-学习/AI/skills",
  "filename": "Agent Skills：开放技能标准与工程实践.md",
  "confidence": "high"
}
```

#### `write_obsidian_note.py`

能力：

- 创建目标目录。
- 避免覆盖同名文件，除非明确允许。
- 写入 Markdown。
- 返回最终路径。
- 清理传入的临时文件。

## 6. 分类策略优化

默认路径：

```text
88-学习/[大学科]/[章节或知识要点]/[主题].md
```

大学科建议：

| 大学科 | 适用内容 |
|---|---|
| `AI` | Agent、LLM、RAG、MCP、skills、prompting、模型工程 |
| `产品` | PRD、需求、用户研究、产品设计、原型、验收 |
| `管理` | OKR、组织、经营、复盘、会议、协作机制 |
| `技术` | 前端、后端、架构、数据库、测试、DevOps |
| `业务` | CRM、门店、回款、供应链、财务、运营 |
| `读书` | 书籍学习、章节精读、阅读笔记 |
| `论文` | 学术论文、技术报告、研究综述 |
| `工具` | 软件工具、命令行、工作流、效率系统 |

AI 章节建议：

```text
AI/智能体
AI/skills
AI/RAG
AI/MCP
AI/harness
AI/prompting
AI/eval
```

规则：

- 不使用 `AI与智能体`、`产品与需求` 这类合并式目录。
- 不因为某个 vault 已有个人目录就跟随个人目录。
- 分类不确定时使用 `88-学习/待分类/`。

## 7. 单文件模板优化

保持 5 个主目录：

```markdown
## 1. 全景
## 2. 概念
## 3. 正文
## 4. 练习
## 5. 来源
```

每个目录职责：

| 目录 | 作用 |
|---|---|
| 全景 | 给出主题的核心脉络、Why/What/How/Limits 一屏图 |
| 概念 | durable concepts、双链、边界、可拆卡 |
| 正文 | 系统化解释，包含 Why / What / How / Limits / Links |
| 练习 | 费曼自测、闭卷回忆、迁移任务、复习节奏 |
| 来源 | 来源、可信度、访问方式、质量检查 |

保留简洁目录，但内容不能变浅。正文内部可以有三级标题承载细节。

## 8. Eval 体系

### Trigger eval

新增 `evals/trigger-evals.json`：

```json
{
  "should_trigger": [
    "学习这个网页并存到 Obsidian",
    "把这篇论文整理成 TAG 流学习笔记",
    "看看我的 Obsidian 哪些知识可以升级",
    "这个飞书文档需要登录，帮我学习整理",
    "帮我把这段资料做成费曼自测"
  ],
  "should_not_trigger": [
    "解释一下 Python list 怎么用",
    "帮我写一个 React Button",
    "翻译这句话",
    "今天上海天气如何",
    "帮我压缩这段 CSS"
  ]
}
```

### Output eval

覆盖场景：

| 场景 | 核心断言 |
|---|---|
| 公开网页 | 有来源、access/public、保存到 `88-学习/` |
| 登录页 | 不伪造内容，返回 blocked 或要求导出 |
| Obsidian 未安装 | 从 `obsidianmd/obsidian-releases` 安装并复检 |
| 多 vault | 不擅自选择，要求确认 |
| 单文件输出 | 主目录仅为全景/概念/正文/练习/来源 |
| 分类 | AI skills 进入 `88-学习/AI/skills/` |
| 临时文件 | 最终结果不暴露 `/private/tmp` |

### Assertion 设计

可以从文本输出和文件系统结果做断言：

- frontmatter 包含 `status/type/domain/source/access/confidence`。
- Markdown 主目录包含且只包含目标五段。
- 文件路径匹配 `88-学习/AI/skills/*.md`。
- 不包含 `/private/tmp` 或具体用户主目录绝对路径。
- 登录页内容不被当作正文学习。
- source 列表包含原始 URL。

## 9. 分阶段落地计划

### Phase 1：整理与拆分

- [x] 新增 `references/note-template.md`。
- [x] 新增 `references/obsidian-workflow.md`。
- [x] 新增 `references/authenticated-sources.md`。
- [x] 新增 `references/upgrade-mode.md`。
- [x] 精简 `SKILL.md` 到高层规则和加载指令。

验收：

- `SKILL.md` 不再承载长模板。
- 现有 README 和 eval 仍可解释完整行为。

### Phase 2：脚本化 Obsidian 流程

- [x] 新增 `scripts/resolve_obsidian_vault.py`。
- [x] 新增 `scripts/install_obsidian.py`。
- [x] 新增 `scripts/classify_learning_path.py`。
- [x] 新增 `scripts/write_obsidian_note.py`。
- [x] README 补充脚本使用方式。

验收：

- 无 Obsidian 时从官方 GitHub releases 安装并复检。
- 有多个 vault 时返回候选列表。
- 成功写入时只报告最终 Obsidian 路径。

### Phase 3：Eval 建设

- [x] 新增 `evals/trigger-evals.json`。
- [x] 扩展 `evals/evals.json`。
- [x] 新增 `evals/assertions.md`。
- [ ] 对至少 8 个核心场景跑一次人工评估。

验收：

- 覆盖公开网页、登录页、粘贴内容、Obsidian 未安装、多 vault、路径分类、单文件模板、知识库升级。
- 每个 eval 有明确 pass/fail 标准。

### Phase 4：质量收敛

- [ ] 根据 eval 结果优化 `description`。
- [ ] 根据误触发/漏触发调整技能边界。
- [ ] 把常见失败案例写入 references。
- [ ] 发布一个稳定版本 tag。

验收：

- 触发准确率明显提升。
- 输出路径稳定。
- 用户可见结果不再暴露临时文件。

## 10. 优先级

| 优先级 | 项目 | 原因 |
|---|---|---|
| P0 | 临时文件不暴露、最终只报告 Obsidian 路径 | 直接影响用户信任 |
| P0 | Obsidian vault 解析脚本 | 直接影响保存正确性 |
| P1 | 单文件模板下沉 reference | 降低上下文成本 |
| P1 | trigger eval | 防止误触发和漏触发 |
| P1 | 登录资料 eval | 防止伪造内容 |
| P2 | 分类脚本 | 提高多用户一致性 |
| P2 | Upgrade Mode reference | 便于后续扩展知识库升级能力 |

## 11. 近期建议

当前已完成：

1. 新增 `references/note-template.md`，把当前五段式模板搬进去。
2. 新增 `scripts/resolve_obsidian_vault.py`，解决跨用户 Obsidian 检测和 vault 选择。
3. 新增 eval，尤其是“最终回复不得暴露 `/private/tmp`”和“保存路径必须在 `88-学习/` 下”。
4. 新增 `references/tag-taxonomy.md`、`references/obsidian-workflow.md`、`references/authenticated-sources.md`、`references/upgrade-mode.md`，把长规则拆出 `SKILL.md`。
5. 新增 `scripts/classify_learning_path.py` 和 `scripts/write_obsidian_note.py`，把分类和写入流程脚本化。
6. 新增 `evals/trigger-evals.json`，补齐触发边界评估入口。

剩余重点：

1. 对至少 8 个核心场景跑一次人工评估。
2. 根据评估结果优化 `description` 和误触发/漏触发边界。
3. 把常见失败案例沉淀进 references。
4. 发布一个稳定版本 tag。
