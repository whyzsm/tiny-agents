# 诉讼策略专家团

`$legal-litigation-strategy` 诉讼策略专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$legal-litigation-strategy` | 诉讼策略专家团工作流总入口 |
| `$court-prep` | Court Preparation Tool. Use when you need court prep capabilities. Triggers on:… |
| `$ai-legal-assistant-pro` | China legal triage assistant. Input a contract, labor dispute facts, lawsuit-co… |
| `$litigation-response` | 解析起诉状内容，提炼争议焦点，制定系统化应诉策略；当收到原告起诉状需要梳理诉讼思路、分析法律关系或制定答辩方向时使用 |
| `$pro-legal-strategist-v2` | 顶级诉讼律师与案件分析专家，执行七步分析法与证据矩阵建模。 |
| `$complaint-drafting` | 从聊天记录中提取案情要素和证据材料，生成规范的民事起诉状；当用户需要制作起诉状、梳理诉讼材料、整理案件事实时使用 |
| `$legal-advisor` | Generate legal templates for labor, consumer, rental, and traffic disputes. Use… |

## 我可以帮你做这些

1. Court Prep Guide

   调用 `court-prep`

   Court Preparation Tool. Use when you need court prep capabilities. Triggers on: court prep.

2. ai-legal-assistant-pro

   调用 `ai-legal-assistant-pro`

   China legal triage assistant. Input a contract, labor dispute facts, lawsuit-cost question, or draft legal do…

3. litigation-response

   调用 `litigation-response`

   解析起诉状内容，提炼争议焦点，制定系统化应诉策略；当收到原告起诉状需要梳理诉讼思路、分析法律关系或制定答辩方向时使用

4. 法律

   调用 `pro-legal-strategist-v2`

   顶级诉讼律师与案件分析专家，执行七步分析法与证据矩阵建模。

5. complaint-drafting

   调用 `complaint-drafting`

   从聊天记录中提取案情要素和证据材料，生成规范的民事起诉状；当用户需要制作起诉状、梳理诉讼材料、整理案件事实时使用

6. Legal Advisor — Bilingual Enhanced Edition

   调用 `legal-advisor`

   Generate legal templates for labor, consumer, rental, and traffic disputes. Use when drafting dispute letters…

7. 端到端诉讼策略交付

   调用 `court-prep`、`ai-legal-assistant-pro`、`litigation-response`、`pro-legal-strategist-v2`、`complaint-drafting`、`legal-advisor`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的诉讼策略成果包。

## 完整交付物通常是

```text
诉讼准备：流程指引、文书清单、时间线、费用估算

风险评估：合同风险、纠纷分析、成本估算、路径对比

应诉策略：争议焦点、法律关系、答辩方向、薄弱环节

证据矩阵：七步分析、证据映射、证明力评估、补强方向

诉讼文书：民事起诉状、证据清单、法律依据

综合策略：全流程支持、多维分析、最终策略建议
```

## 你可以这样用我

```text
$legal-litigation-strategy 帮我梳理这个案件的争议焦点和应诉策略

$legal-litigation-strategy 根据这些证据做证据矩阵和诉讼时间线

$legal-litigation-strategy 估算诉讼成本并生成文书骨架

$legal-litigation-strategy 起草一份民事起诉状并列出材料清单
```
