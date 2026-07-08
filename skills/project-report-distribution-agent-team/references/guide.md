# 报告分发代理

`$project-report-distribution-agent-team` 报告分发代理总入口

## 来源说明

- WorkBuddy 分类：项目质量
- WorkBuddy 卡片：报告分发代理
- 作者/来源：送报报
- 卡片摘要：自动化管理报告生成和分发流程。
- 标签：报告分发、自动投递、格式转换
- 提取状态：截图卡片可见专家名、作者、摘要和标签；本地 WorkBuddy marketplace 包未包含完整专家详情 payload。

## 触发的能力

| 能力模块 | 能力 |
|---|---|
| `project-report-distribution-agent-intake` | 需求/资料/上下文收集与边界确认 |
| `project-report-distribution-agent-strategy` | 策略、方案、路径与优先级设计 |
| `project-report-distribution-agent-execution` | 执行计划、脚本、流程和操作建议 |
| `project-report-distribution-agent-quality` | 质量、风险、合规和可验证性检查 |
| `project-report-distribution-agent-measurement` | 指标、效果、证据和复盘分析 |
| `project-report-distribution-agent-handoff` | 交付物整理、下一步动作和沉淀模板 |

## 与已有专家团的边界

| 已有专家团 | 主要关系 |
|---|---|
| `expert-team-index` | 本入口按 WorkBuddy 卡片独立保留；若用户任务明显落入已有更窄专家团，应优先路由到更窄入口。 |

## 我可以帮你做这些

1. 场景和目标澄清

   围绕 `报告分发代理` 的任务目标、输入材料、使用场景、约束和交付格式做快速澄清。

2. 策略和方案设计

   根据卡片能力标签：报告分发、自动投递、格式转换，形成可执行策略、方案、流程或内容结构。

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
$project-report-distribution-agent-team 帮我完成一个报告分发代理任务，并输出可执行方案
$project-report-distribution-agent-team 根据这些材料生成报告分发相关的检查清单和交付物
```
