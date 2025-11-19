

import typer
from typing import Annotated, Optional, Literal


def run_py_script(name: Annotated[str, typer.Argument(help="Name of the python script to run, e.g., 'a' for a.py")],
                  where: Annotated[Literal["all", "private", "public", "tmp"], typer.Option("--where", "-w", help="Where to look for the script: any, private, public, tmp")] = "all",
                  command: Annotated[Optional[bool], typer.Option(..., "--command", "-c", help="Run as command")] = False,
                #   use_machineconfig_env: Annotated[bool, typer.Option(..., "--use-machineconfig-env/--no-use-machineconfig-env", "-m/-nm", help="Whether to use the machineconfig python environment")] = False
                ) -> None:
    """
    Run a temporary python script stored in machineconfig/scripts/python/helpers/tmp_py_scripts.
    """
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    from pathlib import Path
    if command:
        exec(name)
        return
    if Path(name).is_file():
        if name.endswith(".py"):
            import machineconfig
            import subprocess
            import sys
            subprocess.run([sys.executable, name], cwd=machineconfig.__path__[0])
            return
        else:
            raise RuntimeError(f"File '{name}' is not a python (.py) file.")

    private_python_root = Path.home().joinpath("dotfiles/scripts/python")
    public_python_root = CONFIG_ROOT.joinpath("scripts_python")

    from machineconfig.utils.source_of_truth import LIBRARY_ROOT
    repo_python_root = LIBRARY_ROOT.joinpath("jobs", "scripts", "python_scripts")

    import platform
    if platform.system() == "Windows":
        private_shell_root = Path.home().joinpath("dotfiles/scripts/windows")
        public_shell_root = CONFIG_ROOT.joinpath("scripts_powershell")
        repo_shell_root = LIBRARY_ROOT.joinpath("jobs", "scripts", "powershell_scripts")
    elif platform.system() == "Darwin" or platform.system() == "Linux":
        private_shell_root = Path.home().joinpath("dotfiles/scripts/linux")
        public_shell_root = CONFIG_ROOT.joinpath("scripts_bash")
        repo_shell_root = LIBRARY_ROOT.joinpath("jobs", "scripts", "bash_scripts")
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported for shell scripts.")

    _ = private_shell_root, public_shell_root, repo_shell_root

    target_file: Optional[Path] = None
    candidates: list[Path] = []
    if where in ["all", "private"]:
        result = private_python_root.joinpath(f"{name}.py")
        if result.exists():
            target_file = result
        else:
            candidates.extend(private_python_root.rglob("*.py"))
    if target_file is None and where in ["all", "public"]:
        result = public_python_root.joinpath(f"{name}.py")
        if result.exists():
            target_file = result
        else:
            candidates.extend(public_python_root.rglob("*.py"))
    if target_file is None and where in ["all", "tmp"]:
        try:
            # src/machineconfig/jobs/scripts/python_scripts/a.py
            url = f"""https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/jobs/scripts/python_scripts/{name}.py"""
            print(f"Fetching temporary script from {url} ...")
            import requests
            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ ERROR: Could not fetch script '{name}.py' from repository. Status Code: {response.status_code}")
                raise RuntimeError(f"Could not fetch script '{name}.py' from repository.")
            script_content = response.text
            target_file = Path.home().joinpath("tmp_results", "tmp_scripts", "python", f"{name}.py")
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(script_content, encoding="utf-8")
        except Exception as e:
            print(f"❌ ERROR: Could not fetch script '{name}.py' from repository due to error: {e}")
            candidates += repo_python_root.rglob("*.py")

    if target_file is None:
        print(f"❌ ERROR: Could not find script '{name}.py'. Checked {len(candidates)} candidate files, trying interactively:")
        from machineconfig.utils.options import choose_from_options
        chosen_file = choose_from_options([str(p) for p in candidates], multi=False, msg="Select the script to run:")
        target_file = Path(chosen_file)

    from machineconfig.utils.code import get_uv_command_executing_python_script, exit_then_run_shell_script
    script_content = target_file.read_text(encoding="utf-8")
    shell_script, _shell_script_path = get_uv_command_executing_python_script(python_script=script_content, uv_project_dir=None, uv_with=None, prepend_print=False)
    exit_then_run_shell_script(script=shell_script)



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
    from machineconfig.jobs.scripts.python_scripts import a
    app.command()(a.main)
    return app
