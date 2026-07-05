# tiny-agents

Local CLI for scanning and organizing personal AI agents and skills.

## Commands

Generate a dry-run report:

```bash
python3 -m tiny_agents scan
```

Import confirmed ready items from a report:

```bash
python3 -m tiny_agents import reports/scan-2026-07-05.json
```

The first version scans `~/.codex` and `~/.agents`, excludes system, cache, and
sensitive paths, blocks suspected secrets, and imports only ready agents and
skills.

## Agent And Skill Boundary

A skill is a capability, workflow, or tool instruction. It should not carry an
independent personality, identity, or soul.

An agent is a role-bearing prompt or manifest. A `SKILL.md` with clear identity,
persona, role, personality, or soul settings is reported as a candidate instead
of being imported as a skill automatically.
