"""Pure Python implementation for croshell command - no typer dependencies."""

from typing import Optional
from pathlib import Path


def croshell(
    path: Optional[str],
    project_path: Optional[str],
    uv_with: Optional[str],
    marimo: bool,
    jupyter: bool,
    vscode: bool,
    visidata: bool,
    python: bool,
    profile: Optional[str],
) -> None:
    """Cross-shell command execution."""
    if uv_with is not None:
        user_uv_with_line = f"--with {uv_with} "
    else:
        user_uv_with_line = ""

    if project_path is not None:
        uv_project_line = f'--project {project_path}'
        uv_python_line = ""
    else:
        uv_project_line = ""
        uv_python_line = "--python 3.14"

    from machineconfig.scripts.python.helpers.helpers_croshell.crosh import get_read_python_file_pycode, get_read_data_pycode
    from machineconfig.utils.meta import lambda_to_python_script
    from machineconfig.utils.accessories import randstr
    from machineconfig.utils.ve import get_ve_path_and_ipython_profile
    import json
    from rich.console import Console
    from rich.panel import Panel
    console = Console()

    interactivity = "-i"
    interpreter = "python" if python else "ipython"
    ipython_profile: Optional[str] = profile
    file_obj = Path.cwd()
    if path is not None:
        from machineconfig.utils.path_helper import get_choice_file
        choice_file = get_choice_file(path=path, suffixes={".*"})
        if project_path is None:
            ve_path, _ = get_ve_path_and_ipython_profile(choice_file)
            if ve_path is not None:
                ve_path_obj = Path(ve_path)
                uv_project_line = f'--project {ve_path_obj.parent}'
                uv_python_line = ""
        if choice_file.suffix == ".py":
            program = choice_file.read_text(encoding="utf-8")
            text = f"📄 Selected file: {choice_file.name}"
            console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        else:
            program = lambda_to_python_script(
                lambda: get_read_data_pycode(path=str(choice_file)),
                in_global=True, import_module=False
            )
            text = f"📄 Reading data from: {file_obj.name}"
            console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
    else:
        program = ""

    if Path.home().joinpath("code/machineconfig").exists() and uv_project_line == "":
        uv_project_line = f'--project "{str(Path.home().joinpath("code/machineconfig"))}"'

    preprogram = _build_preprogram()

    pyfile = Path.home().joinpath(f"tmp_results/tmp_scripts/python/croshell/{randstr()}/script.py")
    pyfile.parent.mkdir(parents=True, exist_ok=True)
    title = "Reading Data"
    def_code = lambda_to_python_script(
        lambda: get_read_python_file_pycode(path=str(pyfile), title=title),
        in_global=False, import_module=False
    )
    python_program = preprogram + "\n\n" + def_code + program
    pyfile.write_text(python_program, encoding="utf-8")
    ipython_profile = ipython_profile if ipython_profile is not None else "default"

    nb_target = pyfile.with_suffix(".ipynb")
    if jupyter:
        try:
            nb_path = pyfile.with_suffix(".ipynb")
            nb_content = {
                "cells": [
                    {
                        "cell_type": "code",
                        "metadata": {"language": "python"},
                        "source": [python_program],
                        "outputs": [],
                        "execution_count": None,
                    }
                ],
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
            nb_path.write_text(json.dumps(nb_content), encoding="utf-8")
            nb_target = nb_path
        except Exception:
            pass

    fire_line = _build_fire_line(
        file_obj=file_obj,
        pyfile=pyfile,
        nb_target=nb_target,
        visidata=visidata,
        marimo=marimo,
        jupyter=jupyter,
        vscode=vscode,
        interpreter=interpreter,
        interactivity=interactivity,
        ipython_profile=ipython_profile,
        uv_python_line=uv_python_line,
        uv_project_line=uv_project_line,
        user_uv_with_line=user_uv_with_line,
        uv_with=uv_with,
    )

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(fire_line, strict=False)


def _build_preprogram() -> str:
    """Build the preprogram code for croshell."""
    import inspect
    import textwrap
    from types import FunctionType

    def get_body_simple_function_no_args(f: FunctionType) -> str:
        return textwrap.dedent("\n".join(inspect.getsource(f).splitlines()[1:]))

    preprogram = """
#%%
"""

    def preprogram_func() -> None:
        try:
            from machineconfig.utils.files.headers import print_header, print_logo
            print_header()
            print_logo("Machineconfig")
            from machineconfig.utils.path_extended import PathExtended
            _ = PathExtended
        except ImportError:
            print("machineconfig is not installed in the current environment.")
            pass
        from pathlib import Path
        _ = Path

    preprogram += get_body_simple_function_no_args(preprogram_func)
    return preprogram


def _build_fire_line(
    file_obj: Path,
    pyfile: Path,
    nb_target: Path,
    visidata: bool,
    marimo: bool,
    jupyter: bool,
    vscode: bool,
    interpreter: str,
    interactivity: str,
    ipython_profile: str,
    uv_python_line: str,
    uv_project_line: str,
    user_uv_with_line: str,
    uv_with: Optional[str],
) -> str:
    """Build the fire line command for croshell."""
    if visidata:
        if file_obj.suffix == ".json":
            fire_line = f"uv run {uv_python_line} {user_uv_with_line} {uv_project_line} --with visidata vd {str(file_obj)}"
        else:
            fire_line = f"uv run {uv_python_line} {user_uv_with_line} {uv_project_line} --with visidata,pyarrow vd {str(file_obj)}"
    elif marimo:
        if Path.home().joinpath("code/machineconfig").exists():
            requirements = f"""{user_uv_with_line} {uv_project_line} --with marimo,sqlglot  """
        else:
            requirements = f"""{uv_python_line} {user_uv_with_line} {uv_project_line} --with "marimo,sqlglot,cowsay,machineconfig[plot]>=8.37" """
        fire_line = f"""
cd {str(pyfile.parent)}
uv run {uv_python_line} --with "marimo" marimo convert {pyfile.name} -o marimo_nb.py
uv run {requirements} marimo edit --host 0.0.0.0 marimo_nb.py
"""
    elif jupyter:
        if Path.home().joinpath("code/machineconfig").exists():
            requirements = f"""{user_uv_with_line}  {uv_project_line}  --with jupyterlab """
        else:
            requirements = f"""{user_uv_with_line} {uv_project_line} --with "cowsay,machineconfig[plot]>=8.37" """
        fire_line = f"uv run {requirements} {uv_project_line}  jupyter-lab {str(nb_target)}"
    elif vscode:
        user_uv_add = f"uv add {uv_with}" if uv_with is not None else ""
        fire_line = f"""
cd {str(pyfile.parent)}
uv init {uv_python_line}
uv venv
uv add "cowsay,machineconfig[plot]>=8.37"
uv add {user_uv_add}
# code serve-web
code --new-window {str(pyfile)}
"""
    else:
        if interpreter == "ipython":
            profile = f" --profile {ipython_profile} --no-banner"
        else:
            profile = ""
        if Path.home().joinpath("code/machineconfig").exists():
            ve_line = f"""{user_uv_with_line}  {uv_project_line} """
        else:
            ve_line = f"""{uv_python_line} {user_uv_with_line} {uv_project_line} --with "cowsay,machineconfig[plot]>=8.37" """
        fire_line = f"uv run {ve_line} {interpreter} {interactivity} {profile} {str(pyfile)}"

    return fire_line
