# 合同起草专家团

`$legal-contract-drafting` 合同起草专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$legal-contract-drafting` | 合同起草专家团工作流总入口 |
| `$employment-contract` | Draft and fill employment contract templates — offer letter, employment agreeme… |
| `$hetongzhushou` | 全能型合同管理工具，覆盖合同生成、审查、归档、风险识别、合规审查、条款对比、修改建议和结构化报告输出，适用于企业法务、个人签约和合同管理场景。… |
| `$legal-document-assistant` | 提供常见法律文书模板与撰写指导，涵盖劳务纠纷、离婚协议、交通事故、租房协议等场景；当用户需要法律文书模板、撰写建议或遇到法律纠纷时使用 |
| `$legal-doc-writer` | 中国财税法律文书起草助手。当用户需要起草、审查或修改法律文书时应使用本 Skill，包括：税务筹划报告、法律意见书、合同税务条款、税务行政复议申请书、税务行政… |
| `$nda` | Draft and fill NDA templates — mutual NDA, one-way NDA, confidentiality agreeme… |
| `$legal-advisor` | Generate legal templates for labor, consumer, rental, and traffic disputes. Use… |

## 我可以帮你做这些

1. employment-contract

   调用 `employment-contract`

   Draft and fill employment contract templates — offer letter, employment agreement, IP/inventions assignment (…

2. 合同智能助手 v1.0.3

   调用 `hetongzhushou`

   全能型合同管理工具，覆盖合同生成、审查、归档、风险识别、合规审查、条款对比、修改建议和结构化报告输出，适用于企业法务、个人签约和合同管理场景。…

3. legal-document-assistant

   调用 `legal-document-assistant`

   提供常见法律文书模板与撰写指导，涵盖劳务纠纷、离婚协议、交通事故、租房协议等场景；当用户需要法律文书模板、撰写建议或遇到法律纠纷时使用

4. legal-doc-writer

   调用 `legal-doc-writer`

   中国财税法律文书起草助手。当用户需要起草、审查或修改法律文书时应使用本 Skill，包括：税务筹划报告、法律意见书、合同税务条款、税务行政复议申请书、税务行政诉讼状、税务咨询报告、客户尽职调查报告、税务处理意见函等各类…

5. nda

   调用 `nda`

   Draft and fill NDA templates — mutual NDA, one-way NDA, confidentiality agreement. Produces signable DOCX fil…

6. Legal Advisor — Bilingual Enhanced Edition

   调用 `legal-advisor`

   Generate legal templates for labor, consumer, rental, and traffic disputes. Use when drafting dispute letters…

7. 端到端合同起草交付

   调用 `employment-contract`、`hetongzhushou`、`legal-document-assistant`、`legal-doc-writer`、`nda`、`legal-advisor`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的合同起草成果包。

## 完整交付物通常是

```text
合同模板：标准模板、框架文档、条款结构

专业合同：正文生成、法律审查、条款设计

撰写指南：文书模板、撰写指导、格式规范

财税文书：税务筹划、法律意见书、税务条款

NDA文件：双向/单向NDA、DOCX可签署文件

文书终稿：500+案例、标准格式、终稿输出
```

## 你可以这样用我

```text
$legal-contract-drafting 帮我起草一份合作协议，包含违约和争议解决条款

$legal-contract-drafting 根据这些素材生成 NDA 和服务协议初稿

$legal-contract-drafting 做一套合同模板和法律文书撰写指南

$legal-contract-drafting 起草一份税务相关法律意见书
```
