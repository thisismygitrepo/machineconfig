# Optimization Recommendations for `machineconfig` CLI

To improve the startup time of the `machineconfig` CLI, we should minimize top-level imports. Currently, `mcfg_entry.py` and several intermediate modules import many other modules at the top level. This causes the Python interpreter to load and execute all these modules (and their dependencies) every time the CLI is run, even if the user is running a command that doesn't need them.

Here are the specific recommendations:

## 1. `src/machineconfig/scripts/python/mcfg_entry.py`

**Current State:**
Imports all sub-apps (`devops`, `cloud`, `agents`, `sessions`, `utils`, `ftpx`, `croshell`, `fire_jobs`, `terminal`) at the top level.

**Recommendation:**
Move these imports inside the `get_app` function.

```python
def get_app():
    import typer
    # Move these imports here:
    from machineconfig.scripts.python.devops import get_app as get_devops_app
    from machineconfig.scripts.python.cloud import get_app as get_cloud_app
    from machineconfig.scripts.python.agents import get_app as get_agents_app
    from machineconfig.scripts.python.sessions import get_app as get_sessions_app
    from machineconfig.scripts.python.utils import get_app as get_utils_app

    from machineconfig.scripts.python.ftpx import ftpx as ftpx_func
    from machineconfig.scripts.python.croshell import croshell as croshell_func
    from machineconfig.scripts.python.fire_jobs import fire as get_fire_jobs_app
    from machineconfig.scripts.python.terminal import get_app as get_terminal_app
    
    app = typer.Typer(...)
    # ... rest of the function
```

## 2. `src/machineconfig/scripts/python/devops.py`

**Current State:**
Imports helper modules (`cli_repos`, `cli_config`, `cli_self`, `cli_data`, `cli_nw`, `run_script`) at the top level.

**Recommendation:**
Move these imports inside the `get_app` function.

```python
def get_app():
    # ...
    import machineconfig.scripts.python.helpers_devops.cli_repos as cli_repos
    import machineconfig.scripts.python.helpers_devops.cli_config as cli_config
    import machineconfig.scripts.python.helpers_devops.cli_self as cli_self
    import machineconfig.scripts.python.helpers_devops.cli_data as cli_data
    import machineconfig.scripts.python.helpers_devops.cli_nw as cli_network
    import machineconfig.scripts.python.helpers_devops.run_script as run_py_script_module
    
    cli_app = typer.Typer(...)
    # ...
```

## 3. `src/machineconfig/scripts/python/cloud.py`

**Current State:**
Imports helper modules (`cloud_sync`, `cloud_copy`, `cloud_mount`) at the top level.

**Recommendation:**
Move these imports inside the `get_app` function.

```python
def get_app():
    import typer
    from machineconfig.scripts.python.helpers_cloud.cloud_sync import main as sync_main
    from machineconfig.scripts.python.helpers_cloud.cloud_copy import main as copy_main
    from machineconfig.scripts.python.helpers_cloud.cloud_mount import mount as mount_main
    
    app = typer.Typer(...)
    # ...
```

## 4. `src/machineconfig/scripts/python/utils.py`

**Current State:**
Imports helper modules (`pdf`, `python`, `download`) at the top level.

**Recommendation:**
Move these imports inside the `get_app` function.

```python
def get_app() -> typer.Typer:
    from machineconfig.scripts.python.helpers_utils.pdf import merge_pdfs, compress_pdf
    from machineconfig.scripts.python.helpers_utils.python import edit_file_with_hx, get_machine_specs, init_project, tui_env
    from machineconfig.scripts.python.helpers_utils.download import download
    
    app = typer.Typer(...)
    # ...
```

## 5. `src/machineconfig/scripts/python/helpers_devops/cli_repos.py`

**Current State:**
Imports `cloud_repo_sync` at the top level.

**Recommendation:**
Move the import inside `get_app`.

```python
def get_app():
    from machineconfig.scripts.python.helpers_repos.cloud_repo_sync import main as secure_repo_main
    # ...
    repos_apps.command(name="secure", ...)(secure_repo_main)
    # ...
```

## 6. `src/machineconfig/scripts/python/helpers_devops/cli_config.py`

**Current State:**
Imports `cli_config_dotfile` and `create_links_export` at the top level.

**Recommendation:**
Move these imports inside `get_app`.

```python
def get_app():
    import machineconfig.scripts.python.helpers_devops.cli_config_dotfile as dotfile_module
    import machineconfig.profile.create_links_export as create_links_export
    
    config_apps = typer.Typer(...)
    # ...
```

## 7. `src/machineconfig/scripts/python/helpers_devops/cli_nw.py`

**Current State:**
Imports `cli_share_file`, `cli_share_terminal`, `cli_share_server`, `cli_ssh` at the top level.

**Recommendation:**
Move these imports inside `get_app`.

```python
def get_app():
    import machineconfig.scripts.python.helpers_devops.cli_share_file
    import machineconfig.scripts.python.helpers_devops.cli_share_terminal as cli_share_terminal
    import machineconfig.scripts.python.helpers_devops.cli_share_server as cli_share_server
    import machineconfig.scripts.python.helpers_devops.cli_ssh as cli_ssh
    
    nw_apps = typer.Typer(...)
    # ...
```

## 8. `src/machineconfig/scripts/python/helpers_devops/cli_share_server.py`

**Current State:**
Imports `cli_share_file` at the top level.

**Recommendation:**
Move the import inside `get_share_file_app`.

```python
def get_share_file_app():
    from machineconfig.scripts.python.helpers_devops.cli_share_file import share_file_receive, share_file_send
    app = typer.Typer(...)
    # ...
```

## 9. `src/machineconfig/scripts/python/helpers_devops/run_script.py`

**Current State:**
Imports `machineconfig.jobs.scripts_dynamic.a` inside `get_app`. Since `get_app` is called at startup, `a.py` (and its dependencies like `psutil` and `rich`) is imported at startup.

**Recommendation:**
Wrap the usage of `a.main` in a function that imports it lazily.

```python
def get_app():
    app = typer.Typer(
        name="run-tmp-script",
        help="Helper to run temporary python scripts stored in machineconfig/scripts/python/helpers/tmp_py_scripts",
        no_args_is_help=True,
    )
    
    def run_dynamic_script_a():
        """Run the dynamic script 'a'."""
        from machineconfig.jobs.scripts_dynamic import a
        a.main()

    app.command(name="a")(run_dynamic_script_a)
    return app
```

## Summary

By applying these changes, the initial import of `mcfg_entry.py` will only load `typer` (and standard libraries). The heavy lifting of importing other modules will be deferred until the specific command or subcommand is actually invoked. This is especially important for a CLI with many subcommands where a user typically only runs one at a time.
