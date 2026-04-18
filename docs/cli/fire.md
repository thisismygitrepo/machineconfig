# fire

`fire` resolves a file, directory, or partial script name, then builds an execution command around Python Fire, plain Python, IPython, Streamlit, Jupyter, Marimo, shell sourcing, or direct executable launch.

---

## Usage

```bash
fire [OPTIONS] [PATH] [FUNCTION]
```

## Arguments

| Argument | Description |
| --- | --- |
| `PATH` | Path to the file to run, or a directory / partial name that can be resolved interactively |
| `FUNCTION` | Optional Python function name |

---

## Current execution flags

| Area | Flags |
| --- | --- |
| General execution | `--script`, `--module`, `--interactive`, `--debug`, `--optimized`, `--frozen` |
| Function selection | `--choose-function` |
| Notebook and app launch | `--jupyter`, `--marimo`, `--streamlit`, `--environment` |
| Shell and background helpers | `--zellij-tab`, `--cmd`, `--loop`, `--watch`, `--git-pull` |
| Path and repo handling | `--root-repo`, `--holdDirectory`, `--PathExport` |
| Remote or cloud launch | `--remote`, `--submit-to-cloud` |
| Exposed but currently inert in routing | `--ve` |

---

## Passing function arguments

The current Typer wrapper keeps extra Fire arguments in the pass-through segment after `--`.

Use this form:

```bash
fire jobs.py run -- --limit=2 --dry-run
```

Not this:

```bash
fire jobs.py run --limit=2
```

That extra `--` matters because the wrapper parses its own options first, then forwards the remaining raw arguments into the generated Python Fire command.

---

## Current path resolution

`fire` does not require an exact filename up front.

- if `PATH` is a file, it uses it directly
- if `PATH` is a directory, it recursively scans for candidate scripts and asks you to choose
- if `PATH` does not exist, it searches for a matching filename or partial path
- `--root-repo` changes that search root to the git repository root of the current working directory

Supported target types in the current route:

| Target | Behavior |
| --- | --- |
| `.py` | Build a Python, IPython, Streamlit, Jupyter, or Marimo command |
| `.sh` / `.ps1` | Source the script |
| no suffix | Execute directly |

---

## Function selection

`--choose-function` behaves differently by file type:

- for Python files, it parses top-level functions and offers a `RUN AS MAIN` option
- for shell files, it offers non-comment, non-empty, non-`echo` lines and writes the selected lines into a temporary script

For Python files, when you choose a function and did not already pass kwargs, the helper prompts for argument values based on the parsed signature.

Examples:

```bash
fire tools.py -c
fire tools.py cleanup -- --days=30
```

---

## Notebook and app modes

`--marimo`:

- checks whether the selected file is already a valid marimo notebook
- if not, converts it into a temporary notebook under `~/tmp_results/tmp_scripts/marimo/...`
- launches `marimo edit --host 0.0.0.0`

`--streamlit`:

- reads `.streamlit/config.toml` beside the file, or from the parent app directory when the file lives under `pages/`
- uses the configured port when present, otherwise `8501`
- prints QR codes and LAN / hostname / localhost URLs
- launches `streamlit run --server.address 0.0.0.0 --server.headless true`

`--jupyter` launches JupyterLab against the selected file or generated notebook context.

Examples:

```bash
fire dashboard.py -S -E localhost
fire notebook.py -M
fire analysis.py -j
```

---

## Interactive and development helpers

- `--interactive` launches IPython and currently discovers the IPython profile from the nearest `.ve.yaml`; it falls back to `default`.
- `--watch` prefixes the final command with `watchexec --restart --exts py,sh,ps1`.
- `--git-pull` runs `git -C <script-dir> pull` first.
- `--PathExport` prepends a shell snippet that appends the repo root to `PYTHONPATH`.
- `--zellij-tab` writes the command into a temp script and opens it in a new Zellij tab.
- `--loop` reruns after completion or interruption.

Examples:

```bash
fire src/app.py serve -- --host=0.0.0.0 --port=8000
fire src/app.py -i
fire src/app.py -w -g
fire nested/tool.py -r -P
```

---

## Notes

- `--ve` is still exposed in the CLI help, but the current route implementation does not use it when building the command. Environment discovery currently comes from repo-root handling and `.ve.yaml` / `.venv` discovery instead.
- `mcfg fire` and `machineconfig fire` route into the same command family, but `fire --help` is the best source for the direct entrypoint's full option surface.

---

## Getting help

```bash
fire --help
```
