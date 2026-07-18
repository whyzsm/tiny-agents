# Target Structure

This repository treats `skills/` as capability packages. An imported expert team must become a normal top-level skill package. Its child entries can be real top-level skills, a hybrid of real skills and internal labels, or router-internal labels only.

## Expert Team Package

```text
skills/<team-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── guide.md
└── source.json
```

Required details:

- `SKILL.md` frontmatter `name` matches `<team-name>`.
- `SKILL.md` description includes the domain, main triggers, team mode, and child entries coordinated by the team.
- `agents/openai.yaml` has `display_name`, `short_description`, and `default_prompt` containing `$<team-name>`.
- `references/guide.md` contains converted source workflow details, child capability mapping, templates, and provenance notes when needed.
- `source.json` uses `status: "ready"` and sanitized source values such as `user-provided/<package-name>`.

## Child Entry Modes

The expert-team catalog supports three child-entry modes:

| Mode | Catalog child entries | Router requirement |
|---|---|---|
| `all-top-level-skills` | All child names exist as top-level packages under `skills/`. | The router can tell Codex to invoke those child skills directly. |
| `hybrid` | Some child names are top-level packages; others are team-local labels. | The router must distinguish top-level skills from internal labels. |
| `internal-router-labels` | Child names are local role, phase, or capability labels only. | The router must keep execution inside the expert-team skill and must not claim `$child-name` invocation. |

Choose the mode from source and repository evidence. Do not promote every source agent file into a top-level skill by default.

## Optional Child Skill Package

```text
skills/<child-skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── guide.md        # optional, only for detailed converted material
└── source.json
```

Required details:

- The child package is callable on its own.
- The child `SKILL.md` describes a capability and workflow, not an identity.
- The child name may appear in the expert-team `Expert Roles` list and in `indexes/expert-team-file-list.md` when the team mode uses a real top-level child skill.
- If an existing top-level skill is reused, do not duplicate it. Reference its existing name in the team router and catalog row.
- If a source child is not useful outside its team, leave it as an internal label instead of creating a weak standalone package.

## Index Updates

Update these files:

```text
indexes/skill-registry.md
indexes/skill-registry.json
indexes/expert-team-file-list.md
```

Use this order:

1. Add or update skill packages.
2. Run `python3 scripts/generate_skill_registry.py`.
3. Edit `indexes/expert-team-file-list.md` manually:

```markdown
| <分类> | [`<team-id>`](../skills/<team-name>/SKILL.md) | <显示名称> | `<top-level-skill-or-label-1>`<br>`<top-level-skill-or-label-2>` |
```

4. Increase the expert-team count at the top by exactly the number of new rows added.

Do not update `indexes/agent-skill-index.md` or `indexes/agent-skill-index.json` unless the user asks for a fresh local scan inventory. Do not update `indexes/expert-team-skill-index.md` unless the user asks for that specialized expert-team Skill catalog.

## Acceptance Criteria

A conversion is complete only when:

- The expert team validates as a Codex Skill.
- Every listed child entry is classified as a top-level skill or internal router label.
- Hybrid and internal-label teams clearly explain which entries are not directly callable as standalone `$skill` names.
- `indexes/skill-registry.md` and `indexes/skill-registry.json` include all new packages.
- `indexes/expert-team-file-list.md` has the expert-team row with child names that match the router.
- Generated metadata contains no local absolute paths, secrets, tokens, runtime caches, or hidden prompt claims.
- The final response lists created skills, reused skills, internal labels, selected team mode, validation evidence, and unresolved assumptions.
