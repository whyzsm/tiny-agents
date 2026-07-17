# 登录与授权资料处理

Use this reference for Feishu, Notion, Yuque, DingTalk, private wiki, LMS, Google Docs, internal docs, and any source that returns a login page, no-permission page, SSO page, empty app shell, or JavaScript shell without document text.

## Core Rule

Do not summarize the login page. Do not fabricate source content. Treat authenticated sources as normal inputs that require a safe access path.

## Access Ladder

1. **Public fetch**: try normal URL access and verify the result contains the real document title and body, not just login/loading/app-shell text.
2. **Official export or API**: if a platform connector, CLI, MCP, or official API is available and authorized, export Markdown, HTML, PDF, DOCX, or plain text.
3. **Logged-in browser, visible text only**: if a browser tool is available and the user is already logged in, ask permission to read the visible document content. Do not inspect cookies, local storage, passwords, session files, or hidden tokens.
4. **User-assisted export**: ask the user to export or paste the source. Prefer Markdown, PDF, DOCX, HTML, or copied page body. Use screenshot OCR only when text export is impossible.
5. **Structured failure**: if authorized content cannot be obtained, return or save a blocked-source note with exact access state and next action.

## Security Rules

- Never ask for passwords, 2FA codes, cookies, bearer tokens, authorization headers, or session storage.
- Never attempt to bypass SSO, paywalls, ACLs, tenant restrictions, robots controls, or document permissions.
- Never store raw credentials in notes.
- If an API token is already configured in a tool or environment, use it without printing it. Otherwise ask for an export rather than a secret.

## Access Tags

Use the appropriate `access/*` tag:

- `access/public`
- `access/authenticated`
- `access/exported`
- `access/pasted`
- `access/blocked`

For authenticated notes, include a source line under `## 5. 来源`:

```markdown
- 来源访问方式：`access/authenticated`，通过用户已登录浏览器读取可见正文；未读取 cookies/localStorage。
```

For blocked notes, use:

```markdown
- 来源访问方式：`access/blocked`，当前只获得登录/无权限页面，未取得正文；需要用户提供导出文件或授权可见正文。
```

## Failure Note

If no authorized content is available, create one coherent failure note instead of a fake study note:

```markdown
---
title: "无法学习：[主题或链接]"
tags:
  - status/seed
  - type/system-note
  - domain/unknown
  - source/private-wiki
  - access/blocked
  - confidence/low
source: "[url]"
created: "YYYY-MM-DD"
---

# 无法学习：[[主题或链接]]

## 1. 全景
- 当前状态：只取得登录页、无权限页或空壳页面。
- 不生成内容总结，因为没有取得正文。

## 2. 概念
- `[[授权访问]]`：需要用户或平台授予读取权限后才能学习正文。

## 3. 正文
### Why：为什么无法学习
### What：当前拿到的内容是什么
### How：下一步如何提供资料
### Limits：不会做什么

## 4. 练习
- 暂不生成学习练习；先补充正文。

## 5. 来源
### 来源与可信度
- 来源访问方式：`access/blocked`
- 可信度：低，因为未取得正文。
```
