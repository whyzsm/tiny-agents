# Generation Checklist

Use this checklist before reporting a generated Skill as complete.

## Intake

- [ ] Capability and target user are concrete.
- [ ] At least two natural-language trigger examples are recorded.
- [ ] Inputs, outputs, success criteria, and failure behavior are clear.
- [ ] Destination and install/publish boundary are explicit.
- [ ] Destructive or external actions have confirmation points.

## Package

- [ ] Skill name is lowercase hyphen-case and at most 64 characters.
- [ ] Frontmatter contains an accurate description under 1024 characters.
- [ ] `SKILL.md` has no TODO placeholders, fake tool claims, or persona instructions.
- [ ] `agents/openai.yaml` uses quoted strings and references `$skill-name`.
- [ ] References are one level deep and linked from `SKILL.md`.
- [ ] Scripts have explicit arguments and do not contain local absolute paths.
- [ ] Unused resource directories and auxiliary documentation are removed.

## Verification

- [ ] `quick_validate.py <skill-directory>` passes.
- [ ] `agents/openai.yaml` parses as YAML and its key values match `SKILL.md`.
- [ ] Every new script runs successfully on a temporary fixture.
- [ ] Relevant repository tests pass.
- [ ] `git diff --check` passes.
- [ ] No machine-specific home paths, temporary runtime paths, secrets, tokens, or generated local reports are tracked.
- [ ] `git status --short -uall` contains only intended changes.

## Handoff

- [ ] Report absolute file paths and the generated Skill name.
- [ ] Include trigger examples and validation evidence.
- [ ] List assumptions, unresolved questions, and remaining risks.
- [ ] Do not claim installation, commit, push, or deployment without direct evidence.
