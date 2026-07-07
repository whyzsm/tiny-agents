# PPT 制作专家团

`$hr-ppt-creation` PPT 制作专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$hr-ppt-creation` | PPT 制作专家团总入口 |
| `$cn-ppt-outline-writer` | PPT大纲生成器，专为职场汇报、商业提案、演讲PPT提供结构设计与内容生成。触发场景：用户提到" |
| `$powerpoint-pptx` | Create, inspect, and edit Microsoft PowerPoint p |
| `$mck-ppt-design` | Create professional, consultant-grade PowerPoint |
| `$ppt-from-template` | Generate presentations by extracting visual styl |
| `$ppt` | 将用户讲稿一键生成乔布斯风极简科技感竖屏HTML演示稿。当用户需要生成PPT、演示文稿、Slid |
| `$dragon-ppt-maker` | ppt-maker skill. Dragon PPT Maker skill from the |

## 我可以帮你做这些

你现在要完成一项 PPT 演示文稿的制作任务。你已安装以下 Skill，请按步骤串联使用：

1. PPT 大纲与结构规划（获取层）

   使用 **CN PPT Outline Writer** 完成：
   - 根据演示主题生成 PPT 大纲和页面结构
   - 规划每页的核心信息和叙事逻辑
   - 设计演示文稿的整体故事线
   - 确定页数、章节划分和过渡方式
   - 支持生成 HTML 演示文稿预览

   输出 PPT 大纲和页面结构规划。

2. PowerPoint 文件全功能编辑（获取层）

   使用 **Powerpoint / PPTX** 完成：
   - 创建、检查和编辑 PPTX 文件
   - 配置幻灯片布局、模板和占位符
   - 添加演讲者备注和批注
   - 插入图表、表格和数据可视化
   - 执行视觉质检确保格式一致

   输出基础 PPTX 文件和布局配置。

3. 麦肯锡风格专业设计（分析层）

   使用 **Mck Ppt Design Skill** 完成：
   - 按麦肯锡咨询风格从零创建专业 PPT
   - 应用顾问级排版规范和配色方案
   - 设计数据驱动的图表和分析页面
   - 确保每页有明确的 Takeaway 信息
   - 输出高标准的商业演示文稿

   输出麦肯锡风格专业 PPT。

4. 模板风格提取与重建（分析层）

   使用 **PPT from Template** 完成：
   - 从参考模板中提取视觉风格（配色/字体/布局）
   - 使用 PptxGenJS 从头重新创建幻灯片
   - 保持品牌视觉一致性
   - 适配不同场景的模板需求（汇报/路演/培训）
   - 输出风格统一的演示文稿

   输出基于模板风格重建的 PPT。

5. 极简科技感演示稿生成（输出层）

   使用 **ppt** 完成：
   - 将讲稿一键生成乔布斯风极简科技感演示稿
   - 输出单个可直接运行的 HTML 文件
   - 支持竖屏和横屏两种模式
   - 自动排版和视觉设计
   - 适合科技产品发布、技术分享等场景

   输出极简科技感 HTML 演示文件。

6. 科技风多布局 PPT 制作（输出层）

   使用 **PPT制作** 完成：
   - 使用 python-pptx 制作科技风 PPT
   - 支持多种幻灯片布局和图文混排
   - 嵌入 HTML 内容和数据可视化
   - 生成可编辑的 .pptx 文件
   - 适合工作汇报、项目展示等正式场景

## 完整交付物通常是

```text
将以上步骤的结果整合为完整的 PPT 制作包，交付以下文件：
1. **PPT 大纲**：页面结构、叙事逻辑、章节划分
2. **基础 PPTX 文件**：布局配置、图表表格、备注批注
3. **麦肯锡风格 PPT**：顾问级设计、数据图表、Takeaway
4. **模板风格 PPT**：品牌一致性、视觉提取、风格重建
5. **极简科技感演示**：乔布斯风格、HTML 文件、一键运行
6. **科技风 PPTX 文件**：多布局、图文混排、可编辑格式
```

## 你可以这样用我

```text
$hr-ppt-creation 帮我完成一次PPT 制作，先判断需要哪些子技能
$hr-ppt-creation 根据这些资料生成完整交付物，并说明风险和假设
$hr-ppt-creation 只处理“PPT 大纲与结构规划（获取层）”，给出结果和下一步建议
$hr-ppt-creation 把“PowerPoint 文件全功能编辑（获取层）”的结果整理成可交付报告
```
