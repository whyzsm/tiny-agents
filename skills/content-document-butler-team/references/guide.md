# 文档管家

`$content-document-butler-team` 文档管家总入口

## 来源说明

- WorkBuddy 分类：内容创作
- WorkBuddy 卡片：文档管家
- 作者/来源：金山文档文档管家助手
- 卡片摘要：支持新建、搜索、分类整理、分享授权和内容读取。
- 标签：文档创建、智能整理、文档搜索
- 提取状态：截图卡片可见专家名、作者、摘要和标签；本地 WorkBuddy marketplace 包未包含完整专家详情 payload。

## 触发的能力

| 能力模块 | 能力 |
|---|---|
| `content-document-butler-intake` | 需求/资料/上下文收集与边界确认 |
| `content-document-butler-strategy` | 策略、方案、路径与优先级设计 |
| `content-document-butler-execution` | 执行计划、脚本、流程和操作建议 |
| `content-document-butler-quality` | 质量、风险、合规和可验证性检查 |
| `content-document-butler-measurement` | 指标、效果、证据和复盘分析 |
| `content-document-butler-handoff` | 交付物整理、下一步动作和沉淀模板 |

## 与已有专家团的边界

| 已有专家团 | 主要关系 |
|---|---|
| `expert-team-index` | 本入口按 WorkBuddy 卡片独立保留；若用户任务明显落入已有更窄专家团，应优先路由到更窄入口。 |

## 我可以帮你做这些

1. 场景和目标澄清

   围绕 `文档管家` 的任务目标、输入材料、使用场景、约束和交付格式做快速澄清。

2. 策略和方案设计

   根据卡片能力标签：文档创建、智能整理、文档搜索，形成可执行策略、方案、流程或内容结构。

3. 执行和产物生成

   输出脚本、清单、表格、报告、方案、检查项、模板或操作步骤，避免只给泛泛建议。

4. 质量和风险检查

   检查事实、数据、合规、效果、边界条件和可验证证据，标注风险和待确认事项。

5. 复盘和下一步

   给出指标、验证方法、迭代建议和后续动作，让结果能继续推进。

## 完整交付物通常是

```text
任务背景和目标
关键假设和输入材料
策略/方案/流程
执行清单或可直接使用的内容
质量、风险和证据检查
下一步动作和复盘指标
```

## 你可以这样用我

```text
$content-document-butler-team 帮我完成一个文档管家任务，并输出可执行方案
$content-document-butler-team 根据这些材料生成文档创建相关的检查清单和交付物
```
