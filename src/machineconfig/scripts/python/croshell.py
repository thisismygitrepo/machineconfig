#!/usr/bin/env -S uv run --no-dev --project

"""
croshell

"""

from typing import Annotated, Optional
import typer


def croshell(
    path: Annotated[Optional[str], typer.Argument(help="path of file to read.")] = None,
    python: Annotated[bool, typer.Option("--python", "-P", help="flag to use python over IPython.")] = False,
    profile: Annotated[Optional[str], typer.Option("--profile", "-r", help="ipython profile to use, defaults to default profile.")] = None,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="run in jupyter interactive console")] = False,
    vscode: Annotated[bool, typer.Option("--vscode", "-c", help="open the script in vscode")] = False,
    project_path: Annotated[Optional[str], typer.Option("--project", "-p", help="specify uv project to use")] = None,
    # streamlit_viewer: Annotated[bool, typer.Option("--streamlit", "-s", help="view in streamlit app")] = False,
    uv_with: Annotated[Optional[str], typer.Option("--uv-with", "-w", help="specify uv with packages to use")] = None,
    visidata: Annotated[bool, typer.Option("--visidata", "-v", help="open data file in visidata")] = False,
    marimo: Annotated[bool, typer.Option("--marimo", "-m", help="open the notebook using marimo if available")] = False,
) -> None:
    if uv_with is not None: user_uv_with_line = f"--with {uv_with} "
    else: user_uv_with_line = ""

    if project_path is not None:
        uv_project_line = f'--project "{project_path}"'
    else:
        uv_project_line = ""

    from machineconfig.scripts.python.helpers_croshell.crosh import get_read_python_file_pycode, get_read_data_pycode
    from machineconfig.utils.meta import lambda_to_python_script
    from pathlib import Path
    from machineconfig.utils.accessories import randstr
    from machineconfig.utils.ve import get_ve_path_and_ipython_profile
    import json
    from rich.console import Console
    from rich.panel import Panel
    console = Console()


    # ==================================================================================
    # flags processing
    interactivity = "-i"
    interpreter = "python" if python else "ipython"
    ipython_profile: Optional[str] = profile
    file_obj = Path.cwd()  # initialization value, could be modified according to args.
    if path is not None:
        from machineconfig.utils.path_helper import get_choice_file
        choice_file = get_choice_file(path=path, suffixes={".*"})
        if project_path is None:
            ve_path, _ = get_ve_path_and_ipython_profile(choice_file)
            if ve_path is not None:
                ve_path_obj = Path(ve_path)
                uv_project_line = f'--project "{ve_path_obj.parent}"'
        if choice_file.suffix == ".py":
            program = choice_file.read_text(encoding="utf-8")
            text = f"📄 Selected file: {choice_file.name}"
            console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        else:
            program = lambda_to_python_script(lambda: get_read_data_pycode(path=str(choice_file)),
                                              in_global=True, import_module=False)
            text = f"📄 Reading data from: {file_obj.name}"
            console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
    else:  # if nothing is specified, then run in interactive mode.
        program = ""


    preprogram = """
#%%
"""
    def preprogram_func():
        from machineconfig.utils.files.headers import print_header, print_logo
        print_header()
        print_logo("Machineconfig")
        from pathlib import Path
        from machineconfig.utils.path_extended import PathExtended
        _ = Path, PathExtended  # avoid unused import warnings
    import inspect, textwrap
    from types import FunctionType
    def get_body_simple_function_no_args(f: FunctionType):
        return textwrap.dedent("\n".join(inspect.getsource(f).splitlines()[1:]))
    preprogram += get_body_simple_function_no_args(preprogram_func)

    from pathlib import Path
    pyfile = Path.home().joinpath(f"tmp_results/tmp_scripts/python/croshell/{randstr()}/script.py")
    pyfile.parent.mkdir(parents=True, exist_ok=True)
    title = "Reading Data"
    def_code = lambda_to_python_script(lambda: get_read_python_file_pycode(path=str(pyfile), title=title),
                                       in_global=False, import_module=False)
    # print(def_code)
    python_program = preprogram + "\n\n" + def_code + program
    pyfile.write_text(python_program, encoding="utf-8")
    # ve_root_from_file, ipython_profile = get_ve_path_and_ipython_profile(PathExtended(file))
    ipython_profile = ipython_profile if ipython_profile is not None else "default"
    # ve_activateion_line = get_ve_activate_line(ve_name=args.ve or ve_profile_suggested, a_path=str(PathExtended.cwd()))

    # prepare notebook target path (avoid relying on locals())
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
            # if writing fails, fall back to the default nb_target already set
            pass
    if visidata:
        if file_obj.suffix == ".json":
            fire_line = f"uv run --python 3.14 {user_uv_with_line} {uv_project_line} --with visidata vd {str(file_obj)}"
        else:
            fire_line = f"uv run --python 3.14 {user_uv_with_line} {uv_project_line} --with visidata,pyarrow vd {str(file_obj)}"
    elif marimo:
        if Path.home().joinpath("code/machineconfig").exists(): requirements = f"""{user_uv_with_line} {uv_project_line} --with marimo --project "{str(Path.home().joinpath("code/machineconfig"))}" """
        else: requirements = f"""--python 3.14 {user_uv_with_line} {uv_project_line} --with "marimo,cowsay,machineconfig[plot]>=7.93" """
        fire_line = f"""
cd {str(pyfile.parent)}
uv run --python 3.14 --with "marimo" marimo convert {pyfile.name} -o marimo_nb.py
uv run {requirements} marimo edit --host 0.0.0.0 marimo_nb.py
"""
    elif jupyter:
        if Path.home().joinpath("code/machineconfig").exists(): requirements = f"""{user_uv_with_line}  {uv_project_line}  --with jupyterlab --project "{str(Path.home().joinpath("code/machineconfig"))}" """
        else: requirements = f"""{user_uv_with_line} {uv_project_line} --with "cowsay,machineconfig[plot]>=7.93" """
        fire_line = f"uv run {requirements} {uv_project_line}  jupyter-lab {str(nb_target)}"
    elif vscode:
        user_uv_add = f"uv add {uv_with}" if uv_with is not None else ""
        fire_line = f"""
cd {str(pyfile.parent)}
uv init --python 3.14
uv venv
uv add "cowsay,machineconfig[plot]>=7.93"
uv add {user_uv_add}
# code serve-web
code --new-window {str(pyfile)}
"""
    else:
        if interpreter == "ipython": profile = f" --profile {ipython_profile} --no-banner"
        else: profile = ""
        if Path.home().joinpath("code/machineconfig").exists(): ve_line = f"""{user_uv_with_line}  {uv_project_line} --project "{str(Path.home().joinpath("code/machineconfig"))}" """
        else: ve_line = f"""--python 3.14 {user_uv_with_line} {uv_project_line} --with "cowsay,machineconfig[plot]>=7.93" """
        fire_line = f"uv run {ve_line} {interpreter} {interactivity} {profile} {str(pyfile)}"

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(fire_line, strict=False)


def main() -> None:
    typer.run(croshell)


if __name__ == "__main__":
    # def func(flag: Annotated[bool, typer.Option("--flag/-nf", help="dummy flag for debugging", flag_value=False, is_flag=True)]=True):
    #     console.print(f"flag: {flag}")
    # app = typer.Typer()
    # app.command()(func)
    # app()
    main()
