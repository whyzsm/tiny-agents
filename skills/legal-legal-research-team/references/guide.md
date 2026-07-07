# 法规检索专家团

`$legal-legal-research-team` 法规检索专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$legal-legal-research-team` | 法规检索专家团工作流总入口 |
| `$legalkb` | 法律知识库检索技能。当用户需要查询法律法规、合同条款、司法解释时激活。触发词：搜一下法律、查一下这个条款、总结这份合同、法律咨询、法律问题、查法条。适配如意工… |
| `$case-research` | 中国财税法律案例与法规检索助手。当用户需要检索税务相关判例、行政复议决定、税收法规政策、国家税务总局公告、各地税务实践案例，或需要查找类似税务争议案例时，应使… |
| `$legal-hybrid-skill` | 合法合规类案与法条查询，优先API，失败自动降级本地库 |
| `$legal-system-mapper-mctmilk` | 以某个法条为核心节点，构建其上下游法条关联网络，包括上位规范、并列条款、下位细化、程序衔接、竞合分析。当用户想了解某个法条在法律体系中的位置时使用。 |
| `$legal-case-validator-mctmilk` | 用真实案例验证法条分析结果，分析司法实践中的裁判分歧、高频败诉原因和法官审查重点。AI生成的分析必须用真实案例验证。当用户想检验法条分析是否符合司法实践时使用。 |
| `$legal-concept-deep-dive-mctmilk` | 深入分析法条中的不确定法律概念（如"合理期限"、"重大误解"、"明显不当"）的内涵、外延、裁判标准和边界案例。当用户想穿透法条中模糊词汇的具体含义时使用。 |

## 我可以帮你做这些

1. legal-kb

   调用 `legalkb`

   法律知识库检索技能。当用户需要查询法律法规、合同条款、司法解释时激活。触发词：搜一下法律、查一下这个条款、总结这份合同、法律咨询、法律问题、查法条。适配如意工作台，即插即用。

2. case-research

   调用 `case-research`

   中国财税法律案例与法规检索助手。当用户需要检索税务相关判例、行政复议决定、税收法规政策、国家税务总局公告、各地税务实践案例，或需要查找类似税务争议案例时，应使用本 Skill。适用于税务争议应对、税务筹划合规性验证、法…

3. legal-hybrid-skill

   调用 `legal-hybrid-skill`

   合法合规类案与法条查询，优先API，失败自动降级本地库

4. legal-system-mapper-mctmilk

   调用 `legal-system-mapper-mctmilk`

   以某个法条为核心节点，构建其上下游法条关联网络，包括上位规范、并列条款、下位细化、程序衔接、竞合分析。当用户想了解某个法条在法律体系中的位置时使用。

5. legal-case-validator-mctmilk

   调用 `legal-case-validator-mctmilk`

   用真实案例验证法条分析结果，分析司法实践中的裁判分歧、高频败诉原因和法官审查重点。AI生成的分析必须用真实案例验证。当用户想检验法条分析是否符合司法实践时使用。

6. legal-concept-deep-dive-mctmilk

   调用 `legal-concept-deep-dive-mctmilk`

   深入分析法条中的不确定法律概念（如"合理期限"、"重大误解"、"明显不当"）的内涵、外延、裁判标准和边界案例。当用户想穿透法条中模糊词汇的具体含义时使用。

7. 端到端法规检索交付

   调用 `legalkb`、`case-research`、`legal-hybrid-skill`、`legal-system-mapper-mctmilk`、`legal-case-validator-mctmilk`、`legal-concept-deep-dive-mctmilk`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的法规检索成果包。

## 完整交付物通常是

```text
法规清单：法条检索、司法解释、适用规范

案例汇编：判例检索、法规政策、实践案例

纠纷法条：多类纠纷、官方API、法条查询

体系定位：关联网络、上下位法条、竞合分析

类案验证：真实案例、裁判分歧、败诉原因

概念分析：模糊概念、裁判标准、边界案例
```

## 你可以这样用我

```text
$legal-legal-research-team 检索这个劳动纠纷相关法条和司法解释

$legal-legal-research-team 帮我定位这个法律概念的裁判标准和边界案例

$legal-legal-research-team 做类案检索，验证高频败诉原因

$legal-legal-research-team 梳理上位规范、并列条款和程序衔接关系
```
