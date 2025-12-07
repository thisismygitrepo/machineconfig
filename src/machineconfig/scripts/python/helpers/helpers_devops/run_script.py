

"""run python/shell scripts from pre-defined directorys, or, run command/file in the machineconfig environment

Recursively Searched Predefined Directories:


* 'private' : $HOME/dotfiles/scripts

* 'public'  : $HOME/.config/machineconfig/scripts

* 'library' : $MACHINECONFIG_LIBRARY_ROOT/jobs/scripts

* 'dynamic' : fetched from GitHub repository on the fly (relies on latest commit, rather than the version currently installed)

* 'custom'  : custom directories from comma separated entry 'scripts' under 'general' section @ ~/dotfiles/machineconfig/defaults.ini

"""


import typer
from typing import Annotated, Optional, Literal


def run_py_script(name: Annotated[str, typer.Argument(help="Name of script to run, e.g., 'a' for a.py, or command to execute")] = "",
                  where: Annotated[Literal["all", "a", "private", "p", "public", "b", "library", "l", "dynamic", "d", "custom", "c"], typer.Option("--where", "-w", help="Where to look for the script")] = "all",
                  interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactive selection of scripts to run")] = False,
                  command: Annotated[Optional[bool], typer.Option(..., "--command", "-c", help="Run as command")] = False,
                  list_scripts: Annotated[bool, typer.Option(..., "--list", "-l", help="List available scripts in all locations")] = False,
                ) -> None:
    if command:
        exec(name)
        return

    from pathlib import Path
    if list_scripts:
        from machineconfig.scripts.python.helpers.helpers_search.script_help import list_available_scripts
        list_available_scripts(where=where)
        return

    if not interactive and not name:
        typer.echo("❌ ERROR: You must provide a script name or use --interactive option to select a script.")
        raise typer.Exit(code=1)
    target_file: Optional[Path] = None

    if where in ["dynamic", "d"]:
        # src/machineconfig/jobs/scripts/python_scripts/a.py
        if "." in name: resolved_names: list[str] = [name]
        else: resolved_names = [f"{name}{a_suffix}" for a_suffix in [".py", ".sh", "", ".ps1", ".bat", ".cmd"]]
        urls = [f"""https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/jobs/scripts_dynamic/{a_resolved_name}""" for a_resolved_name in resolved_names]
        for a_url in urls:
            try:
                print(f"Fetching temporary script from {a_url} ...")
                import requests
                response = requests.get(a_url)
                if response.status_code != 200:
                    print(f"❌ ERROR: Could not fetch script '{name}.py' from repository. Status Code: {response.status_code}")
                    raise RuntimeError(f"Could not fetch script '{name}.py' from repository.")
                script_content = response.text
                target_file = Path.home().joinpath("tmp_results", "tmp_scripts", "python", f"{name}.py")
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(script_content, encoding="utf-8")
            except Exception as _e:
                pass


    if target_file is None and Path(name).is_file():
        if name.endswith(".py"):
            import machineconfig
            import subprocess
            import sys
            subprocess.run([sys.executable, name], cwd=machineconfig.__path__[0])
            return
        else:
            if Path(name).suffix in [".sh", ".ps1", ".bat", ".cmd", ""]:
                target_file = Path(name)
            else:
                raise RuntimeError(f"File '{name}' is not a recognized script type. Supported types are {'.py', '.sh', '.ps1', '.bat', '.cmd', ''}.")

    from machineconfig.utils.source_of_truth import CONFIG_ROOT, LIBRARY_ROOT, DEFAULTS_PATH
    private_root = Path.home().joinpath("dotfiles/scripts")  # local directory
    public_root = CONFIG_ROOT.joinpath("scripts")  # local machineconfig directory
    library_root = LIBRARY_ROOT.joinpath("jobs", "scripts")

    def get_custom_roots() -> list[Path]:
        custom_roots: list[Path] = []
        if DEFAULTS_PATH.is_file():
            from configparser import ConfigParser
            config = ConfigParser()
            config.read(DEFAULTS_PATH)
            if config.has_section("general") and config.has_option("general", "scripts"):
                custom_dirs = config.get("general", "scripts").split(",")
                for custom_dir in custom_dirs:
                    custom_path = Path(custom_dir.strip()).expanduser().resolve()
                    if custom_path.is_dir():
                        custom_roots.append(custom_path)
        return custom_roots

    roots: list[Path] = []
    match where:
        case "all" | "a":
            roots = [private_root, public_root, library_root] + get_custom_roots()
        case "private" | "p":
            roots = [private_root]
        case "public" | "b":
            roots = [public_root]
        case "library" | "l":
            roots = [library_root]
        case "dynamic" | "d":
            roots = []
        case "custom" | "c":
            roots = get_custom_roots()

    suffixes: list[str]
    if "." in name:
        suffixes = [""]
    else:
        import platform
        if platform.system() == "Windows":
            suffixes = [".py", ".bat", ".cmd", ".ps1"]
        elif platform.system() == "Darwin" or platform.system() == "Linux":
            suffixes = [""]  # files without suffix could be shell scripts, and that already cover files with .sh suffix without duplications
        else:
            suffixes = [".py"]

    # Finding target file
    potential_matches: list[Path] = []
    if target_file is None:
        for a_root in roots:
            for a_suffix in suffixes:
                if a_root.joinpath(f"{name}{a_suffix}").is_file():
                    target_file = a_root.joinpath(f"{name}{a_suffix}")
                    break  # perfect match
                potential_matches += [a_file for a_file in a_root.rglob(f"*{name}*{a_suffix}") if a_file.is_file()]

    if target_file is None:
        if len(potential_matches) == 1:
            target_file = potential_matches[0]
        elif len(potential_matches) == 0:
            print(f"❌ ERROR: Could not find script '{name}'.")
            print("Searched in:")
            for r in roots:
                print(f"  - {r}")
            raise typer.Exit(code=1)
        else:
            print(f"Warning: Could not find script '{name}'. Checked {len(potential_matches)} candidate files, trying interactively:")
            from machineconfig.utils.options import choose_from_options
            options = [str(p) for p in potential_matches]
            chosen_file_part = choose_from_options(options, multi=False, msg="Select the script to run:", tv=True, preview="bat")
            target_file = Path(chosen_file_part)

    print(f"✅ Found script at: {target_file}")
    if target_file.suffix == ".py":
        from machineconfig.utils.code import get_uv_command_executing_python_file, exit_then_run_shell_script
        shell_script = get_uv_command_executing_python_file(python_file=str(target_file), uv_project_dir=None, uv_with=None, prepend_print=False)
        exit_then_run_shell_script(script=shell_script)
    else:
        from machineconfig.utils.code import exit_then_run_shell_file
        exit_then_run_shell_file(script_path=str(target_file), strict=True)


def copy_script_to_local(name: Annotated[str, typer.Argument(help="Name of the temporary python script to copy, e.g., 'a' for a.py")],
                         alias: Annotated[Optional[str], typer.Option("--alias", "-a", help="Whether to create call it a different name locally")] = None
                         ) -> None:
    """
    Copy a temporary python script stored in machineconfig/scripts/python/helpers/tmp_py_scripts to the local machine.
    """
    url = f"""https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/scripts/python/helpers/tmp_py_scripts/{name}.py"""
    import requests
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ ERROR: Could not fetch script '{name}.py' from repository. Status Code: {response.status_code}")
        raise RuntimeError(f"Could not fetch script '{name}.py' from repository.")
    script_content = response.text
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    local_path = CONFIG_ROOT.joinpath(f"scripts_python/{alias or name}.py")
    with open(local_path, "w") as f:
        f.write(script_content)
    print(f"✅ Script '{name}.py' has been copied to '{local_path}'.")


def get_app():
    app = typer.Typer(
        name="run-tmp-script",
        help="Helper to run temporary python scripts stored in machineconfig/scripts/python/helpers/tmp_py_scripts",
        no_args_is_help=True,
    )
    from machineconfig.jobs.scripts_dynamic import a
    app.command()(a.main)
    return app
