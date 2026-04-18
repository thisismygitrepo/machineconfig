# Code Generation and Command Launching

`machineconfig` uses a small set of helper modules to turn Python callables into runnable scripts, wrap them in `uv run`, execute shell snippets, and bootstrap missing CLIs when a workflow depends on them.

The relevant modules are:

- `machineconfig.utils.meta`
- `machineconfig.utils.code`
- `machineconfig.utils.installer_utils.installer_cli`

---

## What this layer provides

| API area | Main helpers |
| --- | --- |
| Callable-to-script conversion | `get_import_module_string()`, `lambda_to_python_script()` |
| `uv` command generation | `get_uv_command()`, `get_uv_command_executing_python_file()`, `get_uv_command_executing_python_script()` |
| Callable launchers | `get_shell_script_running_lambda_function()`, `run_lambda_function()`, `run_python_script_in_marimo()` |
| Shell execution | `run_shell_file()`, `run_shell_script()` |
| Shell handoff | `exit_then_run_shell_script()`, `exit_then_run_shell_file()` |
| Tool bootstrapping | `install_if_missing(which, binary_name, verbose)` |

---

## From a lambda to runnable Python

`lambda_to_python_script()` expects a no-argument lambda whose body is a call expression, for example:

```python
lambda: build_report(days=7, include_failed=True)
```

It resolves the target callable from the lambda's globals and closure, evaluates keyword arguments, and emits Python source in one of two shapes:

- `in_global=False`: a rewritten function definition with updated defaults
- `in_global=True`: global assignments followed by the function body dedented into script form

When `import_module=True`, the generated source is prefixed with import bootstrap code from `get_import_module_string()` so the callable can be imported from its source file before execution.

Important current constraints:

- positional arguments are not reconstructed; keyword arguments are the intended path
- the lambda body must be a call
- generated source may add `from typing import Optional, Any, Union, Literal` if those annotations appear in the emitted script

---

## Building `uv run` commands

`machineconfig.utils.code` turns Python source into shell-ready commands.

### Current behavior

- `get_uv_command(platform)` returns the repo's expected `~/.local/bin/uv` path on Unix-like systems and `~/.local/bin/uv.exe` on Windows.
- `get_uv_command_executing_python_script()` writes the generated script to `~/tmp_results/tmp_scripts/python/<random>.py`.
- If `prepend_print=True`, the helpers inject preview-print code and ensure `rich` is added to the `uv` dependency list.
- `get_uv_command_executing_python_file()` chooses `--project "<dir>"` when `uv_project_dir` is set, otherwise it uses `--no-project`.

Example:

```python
from machineconfig.utils.code import get_shell_script_running_lambda_function


def rebuild_index(*, force: bool) -> None:
    print(force)


shell_script, py_file = get_shell_script_running_lambda_function(
    lambda: rebuild_index(force=True),
    uv_with=["machineconfig"],
    uv_project_dir=None,
    uv_run_flags="",
)

print(py_file)
print(shell_script)
```

---

## Running shell scripts

`run_shell_script()` writes the provided shell text to a temporary file, displays it with Rich when `display_script=True`, executes it with:

- `bash <temp-file>` on Linux and macOS
- `powershell -ExecutionPolicy Bypass -File "<temp-file>"` on Windows

and then deletes the temporary file.

`run_shell_file()` is the lower-level variant when the script already exists on disk.

`run_python_script_in_marimo()` writes a temporary Python file under `~/tmp_results/tmp_scripts/marimo/<random>/`, converts it with `marimo convert`, then launches `marimo edit`.

---

## `OP_PROGRAM_PATH` handoff

The two `exit_then_run_*` helpers are for workflows that want to hand control to another shell runner.

### `exit_then_run_shell_script()`

- If `OP_PROGRAM_PATH` points to a path that does not exist yet, the helper writes the script there and exits.
- Otherwise it runs the script immediately in the current process and exits.
- In `strict=True`, a missing or already-used handoff path causes a manual-run script to be written under `~/tmp_results/tmp_scripts/manual_run/`, then the process exits with an error.

### `exit_then_run_shell_file()`

- If a writable `OP_PROGRAM_PATH` is available, it writes either the PowerShell file path or `source <script_path>` into that handoff file and exits.
- Otherwise it runs the existing script file directly.

---

## Bootstrapping required tools

`install_if_missing(which, binary_name, verbose)` is the lightweight guard used by several higher-level helpers.

It:

1. checks whether `binary_name` or `which` is already on `PATH`
2. returns `True` immediately if it exists
3. otherwise calls `main_installer_cli()` to install it
4. returns `True` on success or `False` if installation raises

This is the mechanism used by helpers such as `get_public_ip_address()` and `switch_public_ip_address()` before they shell out to `ipinfo` or `warp-cli`.

---

## API reference

## Metaprogramming helpers

::: machineconfig.utils.meta
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Code and shell helpers

::: machineconfig.utils.code
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Installer guard helper

::: machineconfig.utils.installer_utils.installer_cli.install_if_missing
    options:
      show_root_heading: true
      show_source: false
