# 动态网页来源读取

Use this reference when a Web URL returns a thin HTML shell, JavaScript-rendered page, CMS page, or page whose visible content is stored in script variables or API responses.

## When To Use

Use this workflow if any of these are true:

- HTML title is generic but the page visibly should contain article or product content.
- HTML body mainly contains placeholders such as `<app-root>`, empty containers, or mount points.
- The page includes large encoded JSON strings, CMS layer data, `__NEXT_DATA__`, `window.__INITIAL_STATE__`, or similar script state.
- The page is a documentation center, developer portal, course page, or product site with client-side routing.

## Reading Order

1. Fetch the URL as normal HTML and extract title, meta description, canonical URL, headings, visible text, and links.
2. Run `scripts/extract_web_source.py --url URL --json` when local script execution is available.
3. If the script reports `encoded_json`, `script_state`, or `cms_text` content, use those extracted texts as source anchors.
4. If the script reports `spa_shell` or low text volume, inspect loaded JS for official API names such as `getDocumentById`, `getUrlMapping`, `getCatalogTree`, `content`, `article`, or `markdown`.
5. If API access is public and does not require credentials, call the official endpoint with the same origin and public request payload.
6. If content still cannot be read, use a real browser only to read visible public text. Do not scrape cookies, local storage, bearer tokens, or private headers.
7. If the source remains inaccessible, write a structured limitation instead of fabricating details.

## Source Quality Rules

- Treat meta description as a weak source: useful for topic and positioning, insufficient for detailed learning claims.
- Treat decoded CMS text as a source only when it comes from the requested page origin.
- Treat minified JS names and inferred API routes as discovery hints, not facts about the learning topic.
- Do not convert implementation guesses into source claims.
- Mark content as `access/public` only when it was read without private credentials.
- In the final note, explicitly say which source parts were readable: HTML, decoded CMS data, public API, browser-visible text, or user-provided export.

## Failure Language

When a page shell is readable but article text is not, use this limitation:

```markdown
- 页面是动态渲染或文档中心壳页面，直接 HTML 未暴露正文。
- 本笔记只使用已公开读取到的 HTML/CMS/API/可见文本。
- 未读取到的 API、参数、实现细节不做展开，后续需要用官方文档正文或用户导出补充。
```

## Do Not

- Do not summarize login pages, SSO pages, or permission errors as source content.
- Do not ask for passwords, 2FA codes, cookies, bearer tokens, authorization headers, or session storage.
- Do not claim a source was fully read when only meta tags or navigation text were available.
- Do not create a polished note from an empty shell unless the limitation is clearly stated and the note is scoped to what was actually read.
