# Expert Team Conversion Guide

Use this guide when the user provides an external expert package and wants it converted into this repository's expert-team format.

## Conversion Goal

Create a repository-native expert team that can be discovered and invoked by Codex:

- The expert team is a top-level skill package under `skills/`.
- Child entries are classified into one of three repository-supported modes: all real top-level skills, hybrid real skills plus internal labels, or router-internal labels only.
- The expert team router coordinates child skills and/or internal capability labels; it does not vendor a plugin runtime or preserve persona-only agents.
- The registry and expert-team catalog show the final team entry and its child names, with the router explaining which entries are callable top-level skills.

## Source Inventory

Inspect the source package in this order:

1. Manifest files: `.codebuddy-plugin/plugin.json`, `plugin.json`, `settings.json`, package metadata, or marketplace card JSON.
2. Human docs: `README.md`, usage examples, workflow docs, visible card summaries, or screenshots.
3. Team members: `agents/*.md`, `prompts/*.md`, role files, or visible expert cards.
4. Nested skills: `skills/*/SKILL.md`, `skills/*/skill.md`, scripts, assets, and references.
5. Ignore by default: avatars, preview images, local install files, runtime caches, logs, lockfiles, temporary reports, and hidden prompt claims not present in the package.

Record only sanitized provenance such as `user-provided/<package-name>` or `repo-local/<source-family>`. Do not write local absolute paths into generated files.

## Name And Category

Choose names with these rules:

- Use lowercase hyphen-case.
- Keep package names at or below 64 characters.
- Preserve the source package's public name when it is already short and meaningful, such as `design-engine`.
- Use a `-team` suffix when the name would otherwise collide with a child skill or when the repository already uses that family pattern.
- Pick the expert-team category from existing `indexes/expert-team-file-list.md` categories. If unclear, infer from the source domain and state the assumption.

## Child Entry Resolution

Resolve each child entry before writing the expert-team router:

1. Build a candidate list from source nested skills and expert/agent files.
2. For each candidate, extract capability, trigger phrases, inputs, outputs, and success criteria. Strip persona wording.
3. Search `indexes/skill-registry.md` and `indexes/skill-registry.json` by name and capability keywords.
4. Search `skills/*/SKILL.md` only when the registry is stale or unclear.
5. Reuse an existing top-level skill if it materially matches the candidate's capability and output contract.
6. Create a new top-level child skill only when the source child is reusable as a standalone capability or the user explicitly asks for callable child skills.
7. Preserve a child as an internal router label when it is a team-specific phase, role, agent persona, or partial workflow that would be misleading as a standalone skill.
8. If two or more existing skills could match, report the conflict and ask only when the mapping affects the final behavior.

Do not claim an internal label is callable as `$<child-name>`. In hybrid or internal-label mode, the router must say that the label is handled inside the expert-team flow.

## Team Modes

Use the mode that matches the source and repository evidence:

| Mode | Meaning | When to use |
|---|---|---|
| `all-top-level-skills` | Every child entry resolves to `skills/<name>/SKILL.md` or `skills/<name>/skill.md`. | Harmony-style teams and curated routers that coordinate existing callable skills. |
| `hybrid` | Some child entries resolve to top-level skills and some remain team-local labels. | Imported packages that overlap existing repository skills but also contain source-specific stages or role labels. |
| `internal-router-labels` | No child entry is a top-level skill; all child names are router-internal labels. | WorkBuddy/CodeBuddy cards, team-lead packages, or expert folders whose members are not safe standalone capabilities. |

Record the selected mode in `references/guide.md` for the converted package. If practical, include a small mapping table:

| Child entry | Kind | Maps to | Notes |
|---|---|---|---|
| `example-skill` | `top-level-skill` | `skills/example-skill/SKILL.md` | Existing skill reused. |
| `example-phase` | `internal-label` | expert-team router | Source-specific phase retained inside router. |

## Creating Child Skills

When creating a missing child skill:

- Make it a real capability package, not a copied persona.
- Include trigger-aware frontmatter.
- Include `agents/openai.yaml` with `default_prompt` containing `$<child-name>`.
- Include `source.json` with `status: "ready"` and sanitized `source_ref`.
- Keep detailed converted material in `references/guide.md` when the original child prompt is long.
- Validate the child package independently.

If a source child includes deterministic scripts that are useful and safe, copy or rewrite them with explicit arguments and no hardcoded machine paths. Otherwise summarize the workflow in `SKILL.md` and references.

## Creating The Expert Team Router

The router `SKILL.md` should follow the same lightweight shape as `harmony-expert-team`:

1. Frontmatter: `name`, trigger-rich `description`, and optional short description metadata.
2. Overview: state that this is the expert-team entry point.
3. `Expert Roles`: list child entries and mark whether each is a top-level skill or an internal label.
4. `Routing`: tell Codex when to use each top-level skill or internal label.
5. Project or domain workflow: describe phased execution for full-package requests.
6. Delivery checklist and output style.

The router may reference existing skills, newly created child skills, and internal router labels together. It must not depend on the original plugin runtime, member avatars, or nested source folder layout.

## Example Pattern

For a source package shaped like `design-engine`:

- Convert the team lead into the router package.
- Resolve each visible member or nested skill, such as discovery, design system selection, prototype building, quality critique, and export delivery.
- Reuse existing design skills only when their top-level package already covers the same capability.
- Keep source-specific members as internal labels when they are only useful inside the design-engine router.
- Create missing top-level child packages only when they are independently useful and safe to invoke outside the team.
- Add one row in `indexes/expert-team-file-list.md` where the child cell names match the router entries, whether they are top-level skills or internal labels.

## Handoff

Report:

- Expert-team package path.
- Created child skill package paths.
- Reused child skill package paths.
- Internal child labels.
- Selected team mode.
- Expert-team catalog row and category.
- Registry/index updates.
- Validation commands and results.
- Assumptions, conflicts, and any child capability intentionally left out.
