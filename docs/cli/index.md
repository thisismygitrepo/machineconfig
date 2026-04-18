# CLI Reference

Machineconfig currently exposes two entry styles:

- standalone commands such as `devops`, `fire`, and `seek`
- umbrella wrappers: `mcfg` and `machineconfig`

For day-to-day use, prefer the standalone command when you already know which tool you want. Use `mcfg` or `machineconfig` when you want one top-level CLI that routes into the same command tree.

---

## Standalone entrypoints

| Command | Purpose |
| --- | --- |
| [`devops`](devops.md) | Package installation, repo automation, config sync, data sync, self-management, networking, and script execution |
| [`terminal`](terminal.md) | Terminal session and layout management |
| [`agents`](agents.md) | AI agent scaffolding, MCP catalog installs, prompt runs, and parallel agent workflows |
| [`utils`](utils.md) | General-purpose utility commands |
| [`croshell`](croshell.md) | Cross-shell launcher built around `uv run` backends |
| [`seek`](seek.md) | Interactive search across files, text matches, and symbols |
| [`fire`](fire.md) | File, function, notebook, and app runner |
| [`cloud`](cloud.md) | Cloud sync, copy, mount, and SSH transfer helpers |

---

## Umbrella entrypoints

`mcfg` and `machineconfig` are lazy-loading wrappers around the same top-level command families:

```bash
mcfg --help
machineconfig --help
mcfg devops --help
machineconfig agents --help
```

The wrappers currently expose:

- `devops`
- `cloud`
- `terminal`
- `agents`
- `utils`
- `seek`
- `fire`
- `croshell`

For the full command-specific flag surface, check the standalone command as well, for example `fire --help` or `seek --help`.

---

## Getting help

```bash
devops --help
agents --help
cloud --help
croshell --help
fire --help
seek --help
mcfg --help
machineconfig --help
```
