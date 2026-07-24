---
name: screenshot-ui-prompt
description: "此技能用于：用户上传 UI 截图并希望生成精准、可直接复制的 AI 提示词（用于 v0、Lovable、Cursor、CodeBuddy、图像生成器等）以复刻该界面。它先识别截图属于前端元素（组件 / 页面 / 区块）还是非前端元素（流程图、图表、照片、文档），再确认使用设计令牌还是从图片提取配色，最后输出包含显式风格词的完整 UI/UX 交互设计提示词。触发场景：把这张图写成提示词、根据截图生成组件提示词、describe this UI as a prompt、screenshot to prompt。"
---

# Screenshot → UI Prompt Generator

## Overview

Turn a screenshot into a precise, structured AI prompt that recreates the UI. The skill enforces a
three-phase flow: **classify → gather design constraints → emit prompt**, and always includes an
explicit **风格词 (style words)** section so the generated prompt carries visual authority, not just
structure.

## When to Use

- User uploads an image and asks to "write a prompt", "generate a component/page prompt", or "describe
  this UI for an AI builder".
- User pastes a screenshot and wants a spec they can feed to v0 / Lovable / Cursor / CodeBuddy / image
  generators.
- Do NOT use for pure code review, or when the user only wants a verbal description (use normal reply).

## Preconditions

- The executing model MUST support vision (image input). If the model reports it cannot read images,
  stop and tell the user to switch to a multimodal model before proceeding.
- The screenshot must be available as a local file path. If the user only pasted a remote URL, download
  or fetch it locally first (e.g., via WebFetch / curl) before running the color-extraction script.

## Workflow

### Phase 1 — Analyze & Classify

1. Read the image. Identify concrete design elements: controls (button, input, dropdown, select,
   switch, tab, table, card, modal, filter builder, etc.), layout regions, typography, spacing, borders,
   shadows, rounded corners, icons.
2. Classify the screenshot into one of:
   - **组件 (component)** — a single reusable control or small composite (e.g., the filter builder from
     the example).
   - **区块 (section)** — a meaningful part of a page (header bar, sidebar, settings panel).
   - **页面 (page)** — a full screen with navigation + content + (optional) footer.
   - **非前端元素 (non-front-end)** — flowchart, mind map, org chart, photo, scanned document,
     illustration, logo, pure data chart with no UI chrome.
3. If classified as **non-front-end**, STOP and ask the user with the available user-input tool
   (or a concise plain-text question if no structured tool is available):
   - Explain what the image appears to be (e.g., "这看起来是一张流程图/照片/文档，不是前端 UI 元素").
   - Offer options: (a) 仍然按 UI 提示词输出（当作参考视觉）; (b) 改为描述/提取该内容本身;
     (c) 用户提供一张真正的前端截图。 Do NOT guess silently.
4. If front-end, summarize the classification briefly to the user (one line) and proceed to Phase 2.

### Phase 2 — Gather Design Constraints

Ask the user once, bundling up to two questions if the interface supports structured user input:

**Q1 — Design tokens vs. color extraction:**
- "我提供设计令牌 (Design Tokens)" — user will paste CSS variables / JSON / theme; use them verbatim.
- "从图片提取配色" — run `scripts/extract_colors.py IMAGE_PATH` to get dominant colors + a palette
  with exact hex, then use those values.
- "两者结合" — user provides tokens AND you refine/verify with extracted colors.
- "使用参考风格" — skip exact tokens; use a named reference style (see Q2 / style library).

**Q2 — Style reference (风格词):** offer a few from `references/prompt_templates.md` §风格词库, e.g.:
- 金融终端极简 (Goldman Sachs / Bloomberg): 深蓝 #0A2540, 灰白底, 像素级对齐, 高密低噪.
- Apple HIG / 现代简洁.
- Ant Design / 企业后台.
- Linear / 暗色科技.
- 用户自定义 (让用户输入风格描述).
If the user already gave style words in their message, skip this question and use theirs.

Record the chosen constraints; if "从图片提取配色" was chosen, execute the extraction script now and
capture the hex palette into the prompt.

### Phase 3 — Emit the Prompt

1. Load `references/prompt_templates.md` and pick the matching template by Phase-1 classification
   (组件 / 区块 / 页面). Fill every placeholder with the classified elements and Phase-2 constraints.
2. The emitted prompt MUST contain these sections, in order:
   - **风格词 (Style words)** — explicit visual authority (reference style + primary color + background
     + quality traits + vibe + UX goal). Never omit this section.
   - **布局 / 结构** — regions, toolbar, panel, grid.
   - **组件 / 页面要素** — the identified controls, with their states.
   - **配色 / 设计令牌** — exact hex from tokens or extraction.
   - **字体 / 排版** — family, sizes, monospace for numbers if density matters.
   - **交互** — hover/focus/click, add/delete rules, AND/OR, empty states.
   - **技术栈** — React + TS + Tailwind (or named lib), component name, controlled props.
3. Output the prompt in **Chinese first**, then provide an **English version** (for v0 / Lovable / 国际
   工具). Wrap each in a fenced code block so the user can copy directly.
4. After emitting, offer next steps: "要我直接生成该组件/页面的代码预览吗？" or "要补一份纯设计稿提示词吗？"

## Output Quality Rules

- Always include the **风格词** section — a prompt with only structure is weak; visual authority comes
  from explicit style words.
- Use exact hex values, never vague color names, when tokens/extraction are available.
- Keep prompts self-contained and copy-pasteable; no markdown outside the code fences for the prompt body.
- Preserve the source language of the user's request for the primary version.

## Resources

### scripts/extract_colors.py
Deterministic dominant-color + palette extractor. Run:
`python3 scripts/extract_colors.py IMAGE_PATH [--colors N]`
Outputs a ranked palette with hex, RGB, and an approximate role label (background / surface / primary /
text / accent). Requires Pillow; if it is missing, ask before installing dependencies. Use it in Phase
2 when the user chooses "从图片提取配色".

### references/prompt_templates.md
Ready-to-fill prompt templates for 组件 / 区块 / 页面, plus a 风格词库 (style-word library) with
concrete examples (financial-terminal, Apple HIG, Ant Design, Linear, etc.). Load this in Phase 3.
