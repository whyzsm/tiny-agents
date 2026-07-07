# 论文检索专家团

`$academic-paper-search` 论文检索专家团总入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$academic-paper-search` | 论文检索专家团工作流总入口 |
| `$academic-research-hub` | Use this skill when users need to search academic papers, download research documents,… |
| `$literature-search` | Find and compile academic literature with citation lists across Google Scholar, PubMed,… |
| `$deepxiv-cli` | Search, inspect, and progressively read open-access academic papers with the deepxiv CL… |
| `$research-paper-monitor` | 科研文献智能监测与摘要推送系统。自动监测多个学术信源（arXiv、PubMed、CNKI等），根据用户关注的领域和关键词采集最新论文，生成中文摘要并推送。适用于需要跟踪学术前… |
| `$cnki-advanced-search` | 知网（CNKI）高级检索论文自动化工具。当用户提供研究关键词（一组或多组）时，自动在知网 高级检索页面模拟人类检索行为：选择学术期刊类别、勾选CSSCI来源、输入主题关键词（… |
| `$academic-citation-manager` | Add real references and standardize citations for research papers and theses (为科研论文和毕业论… |

## 我可以帮你做这些

1. Academic Research Hub

   调用 `academic-research-hub`

   Use this skill when users need to search academic papers, download research documents, extract citations, or gather scholarly information. Triggers include: requests to "find papers on", "search research about", "download academic articles", "get citations for", or any request involving academic databases like arXiv, PubMed, Semantic Sch…

2. Literature Search

   调用 `literature-search`

   Find and compile academic literature with citation lists across Google Scholar, PubMed, arXiv, IEEE, ACM, Semantic Scholar, Scopus, and Web of Science. Use for requests like “find related literature,” “related work,” “citation list,” or “key papers on a topic.”

3. DeepXiv CLI

   调用 `deepxiv-cli`

   Search, inspect, and progressively read open-access academic papers with the deepxiv CLI. Use when the user wants arXiv / PMC / Semantic Scholar paper search, paper triage, section-by-section reading, trending discovery, citation lookup, author background checks, baseline comparison, or literature review workflows without loading full pa…

4. 科研文献智能监测与摘要推送系统

   调用 `research-paper-monitor`

   科研文献智能监测与摘要推送系统。自动监测多个学术信源（arXiv、PubMed、CNKI等），根据用户关注的领域和关键词采集最新论文，生成中文摘要并推送。适用于需要跟踪学术前沿的科研工作者、研究生、教师等。使用场景包括：(1) 定时监测特定研究领域的最新论文，(2) 根据关键词筛选高相关度论文，(3) 自动生成论文中文摘要，(4) 接收每日/每周文献推送（需配置飞书渠道）。

5. 知网高级检索论文工具

   调用 `cnki-advanced-search`

   知网（CNKI）高级检索论文自动化工具。当用户提供研究关键词（一组或多组）时，自动在知网 高级检索页面模拟人类检索行为：选择学术期刊类别、勾选CSSCI来源、输入主题关键词（含同义词 和同位词，用 + 连接）、多组关键词用OR关系连接，检索后按被引量排序、切换50条/页、 打开摘要视图，最终通过"导出与分析"功能以"查新（引文格式）"导出为Word文件， 包含完整的题录和摘要信息。 触发条件：用户提到需要在知网/CNKI检索论文、高级检索、按关键词搜索CSSCI/C刊论文、 下载题录信息、获取论文摘要、按被引排序检索；或说"帮我在知网检索XX相关论文"、 "用知网高级检索搜索XX主题的C刊论文"、"帮我检索XX关键词的CSSCI论文"。

6. Academic Citation Manager | 学术引用管理器

   调用 `academic-citation-manager`

   Add real references and standardize citations for research papers and theses (为科研论文和毕业论文添加真实参考文献并规范引用标注)

7. 端到端论文检索交付

   调用 `academic-research-hub`、`literature-search`、`deepxiv-cli`、`research-paper-monitor`、`cnki-advanced-search`、`academic-citation-manager`

   先识别任务类型和关键输入，再按需串联子技能，输出可执行、可审查、可复用的论文检索成果包。

## 完整交付物通常是

```text
多数据库检索结果：文献列表、摘要、引用次数

跨平台系统检索：IEEE/ACM/Scopus 补充文献

批量下载文件：PDF 文件、元数据索引

文献监测报告：最新论文、中文摘要、推送配置

知网检索结果：CSSCI 文献、中文核心期刊

规范引用清单：参考文献列表、BibTeX、格式校验
```

## 你可以这样用我

```text
$academic-paper-search 帮我检索多模态大模型评测相关论文，并整理关键文献清单

$academic-paper-search 监测最近一周 arXiv 和 PubMed 上关于具身智能的论文

$academic-paper-search 生成 GB/T 7714 格式参考文献和 BibTeX
```
