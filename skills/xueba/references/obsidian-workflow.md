# Obsidian 写入工作流

Use this reference whenever the user wants learning output saved into Obsidian.

## Required Behavior

Saving to Obsidian means writing a Markdown file into a real local Obsidian vault directory. A generated-output folder, Codex workspace, `/tmp`, or an `obsidian://` URL is not a save destination.

Workflow:

```text
Detect Obsidian
-> If missing, install from official GitHub releases and re-detect
-> Resolve a real vault
-> Resolve the learning root (`docs/xueba/88-学习/` when `docs/xueba/` exists, otherwise `88-学习/`)
-> Classify the learning path
-> Check double-link safety when the draft contains `[[...]]`
-> Write the final Markdown file
-> Clean temporary drafts when possible
-> Report only the final Obsidian path
```

## Scripts

Prefer the bundled scripts when local script execution is available:

```bash
python scripts/resolve_obsidian_vault.py --json
python scripts/install_obsidian.py --json
python scripts/classify_learning_path.py --title "Agent Skills 开放技能标准与工程实践" --domain-tag domain/ai/skills
python scripts/check_obsidian_links.py --vault "/path/to/vault" --content-file note.md
python scripts/write_obsidian_note.py --vault "/path/to/vault" --relative-dir "88-学习/AI/skills" --filename "Agent Skills：开放技能标准与工程实践.md" --content-file note.md
```

Use `--vault` on `resolve_obsidian_vault.py` when the user gives an explicit vault path.

## Obsidian Detection

Check whether Obsidian appears to be installed:

- macOS: common `.app` locations and registered app paths.
- Linux: `obsidian` executable or desktop entries.
- Windows: common install paths or `PATH`.

If Obsidian is not detected:

- still generate Markdown when useful
- install Obsidian from the official GitHub releases repository: https://github.com/obsidianmd/obsidian-releases
- request the required host/network/system approval instead of stopping at a download prompt
- rerun `scripts/resolve_obsidian_vault.py --json` after installation
- ask for a vault path only if Obsidian is installed but no vault can be resolved
- do not fabricate an Obsidian destination

## Vault Selection

Resolve the target vault in this order:

1. User-provided explicit vault path.
2. Obsidian local config, preferring an open or recently used vault.
3. Search likely document locations for `.obsidian` directories within permissions.
4. If there are multiple equally valid candidates, ask the user to choose.

Do not treat the current workspace as the vault unless it contains `.obsidian` or the user explicitly says it is the vault.

## Learning Root And Save Path

Final notes go under the resolved learning root:

1. If the vault contains `docs/xueba/`, use `docs/xueba/88-学习/`.
2. Otherwise use `88-学习/`.

Do not create `88-学习/` at the vault root when `docs/xueba/` exists. This is the common doc-site layout and the user expects all notes below `docs/`.

The logical classification path remains:

```text
[learning-root]/[大学科]/[章节或知识要点]/[主题].md
```

Use `references/tag-taxonomy.md` and `scripts/classify_learning_path.py` for classification.

Pass logical paths such as `88-学习/AI/skills` to `scripts/write_obsidian_note.py`; the script maps them to the resolved learning root.

## Double-Link Safety

In default single-note Study Mode, avoid `[[...]]` unless the target note already exists or is created in the same task.

Before writing a draft that contains double links, run:

```bash
python scripts/check_obsidian_links.py --vault "/path/to/vault" --content-file note.md
```

If unresolved links are reported, convert them to plain text and mark the concept as `可拆卡` instead of leaving an empty-link target.

## Temporary Files

- Do not present `/private/tmp`, `/tmp`, or other scratch paths as final user-visible outputs.
- If a temporary draft is necessary, write the final note into the vault before reporting completion.
- After a successful vault write, clean temporary drafts when possible.
- If the final vault write fails, call the temporary file a draft and explain the missing next action.

## Final Reply

After a successful write, report:

- final Obsidian file path
- source access method
- any source limitations
- next review action

Do not include temporary draft paths in the final user-facing reply.
