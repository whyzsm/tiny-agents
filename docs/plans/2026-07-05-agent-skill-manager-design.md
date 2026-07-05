# Agent and Skill Manager Design

Date: 2026-07-05

## Goal

Build a local Python CLI for managing the user's personal agents and skills. The
tool scans known AI configuration directories, produces a dry-run report, and
later imports confirmed safe items into this repository.

## Confirmed Decisions

- Scan scope: explicit AI configuration directories only.
- Initial roots:
  - `/Users/seminzhu/.codex`
  - `/Users/seminzhu/.agents`
- Target directories:
  - `agents/`
  - `skills/`
- Import behavior: copy core files only, skip cache, logs, build outputs, and
  sensitive paths.
- Secret handling: scan before import; block items with suspected secrets.
- Name conflicts: do not overwrite or merge; report conflicts for manual review.
- Flow: `scan` dry-run first, then `import` from a confirmed JSON report.
- Reports:
  - `reports/scan-YYYY-MM-DD.md`
  - `reports/scan-YYYY-MM-DD.json`
- Directory layout after import:
  - `agents/<name>/...`
  - `skills/<name>/...`
  - each item includes `source.json`
- Scope excludes Codex system skills, plugin cache, and official bundled runtime
  content. It includes personal and manually installed third-party agents and
  skills.
- Implementation: Python CLI, standard library first.
- First version commands: `scan` and `import`.
- Repository: initialize git locally and later push to
  `https://github.com/zsmtiny-create/tiny-agents`.

## Domain Rule

A skill has no soul, personality, or independent role. A skill is a capability,
workflow, or tool instruction. It describes when to use it, how to perform the
work, and what to produce.

An agent is a role-bearing subject. It may have identity, responsibilities,
personality, communication style, tool boundaries, behavior constraints, mission,
or system-prompt-like instructions.

Any `SKILL.md` that contains clear agent identity, personality, role, or soul
settings must not be automatically imported as a skill. It is reported as a
candidate for manual review.

## Architecture

The CLI is split into four layers.

### CLI Layer

Commands:

- `scan`: scans configured roots and generates Markdown and JSON reports.
- `import`: reads a confirmed JSON report and copies safe ready items into
  `agents/` and `skills/`.

### Scan Layer

Default roots:

- `/Users/seminzhu/.codex`
- `/Users/seminzhu/.agents`

Default exclusions:

- `.system`
- plugin caches and runtime caches
- `node_modules`
- `.git`
- auth/session/cache/log/tmp/env/key/credential-like paths

### Classification Layer

The tool uses a two-channel model.

Strict matches become ready items:

- Standard `SKILL.md` without obvious persona, role, soul, or agent identity.
- Explicit agent prompts or manifests, such as `agents/*.md` and `AGENTS.md`.

Heuristic matches become candidates:

- Persona-bearing `SKILL.md`.
- Non-standard but suspicious agent or skill files.
- Ambiguous files that need human review.

Skill-owned helper files such as `skills/*/agents/openai.yaml` are treated as
part of the parent skill, not as standalone agents.

Conflicts are kept out of ready imports.

### Safety Layer

Core files are scanned before import. If a file appears to contain a secret,
token, credential, or private key, the item is blocked. Reports include path and
rule names only, never the suspected secret value.

## Components

- `tiny_agents/cli.py`: command parsing and command dispatch.
- `tiny_agents/config.py`: default roots, exclusions, and core-file rules.
- `tiny_agents/discovery.py`: file tree traversal and candidate path discovery.
- `tiny_agents/classifier.py`: item classification and conflict detection.
- `tiny_agents/secrets.py`: suspected secret detection.
- `tiny_agents/report.py`: Markdown and JSON report generation.
- `tiny_agents/importer.py`: import from confirmed JSON reports.
- `tiny_agents/models.py`: shared data structures.
- `tests/`: unit tests.

## Data Flow

1. `scan` reads default roots, with optional root overrides in later versions.
2. `discovery` walks roots, applies exclusions, and finds known agent and skill
   entry files.
3. `classifier` labels entries as `skill`, `agent`, `candidate`, `conflict`, or
   `blocked`, recording classification reasons.
4. `secrets` scans core files for suspected secrets.
5. `report` writes Markdown and JSON reports under `reports/`.
6. `import` reads a confirmed JSON report and imports only ready agent and skill
   items.
7. `importer` writes `source.json` for each imported item with source path,
   scan time, classification reason, and copied files.

## Error Handling

- Missing scan root: warn and continue.
- Unreadable file: skip the file and warn.
- Malformed frontmatter, JSON, or YAML: fall back to text classification and
  warn.
- Suspected secret: mark the item as blocked.
- Duplicate names: mark all duplicate items as conflicts.
- Existing target directory: fail that import item; do not overwrite.
- Report schema mismatch: reject import.
- File copy failure: stop importing that item and record the error.
- GitHub push failure: preserve local commits and report the remote failure.

## Testing Strategy

Use Python standard-library `unittest`.

Classifier tests:

- Standard `SKILL.md` is classified as a skill.
- Persona-bearing `SKILL.md` becomes a candidate.
- `agents/*.md` and `AGENTS.md` are classified as agents.
- `skills/*/agents/openai.yaml` is not classified as a standalone agent.
- Duplicate names become conflicts.

Secret tests:

- Obvious token, key, and credential patterns are blocked.
- Ordinary documentation does not trigger secret detection.

Report tests:

- JSON schema version is correct.
- Markdown includes ready, candidate, blocked, conflict, and warning sections.

Importer tests:

- Only ready `agent` and `skill` items are imported.
- Candidate, blocked, and conflict items are not imported.
- `source.json` is written.
- Existing target directories are not overwritten.

Verification command:

```bash
python3 -m unittest
```
