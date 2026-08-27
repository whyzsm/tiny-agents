# Requirement Intake Adapter

This directory contains the Python + MCP adapter for requirement-link intake.

## What it does

- Keeps the existing screenshot, link, and copied-text entry types unchanged.
- Adds a link-based ingestion path that can read Yuque-like content through MCP.
- Normalizes the fetched content into a single requirement bundle for `lemon-product-agent`.

## What it does not do

- It does not write back to Yuque or any other source.
- It does not decide page type, component choice, or implementation scope.
- It does not replace screenshot or copied-text intake.

## Yuque URL auto-resolution

For a Yuque document URL shaped like:

```text
https://your-space.yuque.com/group/book/doc-slug
```

the adapter derives:

```text
repo_id = group/book
doc_id = doc-slug
tool    = yuque_get_doc
```

No specific requirement document URL is hard-coded.

You can inspect the resolved MCP call without contacting the MCP server:

```bash
python3 scripts/requirement-intake/mcp_requirement_source.py \
  --source-uri "https://your-space.yuque.com/group/book/doc-slug" \
  --print-fetch-plan
```

## Example

```bash
MCP_URL=http://127.0.0.1:3000/mcp \
python3 scripts/requirement-intake/mcp_requirement_source.py \
  --source-uri "https://your-space.yuque.com/group/book/doc-slug"
```

The script prints a normalized JSON bundle that can be fed into the requirement stage artifact.

If the MCP server exposes a different tool contract, keep using the explicit
tool fallback:

```bash
MCP_URL=http://127.0.0.1:3000/mcp \
python3 scripts/requirement-intake/mcp_requirement_source.py \
  --source-uri "https://requirements.example.com/items/123" \
  --tool-name "getRequirementDocument" \
  --tool-arguments '{"url":"https://requirements.example.com/items/123"}'
```
