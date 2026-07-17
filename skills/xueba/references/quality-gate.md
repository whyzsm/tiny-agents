# 学霸质量门禁

Use this reference before xueba claims a learning note, vault upgrade report, expert spec, or agent-boundary answer is complete.

The quality gate is not decoration. It prevents four common failures:

- shallow summaries that do not teach
- hallucinated or weakly sourced claims
- broken Obsidian saves
- expert-mode answers that blur skill, expert, and runtime-agent boundaries

## Universal Gate

Apply these checks to every xueba task:

| Check | Pass condition | Failure action |
|---|---|---|
| Mode selection | Study, Upgrade, Learning Expert, or Agent Design Mode is selected correctly | Reclassify before producing the final artifact |
| Source access | Access method is known: public, authenticated, exported, pasted, local, or blocked | Record limitation or request/export source |
| Source boundary | Login/no-permission/empty pages are not summarized as source text | Return structured failure |
| Certainty labels | Important source claims, inference, missing content, and uncertain content are separated | Add `原文依据`, `推论`, `待补充`, `待验证` |
| Final artifact | Output has a concrete note, report, prompt/spec, or boundary answer | Do not finish with only a plan |
| Temporary paths | Final reply does not present `/tmp`, `/private/tmp`, or generated-output drafts as durable saves | Report only the real final path, or mark draft explicitly |

## Study Note Gate

A Study Mode note passes only when:

- frontmatter includes `title`, `tags`, `source`, `created`
- tags include `status/*`, `type/system-note`, `domain/*`, `source/*`, `access/*`, `confidence/*`
- main headings are exactly:
  - `## 1. 全景`
  - `## 2. 概念`
  - `## 3. 正文`
  - `## 4. 练习`
  - `## 5. 来源`
- `全景` explains learning goals, prerequisites, topic map, core judgment, and what problem this knowledge solves
- `概念` uses `C001` style IDs when multiple reusable concepts exist
- concepts include aliases or English terms when useful, boundaries, common misconceptions, relationships, and source anchors
- `正文` covers Why, What, How, Limits, Evidence, and Links
- `练习` contains recall, explanation/Feynman, transfer, and real-task checks when relevant
- every exercise has a reference answer, scoring rule, or expected output
- `来源` includes source access method, confidence, limitations, AI-readable YAML, and quality checklist
- AI-readable YAML includes `summary`, `concepts`, `relations`, `keywords`, and `qa_pairs`

## Obsidian Save Gate

Claim "saved to Obsidian" only when:

- the live Obsidian vault has been resolved or explicitly provided
- the target directory is inside that vault
- the target path contains `88-学习/`
- the final path is a filesystem path, not an `obsidian://` deep link
- generated-output, current workspace, `/tmp`, and `/private/tmp` are not treated as final vaults unless the user explicitly provided such a directory and it contains `.obsidian`
- if Obsidian is not installed, the answer uses the official releases source `https://github.com/obsidianmd/obsidian-releases` and does not claim save success before installation and vault resolution succeed

## Upgrade Mode Gate

An Upgrade Mode report passes only when:

- scope is explicit: vault, folder, or selected files
- mode is explicit: report-only, propose-patches, or apply-edits
- report preserves original notes unless edits were requested
- findings include issue type, suggested action, impact, confidence, and effort
- recommendations distinguish weak source, missing tags, tag drift, orphan notes, duplicate concepts, concept candidates, MOC candidates, stale knowledge, and broken links when relevant
- final reply lists changed files only if edits were actually applied

## Learning Expert Gate

A Learning Expert Mode output passes only when it includes:

- expert identity and role anchor
- capability precheck
- six capability modules or a clear reference to them
- workflow from source access to final handoff
- delivery contract
- quality gate
- statement that ordinary xueba tasks stay single-expert by default
- no fake multi-agent execution unless the user explicitly asked for team design

## Agent Design Gate

An Agent Design Mode output passes only when it distinguishes:

- Skill
- Expert Mode
- Agent Object
- Local Runtime Harness
- Runtime Agent
- Multi-Agent Team

It must state that current xueba is a Codex Skill with Learning Expert Mode, Agent Object Layer, and Local Runtime Harness, but not a deployed autonomous runtime agent. Runtime-agent proposals must include identity, task schema, memory, tools, permissions, scheduler, evaluation, observability, deployment, and lifecycle.

## Local Eval Gate

Before release, run:

```bash
python3 scripts/run_evals.py --report-dir .xueba-eval-report
```

For a generated note, also run:

```bash
python3 scripts/run_evals.py --note /path/to/generated-note.md
```

The release should not be called stable while deterministic checks fail.
