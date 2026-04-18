# agents

`agents` manages Machineconfig's AI-agent scaffolding, prompt execution, MCP catalog installs, and parallel multi-agent job files.

---

## Usage

```bash
agents [OPTIONS] COMMAND [ARGS]...
```

## Current top-level commands

| Command | Current behavior |
| --- | --- |
| `parallel` | Create agent layouts, create a shared context file, collect outputs, or emit a template command |
| `make-config` | Scaffold AI config files, instructions, and optional shared `.ai` assets in a repository |
| `add-mcp` | Resolve MCP entries from Machineconfig catalogs and install them into agent configs |
| `make-todo` | Generate filtered checklist files for repo contents |
| `make-symlinks` | Create `~/code_copies/<repo>_copy_<n>` symlinks to the current repo |
| `run-prompt` | Run one prompt through a selected agent, with inline, file, or YAML-backed context |
| `ask` | Ask a selected agent directly |
| `add-skill` | Add a supported skill into an agent directory |

---

## `parallel`

Current subcommands:

| Command | Behavior |
| --- | --- |
| `create` | Build an agent layout file with prompt/context splitting and output paths |
| `create-context` | Ask one agent to persist a shared `context.md` for a job |
| `collect` | Concatenate collected agent material files into one output file |
| `make-template` | Print a starter template for fire-agent usage |

`agents parallel create` currently accepts the main workflow controls: `--agent`, `--model`, `--reasoning-effort`, `--provider`, `--host`, `--context` or `--context-path`, `--prompt` or `--prompt-path`, `--prompt-name`, `--job-name`, `--agent-load`, `--separator`, `--agents-dir`, `--output-path`, and `--interactive`.

Examples:

```bash
agents parallel --help
agents parallel create --help
agents parallel create --agent codex --reasoning-effort high --context-path ./.ai/agents/docs/context.md --prompt-path ./.ai/prompts/update.md --job-name updateDocs
agents parallel create-context --job-name updateDocs "Collect the repo context for this doc task"
agents parallel collect ./.ai/agents/updateDocs ./tmp/materials.txt
```

---

## Prompt-running commands

`run-prompt` is the structured workflow entrypoint. It supports:

- `--agent`
- `--reasoning-effort` for codex agents
- `--context` or `--context-path`
- `--context-yaml-path` plus `--context-name`
- `--where` to choose catalog locations for context YAML lookup
- `--show-format` and `--edit` for prompts-YAML guidance and editing

Examples:

```bash
agents run-prompt --agent codex --reasoning-effort high --context-path ./context.md "inspect this repo"
agents run-prompt --agent copilot --context-name docs.cli --where all "update the assigned docs"
agents run-prompt --show-format
```

`ask` is the lighter-weight direct path. Current behavior to keep in mind:

- default agent is `codex`
- `--reasoning` accepts `n`, `l`, `m`, `h`, `x`
- that shortcut is only supported for `codex` and `copilot`
- `--file-prompt` appends the file contents into the final prompt with explicit `BEGIN FILE` and `END FILE` markers

Examples:

```bash
agents ask --agent codex --reasoning h "inspect the repo"
agents ask --agent copilot --reasoning m "summarize the current module"
agents ask "summarize this file" --file-prompt ./README.md
```

---

## Repository and MCP helpers

`make-config` currently requires `--root` and can optionally add private config files, instructions, shared `.ai` assets, VS Code tasks, and `.gitignore` entries:

```bash
agents make-config --root .
agents make-config --root . --agent codex,copilot --include-scripts --add-gitignore
```

`add-mcp` resolves names from Machineconfig MCP catalogs and installs them for one or more agents. Notes:

- `--scope local` requires running inside a git repository
- `--where` selects catalog locations
- `--edit` opens the catalog files and exits immediately if no MCP names were provided

```bash
agents add-mcp --help
agents add-mcp postgres,filesystem --agent codex,copilot --scope local
agents add-mcp --edit --where library
```

`make-todo` scans a repo or workspace and writes filtered checklist files under `.ai/todo/files` by default. `make-symlinks` creates repo symlinks under `~/code_copies/`.

---

## `add-skill`

`add-skill` exists, but the current implementation only recognizes a small built-in mapping. At the moment, the shipped mapping includes `agent-browser`; unknown skill names exit with an error instead of searching for alternatives.

---

## Getting help

```bash
agents --help
agents parallel --help
agents make-config --help
agents add-mcp --help
agents make-todo --help
agents run-prompt --help
agents ask --help
agents add-skill --help
```
