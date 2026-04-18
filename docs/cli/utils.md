# utils

`utils` is the grouped entrypoint for Machineconfig helper workflows.

## Usage

```bash
utils [OPTIONS] COMMAND [ARGS]...
```

Top-level sub-apps:

| Sub-app | Purpose |
|---------|---------|
| `machine` | Process, environment, hardware, and local device helpers |
| `pyproject` | Project bootstrap, dependency maintenance, and typing workflows |
| `file` | File editing, downloading, PDF tools, and database viewing |

Hidden one-letter aliases exist, but this page uses canonical names.

## machine

```bash
utils machine [OPTIONS] COMMAND [ARGS]...
```

| Command | Summary |
|---------|---------|
| `kill-process` | Interactive process picker with configurable filter field |
| `environment` | Inspect `ENV` or `PATH` using the default fuzzy picker or a Textual TUI |
| `get-machine-specs` | Print machine specifications |
| `list-devices` | List available devices for mounting |
| `mount` | Mount a device by query or through an interactive picker |

Key behavior:

- `kill-process` defaults to interactive mode and supports `--filter-by command|ports|name|pid|username|status|memory|cpu`.
- `environment` defaults to `ENV`; pass `PATH` as the positional argument to browse `PATH` entries instead.
- `environment --tui` uses the full-screen Textual UI instead of the default fuzzy picker.
- `get-machine-specs --hardware` includes compute capability details.
- `mount` requires both `--device` and `--mount-point` unless `--interactive` is set.
- `mount --backend` accepts `mount`, `dislocker`, or `udisksctl`.

Examples:

```bash
utils machine environment PATH
utils machine environment ENV --tui
utils machine get-machine-specs --hardware
utils machine mount --interactive
utils machine mount --device sdb1 --mount-point /mnt/data --read-only
```

## pyproject

```bash
utils pyproject [OPTIONS] COMMAND [ARGS]...
```

| Command | Summary |
|---------|---------|
| `init-project` | Initialize a project with a uv virtual environment and dev packages |
| `upgrade-packages` | Regenerate package-add commands for a project, optionally clearing groups first |
| `type-hint` | Type-hint a file or project directory |
| `type-check` | Run the lint-and-type-check suite for a repository |
| `reference-test` | Validate `_PATH_REFERENCE` targets in a repository |
| `type-fix` | Create and optionally launch an agent layout from `./.ai/linters/issues_<checker>.md` |

Key behavior:

- `init-project` defaults to Python `3.13` and package groups `p,t,l,i,d`.
- `upgrade-packages [ROOT]` can repeat `--clean-group` before regenerating `pyproject_init.sh`.
- `type-hint [PATH]` defaults to `--dependency self-contained`. When given a project directory, it currently scans for `dtypes.py` files and reports the corresponding `*_names.py` outputs.
- `type-check [REPO]` resolves the repository root from the nearest `pyproject.toml` and passes exclusions through the lint/type-check script.
- If `--exclude` is omitted, `type-check` currently defaults to excluding `tests`, `.github`, `.codex`, `.ai`, `.links`, and `.venv`.
- `reference-test REPO` supports `--search-root` and `--verbose`.
- `type-fix` is a callback command rather than a nested app. It accepts `--agent`, `--agent-load`, `--which-checker`, and `--max-agents`, generates a layout under `./.ai/agents/fix_<checker>_issues/`, then prompts to run it.

Examples:

```bash
utils pyproject init-project --name sample --python 3.14
utils pyproject upgrade-packages . --clean-group dev
utils pyproject type-hint src/my_module.py
utils pyproject type-check . --exclude tests --exclude .venv
utils pyproject reference-test . --verbose
utils pyproject type-fix --which-checker pyright --agent codex
```

## file

```bash
utils file [OPTIONS] COMMAND [ARGS]...
```

| Command | Summary |
|---------|---------|
| `edit` | Open a file or project path in the default editor |
| `download` | Download a file and optionally decompress it |
| `pdf-merge` | Merge one or more PDF files |
| `pdf-compress` | Compress a PDF file |
| `read-db` | Launch a terminal database client |

Key behavior:

- `download [URL]` supports `--decompress`, `--output`, and `--output-dir`.
- `pdf-merge PDFS...` accepts one or more input files and can `--compress` the merged output.
- `pdf-compress PDF_INPUT` supports `--quality`, `--image-dpi`, `--compress-streams`, and `--object-streams`.
- `read-db [PATH]` defaults to the `harlequin` backend and supports `--backend`, `--read-only/--read-write`, `--theme`, and `--limit`.

Examples:

```bash
utils file edit .
utils file download https://example.com/archive.tar.gz --decompress --output-dir ./downloads
utils file pdf-merge a.pdf b.pdf c.pdf --output merged.pdf
utils file pdf-compress report.pdf --output report-small.pdf --quality 75 --image-dpi 144
utils file read-db ./local.db --backend harlequin --read-only
```

## Typical Flow

Use live help to drill into the subgroup you need:

```bash
utils --help
utils machine --help
utils machine mount --help
utils pyproject --help
utils pyproject type-check --help
utils pyproject reference-test --help
utils file --help
utils file read-db --help
```
