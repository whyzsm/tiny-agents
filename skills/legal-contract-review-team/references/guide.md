# 合同审查专家团

`$legal-contract-review-team` 合同审查专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$legal-contract-review-team` | 合同审查专家团工作流总入口 |
| `$contract-review` | Legal contract analysis using CUAD dataset (41 risk categories). Supports NDA,… |
| `$contract-risk-reviewer` | 专业级合同风险审查工具，自动识别 20+ 类常见风险条款，给出修改建议和法律依据 |
| `$audit-new` | 合同风险识别与条款分析 - 智能合同审查工具，自动识别风险条款、补充缺失条款、对比差异条款 |
| `$contract-reviewer` | Review business contracts for risks, missing clauses, unfavorable terms, and co… |
| `$contract-guardian` | 合同卫士 — AI合同审查助手，识别风险条款、提取关键信息、追踪到期日 |
| `$contract-auditor` | 合同审计 Skill - AI 辅助审查合同条款，识别风险和问题 功能： - 自动提取合同文本（Word 格式） - 审查金额条款（一致性、付款节点、违约金）… |

## 我可以帮你做这些

1. contract-review

   调用 `contract-review`

   Legal contract analysis using CUAD dataset (41 risk categories). Supports NDA, SaaS, M&A, employment, payment…

2. contract-risk-reviewer

   调用 `contract-risk-reviewer`

   专业级合同风险审查工具，自动识别 20+ 类常见风险条款，给出修改建议和法律依据

3. contract-review

   调用 `audit-new`

   合同风险识别与条款分析 - 智能合同审查工具，自动识别风险条款、补充缺失条款、对比差异条款

4. contract-reviewer

   调用 `contract-reviewer`

   Review business contracts for risks, missing clauses, unfavorable terms, and compliance gaps. Use when analyz…

5. contract-guardian

   调用 `contract-guardian`

   合同卫士 — AI合同审查助手，识别风险条款、提取关键信息、追踪到期日

6. contract_auditor

   调用 `contract-auditor`

   合同审计 Skill - AI 辅助审查合同条款，识别风险和问题 功能： - 自动提取合同文本（Word 格式） - 审查金额条款（一致性、付款节点、违约金） - 审查交付条款（时间、标准、延期责任） - 审查合规性（…

7. 端到端合同审查交付

   调用 `contract-review`、`contract-risk-reviewer`、`audit-new`、`contract-reviewer`、`contract-guardian`、`contract-auditor`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的合同审查成果包。

## 完整交付物通常是

```text
风险扫描：41类CUAD风险、高风险条款清单

条款解读：智能识别、法律含义、咨询建议

缺失补充：风险条款、缺失条款、差异对比

深度审查：商业合同、合规漏洞、谈判清单

关键提取：核心条款、到期追踪、续签提醒

金额审计：金额一致性、付款节点、违约金评估
```

## 你可以这样用我

```text
$legal-contract-review-team 审查这份 SaaS 合同，标出风险条款和缺失条款

$legal-contract-review-team 提取合同金额、付款节点、违约金和到期日

$legal-contract-review-team 对比两版合同差异并给出风险说明

$legal-contract-review-team 生成合同审查报告和修订建议清单
```
