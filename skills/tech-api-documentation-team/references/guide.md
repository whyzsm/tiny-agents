# API 文档专家团

`$tech-api-documentation-team` API 文档工作流入口

图片中的 `tech-api-documentation-codex` 在本仓库映射为真实入口 `$tech-api-documentation-team`。

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$tech-api-documentation-team` | 完整 API 文档工作流总入口 |
| `$sovereign-api-docs-generator` | 从路由、控制器、Schema、GraphQL SDL 生成端点文档 |
| `$api-dev` | API 脚手架、验证、调试、mock、curl/scripts 与实现一致性检查 |
| `$api-doc-writer` | 面向开发者的 REST API Reference、参数、状态码和示例 |
| `$qa-api-tester` | 可执行请求、curl、pytest/requests、Postman、链式流程和 Schema 校验 |
| `$afrexai-api-docs` | OpenAPI 3.0 YAML/JSON、Markdown 文档、SDK 快速开始和多语言片段 |

## 我可以帮你做这些

1. API 契约设计

   调用 `tech-api-documentation-team` 的契约设计阶段

   设计 REST/GraphQL 资源模型、URL 命名、版本策略、认证授权、分页和错误格式。

2. 代码到文档提取

   调用 `sovereign-api-docs-generator`

   从路由、控制器、Schema、proto 或 GraphQL SDL 提取端点、参数、响应和示例。

3. API 实现验证

   调用 `api-dev`

   搭建、调试、mock 和验证接口，并检查实现行为与文档描述是否一致。

4. API Reference 写作

   调用 `api-doc-writer`

   编写端点说明、请求参数、响应结构、认证方式、状态码和示例请求。

5. 可执行 API 测试

   调用 `qa-api-tester`

   生成 curl、pytest/requests、Postman 集合、链式请求、Schema 校验和 mock 数据。

6. 最终文档包交付

   调用 `afrexai-api-docs`

   输出 OpenAPI 3.0、Markdown API 文档、SDK 快速开始、curl 示例和多语言代码片段。

## 完整交付物通常是

```text
API 设计规格

OpenAPI 3.0 YAML 或 JSON

Markdown API Reference

请求和响应示例

SDK Quickstart

curl、Postman 或 pytest 验证包
```

## 你可以这样用我

```text
$tech-api-documentation-team 为这组 REST 路由生成 OpenAPI 3.0 和 Markdown API 文档

$tech-api-documentation-team 设计一个用户、订单和支付 API，并包含分页、认证和错误格式

$tech-api-documentation-team 检查这些接口实现和现有文档是否一致，列出差异

$tech-api-documentation-team 为这个 API 输出 SDK 快速开始、curl 示例和 Postman 验证集合
```
