# croshell

`croshell` builds a temporary `uv run` launch context, then opens it in an interactive backend such as IPython, Python, Marimo, Jupyter, VS Code, or VisiData.

---

## Usage

```bash
croshell [OPTIONS] [PATH]
```

## Arguments

| Argument | Description |
| --- | --- |
| `PATH` | Optional file or directory to inspect before launching the backend |

---

## Options

| Option | Short | Description |
| --- | --- | --- |
| `--project` | `-p` | Reuse a specific `uv` project directory |
| `--uv-with` | `-w` | Add extra packages to the launch environment |
| `--backend` | `-b` | Backend: `ipython`, `python`, `marimo`, `jupyter`, `vscode`, or `visidata` |
| `--profile` | `-r` | IPython profile name |
| `--self` | `-s` | Point the project at `~/code/machineconfig` when that checkout exists |
| `--frozen` | `-f` | Add `--frozen` to the `uv run` invocation |

The backend option also accepts short aliases from the current enum mapping:

- `ipython` or `i`
- `python` or `p`
- `marimo` or `m`
- `jupyter` or `j`
- `vscode` or `c`
- `visidata` or `v`

---

## Current launch behavior

`croshell` does more than open a shell:

- if `PATH` is a Python file, it stages that file inside a generated temporary script
- if `PATH` is a non-Python file, it generates a reader script using Machineconfig file readers and prints the parsed content in the chosen backend
- if `PATH` is omitted, it still creates a temporary script and launches the selected backend in the current context

Project resolution is currently:

1. explicit `--project`, if provided
2. nearest `.ve.yaml` or `.venv` discovered from the selected file
3. `~/code/machineconfig`, if that checkout exists and nothing else was selected

---

## Backend-specific notes

- `ipython` is the default backend.
- `python` runs the generated script with plain Python instead of IPython.
- `marimo` converts the generated script to `marimo_nb.py` in a temporary directory, then runs `marimo edit --host 0.0.0.0`.
- `jupyter` emits a temporary `.ipynb` and opens it in JupyterLab.
- `vscode` initializes a temporary `uv` workspace and opens the generated script in VS Code.
- `visidata` opens the selected file directly with `vd`; JSON files use plain `visidata`, other files add `pyarrow`.

---

## Examples

```bash
# Launch the default IPython backend
croshell

# Open a Python file with IPython
croshell script.py --backend ipython

# Inspect a data file with VisiData
croshell data.csv --backend visidata

# Open a generated notebook in Marimo
croshell analysis.py --backend marimo --project .

# Force the Machineconfig checkout as the uv project
croshell src/machineconfig/scripts/python/croshell.py --self
```

---

## Getting help

```bash
croshell --help
```
