# Obsidian 写入工作流

Use this reference whenever the user wants learning output saved into Obsidian.

## Required Behavior

Saving to Obsidian means writing a Markdown file into a real local Obsidian vault directory. A generated-output folder, Codex workspace, `/tmp`, or an `obsidian://` URL is not a save destination.

Workflow:

```text
Detect Obsidian
-> If missing, request approval, install from official GitHub releases when approved, and re-detect
-> Resolve a real vault
-> Confirm or create 88-学习/
-> Classify the learning path
-> Write the final Markdown file
-> Clean temporary drafts when possible
-> Report only the final Obsidian path
```

## Scripts

Prefer the bundled scripts when local script execution is available:

```bash
python3 scripts/resolve_obsidian_vault.py --json
python3 scripts/install_obsidian.py --json
python3 scripts/classify_learning_path.py --title "Agent Skills 开放技能标准与工程实践" --domain-tag domain/ai/skills
python3 scripts/write_obsidian_note.py --vault "/path/to/vault" --relative-dir "88-学习/AI/skills" --filename "Agent Skills：开放技能标准与工程实践.md" --content-file note.md
```

Use `--vault` on `resolve_obsidian_vault.py` when the user gives an explicit vault path.

## Obsidian Detection

Check whether Obsidian appears to be installed:

- macOS: common `.app` locations and registered app paths.
- Linux: `obsidian` executable or desktop entries.
- Windows: common install paths or `PATH`.

If Obsidian is not detected:

- still generate Markdown when useful
- request explicit user or host approval before installing Obsidian
- install Obsidian from the official GitHub releases repository only when approved: https://github.com/obsidianmd/obsidian-releases
- use `scripts/install_obsidian.py --json --dry-run` first when the user wants to see what will be installed
- rerun `scripts/resolve_obsidian_vault.py --json` after installation
- ask for a vault path only if Obsidian is installed but no vault can be resolved
- do not fabricate an Obsidian destination
- do not claim the note was saved to Obsidian until a real vault has been resolved and written

## Vault Selection

Resolve the target vault in this order:

1. User-provided explicit vault path.
2. Obsidian local config, preferring an open or recently used vault.
3. If config does not identify a single vault, rerun the resolver with `--search` to search likely document locations for `.obsidian` directories within permissions.
4. If there are multiple equally valid candidates, ask the user to choose.

Do not treat the current workspace as the vault unless it contains `.obsidian` or the user explicitly says it is the vault.

## Save Path

Final notes go under:

```text
[vault]/88-学习/[大学科]/[章节或知识要点]/[主题].md
```

Use `references/tag-taxonomy.md` and `scripts/classify_learning_path.py` for classification.

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
