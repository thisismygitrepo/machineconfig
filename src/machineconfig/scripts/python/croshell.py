#!/usr/bin/env -S uv run --no-dev --project

"""
croshell
"""

from typing import Annotated, Optional
import typer
from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.utils.accessories import randstr

from machineconfig.utils.options import choose_from_options
from machineconfig.utils.ve import get_ve_activate_line
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def add_print_header_pycode(path: str, title: str):
    return f"""
try:
    from crocodile.file_management import P as PathExtended
except ImportError:
    from machineconfig.utils.path_extended import PathExtended
pycode = PathExtended(r'{path}').read_text(encoding="utf-8")
pycode = pycode.split("except Exception: print(pycode)")[2]

try:
    from rich.text import Text
    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console()
    if pycode.strip() != "":
        console.print(Panel(Syntax(pycode, lexer="python"), title='{title}'), style="bold red")
except Exception: print(pycode)
"""


def get_read_data_pycode(path: str):
    # We need to be careful here since we're generating Python code as a string
    # that will use f-strings itself
    return f"""
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
console = Console()
p = PathExtended(r'{path}').absolute()
try:
    dat = p.readit()
    if isinstance(dat, dict):
        panel_title = f"📄 File Data: {{p.name}}"
        console.print(Panel(Text(str(dat), justify="left"), title=panel_title, expand=False))
        pprint(dat, PathExtended.name)
    else:
        panel_title = f"📄 Successfully read the file: {{p.name}}"
        console.print(Panel(Text(str(dat), justify="left"), title=panel_title, expand=False))
except Exception as e:
    error_message = f'''❌ ERROR READING FILE\nFile: {{p.name}}\nError: {{e}}'''
    console.print(Panel(Text(error_message, justify="left"), title="Error", expand=False, border_style="red"))
"""


def get_read_pyfile_pycode(path: PathExtended, as_module: bool, cmd: str = ""):
    if as_module:
        pycode = rf"""
import sys
sys.path.append(r'{path.parent}')
from {path.stem} import *
{cmd}
"""
    else:
        pycode = f"""
__file__ = PathExtended(r'{path}')
{path.read_text(encoding="utf-8")}
"""
    return pycode


