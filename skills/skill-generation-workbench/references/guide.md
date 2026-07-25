# Skill Generation Workbench Guide

## Entry

Use this entry when the user wants to design, generate, convert, upgrade, or
review a Codex Skill package. It coordinates the existing `skill-creator`
capability with repository-local scaffolding and validation rules.

## Capability Modules

| Module | Source | Responsibility |
|---|---|---|
| `skill-creator` | Codex Skill Creator | Skill anatomy, naming, progressive disclosure, and validation baseline. |
| `intake` | `SKILL.md` | Collect triggers, inputs, outputs, destination, and side-effect boundaries. |
| `blueprint` | `references/skill-contract.md` | Turn the request into a concrete package contract before writing files. |
| `capability-discovery` | `find-skills` then `https://skillhub.cn/` | Search for reusable Skills before writing; record candidates and rejected overlaps without installing. |
| `scaffold` | `scripts/scaffold_skill.py` | Create a non-overwriting package skeleton with safe metadata. |
| `validation` | `references/generation-checklist.md` | Check structure, metadata, tests, paths, secrets, and handoff evidence. |

## Routing

- For a new Skill, complete capability discovery (`find-skills` first, then SkillHub), then `intake`, `blueprint`, `scaffold`, implementation, and validation in order.
- For an existing Skill, inspect and patch the current package; do not reinitialize it.
- For an upgrade or conversion that writes files, run capability discovery before inspecting the final implementation plan; reuse or extend a verified match instead of creating a duplicate.
- For an external prompt or expert card, preserve only visible capability evidence and mark missing details as assumptions.
- For a review-only request, stop after inspection and return findings without changing files.
- For installation, commit, push, deletion, or deployment, require explicit user authorization.

## Capability Discovery Before Writing

Run these searches in order for create, upgrade, and convert work:

```bash
npx --yes skills find "<domain> <task> <stack>"
skillhub --skip-self-upgrade search "<domain> <task> <stack>" --json --search-limit 20
```

The second command uses `https://skillhub.cn/` through the SkillHub CLI. Use
`https://api.skillhub.cn/api/v1/search?q=<query>&limit=<n>` only as its public API fallback.
Searches do not install packages. Read visible candidate `SKILL.md` files or package metadata when
reachable, compare candidates with the local registry, and record the evidence and final
reuse/upgrade/convert/create decision in the blueprint.

## Repository Package Shape

The repository entry should contain only the files needed to execute and verify
the capability:

```text
skill-name/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── guide.md
│   ├── manifest.json
│   └── task-specific references
├── scripts/                # only when deterministic helpers are useful
└── source.json
```

Keep all paths in `source.json` relative or public. Do not copy local install
configuration, runtime caches, generated reports, or platform-specific helper
files into the package.
