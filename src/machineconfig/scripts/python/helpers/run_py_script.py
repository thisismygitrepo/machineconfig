

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
        import machineconfig
        import subprocess
        import sys
        subprocess.run([sys.executable, name], cwd=machineconfig.__path__[0])
        return

    target_py_file: Optional[Path] = None
    if where in ["all", "private"]:
        result = Path.home().joinpath("dotfiles/scripts/python").joinpath(f"{name}.py")
        if result.exists():
            target_py_file = result
    if target_py_file is None and where in ["all", "public"]:
        result = CONFIG_ROOT.joinpath("scripts_python").joinpath(f"{name}.py")
        if result.exists():
            target_py_file = result
    if target_py_file is None and where in ["all", "tmp"]:
        url = f"""https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/scripts/python/helpers/tmp_py_scripts/{name}.py"""
        print(f"Fetching temporary script from {url} ...")
        import requests
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ ERROR: Could not fetch script '{name}.py' from repository. Status Code: {response.status_code}")
            raise RuntimeError(f"Could not fetch script '{name}.py' from repository.")
        script_content = response.text
        from machineconfig.utils.code import get_uv_command_executing_python_script, exit_then_run_shell_script
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
    from machineconfig.scripts.python.helpers.tmp_py_scripts import a
    app.command()(a.main)
    return app
