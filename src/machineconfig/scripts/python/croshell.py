#!/usr/bin/env -S uv run --no-dev --project

"""
croshell
"""

from typing import Annotated, Optional
from machineconfig.scripts.python.helpers_croshell.crosh import code, get_read_data_pycode
from machineconfig.utils.meta import lambda_to_python_script
import typer
from machineconfig.utils.path_extended import PathExtended
from pathlib import Path
from machineconfig.utils.accessories import randstr
import json
from machineconfig.utils.options import choose_from_options
from rich.console import Console
from rich.panel import Panel


console = Console()


def croshell(
    path: Annotated[Optional[str], typer.Argument(help="path of file to read.")] = "",
    python: Annotated[bool, typer.Option("--python", "-p", help="flag to use python over IPython.")] = False,
    profile: Annotated[Optional[str], typer.Option("--profile", "-P", help="ipython profile to use, defaults to default profile.")] = None,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="run in jupyter interactive console")] = False,
    vscode: Annotated[bool, typer.Option("--vscode", "-c", help="open the script in vscode")] = False,
    streamlit_viewer: Annotated[bool, typer.Option("--streamlit", "-s", help="view in streamlit app")] = False,
    visidata: Annotated[bool, typer.Option("--visidata", "-v", help="open data file in visidata")] = False,
    marimo: Annotated[bool, typer.Option("--marimo", "-m", help="open the notebook using marimo if available")] = False,
) -> None:
    # ==================================================================================
    # flags processing
    interactivity = "-i"
    interpreter = "python" if python else "ipython"
    ipython_profile: Optional[str] = profile
    file_obj = PathExtended.cwd()  # initialization value, could be modified according to args.

    if path == ".":
        text = "🔍 Searching for Python files..."
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        options = [str(item) for item in PathExtended.cwd().search("*.py", r=True)]
        file_selected = choose_from_options(msg="Choose a python file to run", options=options, fzf=True, multi=False)
        assert isinstance(file_selected, str)
        program = PathExtended(file_selected).read_text(encoding="utf-8")
        text = f"📄 Selected file: {PathExtended(file_selected).name}"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))

    elif path != "" and path is not None:
        if streamlit_viewer:
            #             text = "📊 STARTING STREAMLIT VIEWER"
            #             console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
            #             from machineconfig.scripts.python.viewer import run
            #             py_file_path = run(data_path=args.read, data=None, get_figure=None)
            #             final_program = f"""
            # #!/bin/bash
            # streamlit run {py_file_path}
            # """
            #             PROGRAM_PATH.write_text(data=final_program, encoding="utf-8")
            print("Streamlit viewer is not yet implemented in this version.")
            return None
        file_obj = PathExtended(str(path).lstrip()).expanduser().absolute()
        program = lambda_to_python_script(lambda: get_read_data_pycode(path=str(file_obj)), in_global=True, import_module=False)
        text = f"📄 Reading data from: {file_obj.name}"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
    else:  # if nothing is specified, then run in interactive mode.
        # text = "⌨️  Entering interactive mode"
        # console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        # from machineconfig.scripts.python.croshell import InteractiveShell
        # InteractiveShell().run()
        # return None
        program = ""
    preprogram = """
#%%
"""
    def preprogram_func():
        from machineconfig.utils.files.headers import print_header, print_logo
        print_header()
        print_logo("CROCODILE")
        from pathlib import Path
        from machineconfig.utils.path_extended import PathExtended
        _ = Path, PathExtended  # avoid unused import warnings
    import inspect, textwrap
    from types import FunctionType
    def get_body_simple_function_no_args(f: FunctionType):
        return textwrap.dedent("\n".join(inspect.getsource(f).splitlines()[1:]))
    preprogram += get_body_simple_function_no_args(preprogram_func)

    pyfile = PathExtended.tmp().joinpath(f"tmp_scripts/python/croshell/{randstr()}/script.py")
    pyfile.parent.mkdir(parents=True, exist_ok=True)

    title = "Reading Data"
    def_code = lambda_to_python_script(lambda: code(path=str(pyfile), title=title), in_global=False, import_module=False)
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
            fire_line = f"uv run --python 3.14 --with visidata vd {str(file_obj)}"
        else:
            fire_line = f"uv run --python 3.14 --with visidata,pyarrow vd {str(file_obj)}"
    elif marimo:
        if Path.home().joinpath("code/machineconfig").exists(): requirements = f"""--with marimo --project "{str(Path.home().joinpath("code/machineconfig"))}" """
        else: requirements = """--python 3.14 --with "marimo,machineconfig[plot]>=6.57" """
        fire_line = f"""
cd {str(pyfile.parent)}
uv run --python 3.14 --with "marimo" marimo convert {pyfile.name} -o marimo_nb.py
uv run {requirements} marimo edit --host 0.0.0.0 marimo_nb.py
"""
    elif jupyter:
        if Path.home().joinpath("code/machineconfig").exists(): requirements = f"""--project "{str(Path.home().joinpath("code/machineconfig"))}" --with jupyterlab """
        else: requirements = """--with "machineconfig[plot]>=6.57" """
        fire_line = f"uv run {requirements} jupyter-lab {str(nb_target)}"
    elif vscode:
        fire_line = f"""
cd {str(pyfile.parent)}
uv init --python 3.14
uv venv
uv add "machineconfig[plot]>=6.57"
# code serve-web
code --new-window {str(pyfile)}
"""
    else:
        if interpreter == "ipython": profile = f" --profile {ipython_profile} --no-banner"
        else: profile = ""
        if Path.home().joinpath("code/machineconfig").exists(): ve_line = f"""--project "{str(Path.home().joinpath("code/machineconfig"))}" """
        else: ve_line = """--python 3.14 --with "machineconfig[plot]>=6.57" """
        # ve_path_maybe, ipython_profile_maybe = get_ve_path_and_ipython_profile(Path.cwd())
        # --python 3.14
        fire_line = f"uv run {ve_line} {interpreter} {interactivity} {profile} {str(pyfile)}"

    import os
    program_path_maybe = os.environ.get("OP_PROGRAM_PATH", None)
    if program_path_maybe is not None:
        program_path_obj = PathExtended(program_path_maybe)
        program_path_obj.parent.mkdir(parents=True, exist_ok=True)
        program_path_obj.write_text(data=fire_line, encoding="utf-8")
    else:
        from machineconfig.utils.code import run_shell_script
        run_shell_script(fire_line, clean_env=False)


def main() -> None:
    typer.run(croshell)


if __name__ == "__main__":
    # def func(flag: Annotated[bool, typer.Option("--flag/-nf", help="dummy flag for debugging", flag_value=False, is_flag=True)]=True):
    #     console.print(f"flag: {flag}")
    # app = typer.Typer()
    # app.command()(func)
    # app()
    main()
