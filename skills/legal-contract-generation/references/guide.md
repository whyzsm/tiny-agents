# 合同生成专家团

`$legal-contract-generation` 合同生成专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$legal-contract-generation` | 合同生成专家团工作流总入口 |
| `$employment-contract` | Draft and fill employment contract templates — offer letter, employment agreeme… |
| `$legal-advisor` | Generate legal templates for labor, consumer, rental, and traffic disputes. Use… |
| `$contract-review-pro` | 合同风险识别与条款分析 - 智能合同审查工具，自动识别风险条款、补充缺失条款、对比差异条款 |
| `$nathan-legal-os-pro` | Comprehensive legal document automation for clause extraction, document summariz… |
| `$hetongzhushou` | 全能型合同管理工具，覆盖合同生成、审查、归档、风险识别、合规审查、条款对比、修改建议和结构化报告输出，适用于企业法务、个人签约和合同管理场景。… |
| `$legal-doc-writer` | 中国财税法律文书起草助手。当用户需要起草、审查或修改法律文书时应使用本 Skill，包括：税务筹划报告、法律意见书、合同税务条款、税务行政复议申请书、税务行政… |

## 我可以帮你做这些

1. employment-contract

   调用 `employment-contract`

   Draft and fill employment contract templates — offer letter, employment agreement, IP/inventions assignment (…

2. Legal Advisor — Bilingual Enhanced Edition

   调用 `legal-advisor`

   Generate legal templates for labor, consumer, rental, and traffic disputes. Use when drafting dispute letters…

3. contract-review

   调用 `contract-review-pro`

   合同风险识别与条款分析 - 智能合同审查工具，自动识别风险条款、补充缺失条款、对比差异条款

4. LegalDoc AI

   调用 `nathan-legal-os-pro`

   Comprehensive legal document automation for clause extraction, document summariz…

5. 合同智能助手 v1.0.3

   调用 `hetongzhushou`

   全能型合同管理工具，覆盖合同生成、审查、归档、风险识别、合规审查、条款对比、修改建议和结构化报告输出，适用于企业法务、个人签约和合同管理场景。…

6. legal-doc-writer

   调用 `legal-doc-writer`

   中国财税法律文书起草助手。当用户需要起草、审查或修改法律文书时应使用本 Skill，包括：税务筹划报告、法律意见书、合同税务条款、税务行政复议申请书、税务行政诉讼状、税务咨询报告、客户尽职调查报告、税务处理意见函等各类…

7. 端到端合同生成交付

   调用 `employment-contract`、`legal-advisor`、`contract-review-pro`、`nathan-legal-os-pro`、`hetongzhushou`、`legal-doc-writer`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的合同生成成果包。

## 完整交付物通常是

```text
合同正文：经过合规审查和风险优化的完整合同文本

风险报告：合同条款的风险识别结果和应对建议

附属文书（按需）：补充协议、签署指引或法律意见书
```

## 你可以这样用我

```text
$legal-contract-generation 帮我生成一份服务合同，并标出关键风险条款

$legal-contract-generation 根据这些商务条件起草合同正文和签署指引

$legal-contract-generation 生成劳动合同模板，并补充必要条款清单

$legal-contract-generation 输出合同正文、风险报告和附属文书
```
