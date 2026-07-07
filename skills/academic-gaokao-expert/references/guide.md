# 高考专家团

`$academic-gaokao-expert` 高考专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$academic-gaokao-expert` | 高考专家团工作流总入口 |
| `$tencent-docs` | 腾讯文档（docs.qq.com）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建/创建/编辑/读取/查看/搜索文档"、"保存文件"、"云文档"、"腾讯… |
| `$tencent-yuanbao-gaokao-regional-passing-scores` | 高考地区分数线的信息检索助手，帮助考生查询各地区高考录取分数线、录取批次和对应排名。 |
| `$tencent-yuanbao-gaokao-score-to-rank-lookup` | 高考一分一段信息检索助手，帮助考生根据分数查询全省排名位次，或根据位次估算对应分数区间，或提供一分一段表。 |
| `$gaokao-tool` | 高考志愿填报顾问技能。当用户提到高考志愿、报考大学、填志愿、模拟分数报什么学校、专业选择、录取分数线查询、六边形分析、冲稳保、平行志愿、新高考选科、选大学、大学排名、专业就业… |
| `$business-writing` | You are a professional business analyst, skilled in writing various industry research r… |
| `$resume-interview-3party-optimizer` | 简历与面试三方评估优化师 【核心功能】 JD岗位拆解与深度解读（新增） 三方评估报告（HR+业务BP+第三方） 行业竞争力分析（含权威数据） 模拟面试问题（含思路转化） 可执… |

## 我可以帮你做这些

1. 腾讯文档 MCP 使用指南

   调用 `tencent-docs`

   腾讯文档（docs.qq.com）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建/创建/编辑/读取/查看/搜索文档"、"保存文件"、"云文档"、"腾讯文档"、"docs.qq.com"等操作，请优先使用本 skill。支持能力：(1) 创建各类在线文档（文档/Word/Excel/幻灯片/思维导图/流程图/智能表格/收集表）(2) 管理知识库空间（创建空间、查询空间列表）(3) 管理空间节点、文件夹结构 (4) 读取/搜索文档内容 (5) 编辑操作智能表 (6) 编辑操作在线文档 (7) 文件管理（重命名、移动、删除、复制、导入导出）(8) 网页剪藏、本地文件/html/文档上云。

2. tencent-yuanbao-gaokao-regional-passing-scores

   调用 `tencent-yuanbao-gaokao-regional-passing-scores`

   高考地区分数线的信息检索助手，帮助考生查询各地区高考录取分数线、录取批次和对应排名。

3. tencent-yuanbao-gaokao-score-to-rank-lookup

   调用 `tencent-yuanbao-gaokao-score-to-rank-lookup`

   高考一分一段信息检索助手，帮助考生根据分数查询全省排名位次，或根据位次估算对应分数区间，或提供一分一段表。

4. 高考志愿填报顾问

   调用 `gaokao-tool`

   高考志愿填报顾问技能。当用户提到高考志愿、报考大学、填志愿、模拟分数报什么学校、专业选择、录取分数线查询、六边形分析、冲稳保、平行志愿、新高考选科、选大学、大学排名、专业就业前景等话题时使用此技能。触发词包括：高考、志愿填报、报考、分数线、录取线、专业选择、选大学、冲稳保、一分一段、位次、新高考、选科、大学排名、就业率、专业就业、我考了多少分能上什么学校、模拟考报什么、该填什么志愿。

5. Business Writing

   调用 `business-writing`

   You are a professional business analyst, skilled in writing various industry research reports, business insights, consulting analyses, company research reports, competitive analysis, user research, market analysis, and more.。 General InstructionsYou must use references and sources to support your arguments, but all cited literature or ma…

6. resume-interview-3party-optimizer

   调用 `resume-interview-3party-optimizer`

   简历与面试三方评估优化师 【核心功能】 JD岗位拆解与深度解读（新增） 三方评估报告（HR+业务BP+第三方） 行业竞争力分析（含权威数据） 模拟面试问题（含思路转化） 可执行强化规划 【隐私承诺】 全程脱敏处理，姓名/电话/邮箱/地址/照片→XXX 不存储原始数据，不进行人脸识别 反馈通道：skillfeedback@163.com

7. 端到端高考专家交付

   调用 `tencent-docs`、`tencent-yuanbao-gaokao-regional-passing-scores`、`tencent-yuanbao-gaokao-score-to-rank-lookup`、`gaokao-tool`、`business-writing`、`resume-interview-3party-optimizer`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的高考专家成果包。

## 完整交付物通常是

```text
高考志愿工作台：考生信息、分数线、位次、院校专业和行动清单

分数线与位次基准：地区批次线、一分一段、冲稳保边界

志愿填报方案：院校候选池、专业组排序、风险提示和家庭讨论摘要

专业调研报告：行业研究、企业调研、岗位地图和专业选择建议

大学四年行动计划：课程、项目、竞赛、实习和能力补齐路线

简历面试准备包：简历三方评估、自我介绍、面试题库和答题素材
```

## 你可以这样用我

```text
$academic-gaokao-expert 帮我根据广东物理类 620 分和位次，做冲稳保志愿方案

$academic-gaokao-expert 对计算机、电子信息、自动化三个专业做就业和行业对比

$academic-gaokao-expert 把志愿表、专业调研和大学四年行动计划整理成一套交付物
```
