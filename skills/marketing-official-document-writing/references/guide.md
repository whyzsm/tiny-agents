# 公文写作专家团

`$marketing-official-document-writing` 公文写作专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$marketing-official-document-writing` | 公文写作专家团工作流总入口 |
| `$official-doc-writer` | 通知、报告、请示、函等党政机关公文生成，符合 GB/T 9704-2012 标准 |
| `$official-writing` | 国家标准格式规范、公文模板、写作技巧和语言优化 |
| `$govwriter-pro` | 素材重构、主题创作、提纲扩写和体制内表达优化 |
| `$official-doc` | 公文格式检查、语气审查、模板匹配和专项校验 |
| `$docx-formatter` | 中国公文格式 Word 文档生成、标题样式、正文排版和标点处理 |
| `$doc-format-gw` | Word 公文终检排版、页边距、行距、字号、字体和版记检查 |

## 我可以帮你做这些

1. 公文类型判断和初稿生成

   调用 `official-doc-writer`

   根据事项判断通知、报告、请示、批复、函、会议纪要等文种，并生成标准初稿。

2. 格式规范和模板对标

   调用 `official-writing`

   对照 GB/T 9704-2012、对应文种模板和常用公文表达优化结构与语言。

3. 素材重构和正文优化

   调用 `govwriter-pro`

   基于原文素材重构，或根据主题、提纲、过往材料生成更完整的公文正文。

4. 格式和语气审查

   调用 `official-doc`

   检查标题、主送机关、正文、附件、落款、日期、语气和专项文种要求。

5. Word 文档生成

   调用 `docx-formatter`

   生成符合公文格式规范的 Word 文档，处理标题层级、字体样式、段落和中文标点。

6. 公文排版终检

   调用 `doc-format-gw`

   检查页边距、行距、字号、字体、页码、版记和打印输出前的排版一致性。

7. 端到端公文交付

   调用 `official-doc-writer`、`official-writing`、`govwriter-pro`、`official-doc`、`docx-formatter`、`doc-format-gw`

   从文种判断、正文生成、格式审查到 Word 排版终检完成完整公文交付。

## 完整交付物通常是

```text
公文初稿或正稿：通知、报告、请示、函、会议纪要等正式文本

内容优化说明：结构、逻辑、语气、表达和材料使用建议

格式检查报告：GB/T 9704-2012 对标、文种要素、落款和附件检查

Word 排版文件：标题层级、字体字号、行距、页边距、页码和版记设置

终检结论：可直接发送、需补充信息或需人工确认的风险点
```

## 你可以这样用我

```text
$marketing-official-document-writing 帮我写一份会议通知，要求符合公文格式

$marketing-official-document-writing 根据这些素材重构一份请示

$marketing-official-document-writing 检查这份报告的格式、语气和文种要素

$marketing-official-document-writing 把这份公文整理成标准 Word 排版
```
