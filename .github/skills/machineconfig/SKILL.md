---
name: machineconfig
description: Teach and execute Machineconfig usage through direct Typer entrypoints. Use this when asked to use, explain, troubleshoot, or extend the machineconfig CLI/library via devops, cloud, sessions, agents, utils, fire, croshell, or msearch, especially when mapping command paths to implementation files.
---

# Machineconfig

Use this skill to work from direct CLI commands into nested Typer apps and helper modules.

## Quick Workflow

1. Detect execution mode.
- In this repository, prefer `UV_CACHE_DIR=/tmp/uv-cache uv run <command> ...`.
- For globally installed usage, use direct entrypoints like `devops`, `cloud`, `sessions`, `agents`, `utils`, `fire`, `croshell`, `msearch`.

2. Resolve command path before acting.
- Start with `<command> --help`.
- Drill down with `<command> <subcommand> --help` until you hit a leaf command.
- Use canonical command names only (no short aliases).

3. Follow source, not old docs.
- Treat Typer registrations in source as the source of truth.
- If docs conflict with source, explain the mismatch and proceed with the source-backed command.

4. Map command to implementation.
- Use `references/source-map.md` to jump directly to the file that registers/implements the command.
- Remember `mcfg_entry.py` is a lazy dispatcher; most behavior lives in helper modules.

5. Run safely.
- Commands under install/update/network/config may mutate system state.
- Call out side effects and require explicit confirmation for risky actions.

## Command Surface

Load `references/cli-map.md` for the current command tree and nested subcommands.

Highlights:
- Primary commands: `devops`, `cloud`, `sessions`, `agents`, `utils`, `fire`, `croshell`, `msearch`.
- This skill intentionally excludes command aliases.
- `devops self security` and `devops self buid-docker` appear only when `~/code/machineconfig` exists.

## Practical Rules

- Prefer these for repo-local reproducibility:
```bash
UV_CACHE_DIR=/tmp/uv-cache uv run devops --help
UV_CACHE_DIR=/tmp/uv-cache uv run devops repos --help
```
- Use long flags in guidance.
- When adding or changing commands, update both Typer registration and helper implementation, then re-check `--help` output.