def main(
    module: Annotated[bool, typer.Option("--module", "-m", help="flag to run the file as a module as opposed to main.")] = False,
    newWindow: Annotated[bool, typer.Option("--newWindow", "-w", help="flag for running in new window.")] = False,
    nonInteratctive: Annotated[bool, typer.Option("--nonInteratctive", "-N", help="flag for a non-interactive session.")] = False,
    python: Annotated[bool, typer.Option("--python", "-p", help="flag to use python over IPython.")] = False,
    fzf: Annotated[bool, typer.Option("--fzf", "-F", help="search with fuzzy finder for python scripts and run them")] = False,
    ve: Annotated[Optional[str], typer.Option("--ve", "-v", help="virtual enviroment to use, defaults to activated ve, if existed, else ve.")] = None,
    profile: Annotated[Optional[str], typer.Option("--profile", "-P", help="ipython profile to use, defaults to default profile.")] = None,
    read: Annotated[str, typer.Option("--read", "-r", help="read a binary file.")] = "",
    file: Annotated[str, typer.Option("--file", "-f", help="python file path to interpret")] = "",
    cmd: Annotated[str, typer.Option("--cmd", "-c", help="python command to interpret")] = "",
    terminal: Annotated[str, typer.Option("--terminal", "-t", help="specify which terminal to be used. Default console host.")] = "",
    shell: Annotated[str, typer.Option("--shell", "-S", help="specify which shell to be used. Defaults to CMD.")] = "",
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="run in jupyter interactive console")] = False,
    streamlit_viewer: Annotated[bool, typer.Option("--stViewer", "-s", help="view in streamlit app")] = False,
) -> None:
    # ==================================================================================
    # flags processing
    interactivity = "" if nonInteratctive else "-i"
    interpreter = "python" if python else "ipython"
    ipython_profile: Optional[str] = profile
    file_obj = PathExtended.cwd()  # initialization value, could be modified according to args.

    if cmd != "":
        text = "🖥️  Executing command from CLI argument"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        import textwrap

        program = textwrap.dedent(cmd)

    elif fzf:
        text = "🔍 Searching for Python files..."
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        options = [str(item) for item in PathExtended.cwd().search("*.py", r=True)]
        file_selected = choose_from_options(msg="Choose a python file to run", options=options, fzf=True, multi=False)
        assert isinstance(file_selected, str)
        program = PathExtended(file_selected).read_text(encoding="utf-8")
        text = f"📄 Selected file: {PathExtended(file_selected).name}"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))

    elif file != "":
        file_obj = PathExtended(file.lstrip()).expanduser().absolute()
        program = get_read_pyfile_pycode(file_obj, as_module=module, cmd=cmd)
        text1 = f"📄 Loading file: {file_obj.name}"
        text2 = f"🔄 Mode: {'Module' if module else 'Script'}"
        console.print(Panel(f"{text1}\n{text2}", title="[bold blue]Info[/bold blue]"))

    elif read != "":
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
            return None
        file_obj = PathExtended(str(read).lstrip()).expanduser().absolute()
        program = get_read_data_pycode(str(file_obj))
        text = f"📄 Reading data from: {file_obj.name}"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))

    else:  # if nothing is specified, then run in interactive mode.
        text = "⌨️  Entering interactive mode"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        # from machineconfig.scripts.python.croshell import InteractiveShell
        # InteractiveShell().run()
        # return None
        program = ""

    preprogram = """

#%%
try:
    from crocodile.croshell import *
    print_header()
    print_logo(logo="crocodile")
except ImportError:
    print("Crocodile not found, skipping import.")
from pathlib import Path
print(f"🐊 Crocodile Shell | Running @ {Path.cwd()}")
"""

    pyfile = PathExtended.tmp().joinpath(f"tmp_scripts/python/croshell/{randstr()}.py")
    pyfile.parent.mkdir(parents=True, exist_ok=True)

    if read != "":
        title = "Reading Data"
    elif file != "":
        title = "Running Python File"
    else:
        title = "Executed code"
    total_program = preprogram + add_print_header_pycode(str(pyfile), title=title) + program

    pyfile.write_text(total_program, encoding="utf-8")

    # ve_root_from_file, ipython_profile = get_ve_path_and_ipython_profile(PathExtended(file))
    ipython_profile = ipython_profile if ipython_profile is not None else "default"
    # ve_activateion_line = get_ve_activate_line(ve_name=args.ve or ve_profile_suggested, a_path=str(PathExtended.cwd()))
    activate_ve_line = get_ve_activate_line(ve_root="$HOME/code/machineconfig/.venv")
    final_program = f"""
#!/bin/bash

{activate_ve_line}

"""
    if jupyter:
        fire_line = f"code --new-window {str(pyfile)}"
    else:
        fire_line = interpreter
        if interpreter == "ipython":
            fire_line += f" {interactivity} --profile {ipython_profile} --no-banner"
        fire_line += f" {str(pyfile)}"

    final_program += fire_line

    title = "🚀 LAUNCHING SCRIPT"
    text1 = f"📄 Script: {pyfile}"
    text2 = f"🔥 Command: {fire_line}"
    launch_message = f"{title}   \n{text1}\n{text2}"
    console.print(Panel(Text(launch_message, justify="left"), expand=False, border_style="blue"))

    # PROGRAM_PATH.write_text(data=final_program, encoding="utf-8")
    # (PROGRAM_PATH + ".py").write_text(str(pyfile), encoding='utf-8')
    import subprocess

    subprocess.run(final_program, shell=True, check=True)


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
