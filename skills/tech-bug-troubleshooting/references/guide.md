# BUG 排查专家团

`$tech-bug-troubleshooting` BUG 排查专家团

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$tech-bug-troubleshooting` | 端到端 BUG 排查工作流总入口 |
| `$log-analyzer` | 日志时间线、错误模式、请求 ID、首次失败点分析 |
| `$debug-pro` | 复现步骤、运行环境、最小可复现路径和隔离验证 |
| `$code-error-fixer` | 编译错误、运行时错误、类型错误、依赖错误和堆栈诊断 |
| `$superpowers-systematic-debugging` | 证据链、假设验证、根因定位和系统化调试纪律 |
| `$bug-fixing-openclaw` | 修复实现、影响面扫描、回归验证和修复报告 |
| `$nexus-error-explain` | 粘贴错误、堆栈信息和异常文本的本地解释 |

## 我可以帮你做这些

1. 日志与错误线索整理

   调用 `log-analyzer`

   从日志、时间戳、请求 ID、错误频率和首个异常中提取排查线索。

2. 复现与环境隔离

   调用 `debug-pro`

   确认失败命令、运行环境、输入条件和最小可复现步骤，区分环境问题与代码问题。

3. 堆栈与代码路径诊断

   调用 `code-error-fixer`

   解析编译、运行时、类型、依赖和堆栈错误，追踪异常值进入失败代码路径的来源。

4. 根因假设验证

   调用 `superpowers-systematic-debugging`

   建立证据链，为每个可能根因设计验证步骤，避免只在表象位置修补。

5. 修复与回归控制

   调用 `bug-fixing-openclaw`

   执行最小修复、扫描影响面、补充必要测试，并验证原始失败路径已恢复。

6. 单条错误快速解释

   调用 `nexus-error-explain`

   对粘贴的报错、异常文本或堆栈信息做本地解释，并给出下一步排查方向。

## 完整交付物通常是

```text
复现步骤和失败证据

日志时间线与关键错误模式

根因分析和验证依据

最小修复方案

影响面与回归风险说明

验证命令、测试结果和修复报告
```

## 你可以这样用我

```text
$tech-bug-troubleshooting 帮我排查这个接口 500，下面是日志和请求参数

$tech-bug-troubleshooting 这个测试突然失败了，请复现、定位根因并修复

$tech-bug-troubleshooting 分析这段堆栈，找出是哪条代码路径导致空指针

$tech-bug-troubleshooting 用多 agent 帮我排查这个线上回归，最后给出根因和验证结果
```
