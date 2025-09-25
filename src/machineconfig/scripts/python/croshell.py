#!/usr/bin/env -S uv run --project

"""
croshell
"""

import argparse
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.utils2 import randstr

from machineconfig.utils.options import display_options
from machineconfig.utils.ve import get_ve_activate_line
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text  # Added import for rich.text
# from machineconfig.utils.utils2 import pprint

console = Console()


def add_print_header_pycode(path: str, title: str):
    return f"""
# from machineconfig.utils.path_reduced import P as PathExtended
from crocodile.file_management import P as PathExtended
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


def build_parser():
    parser = argparse.ArgumentParser(description="Generic Parser to launch crocodile shell.")
    # A FLAG:
    parser.add_argument("--module", "-m", help="flag to run the file as a module as opposed to main.", action="store_true", default=False)  # default is running as main, unless indicated by --module flag.
    parser.add_argument("--newWindow", "-w", help="flag for running in new window.", action="store_true", default=False)
    parser.add_argument("--nonInteratctive", "-N", help="flag for a non-interactive session.", action="store_true", default=False)
    parser.add_argument("--python", "-p", help="flag to use python over IPython.", action="store_true", default=False)
    parser.add_argument("--fzf", "-F", help="search with fuzzy finder for python scripts and run them", action="store_true", default=False)

    # OPTIONAL KEYWORD
    parser.add_argument("--ve", "-v", help="virtual enviroment to use, defaults to activated ve, if existed, else ve.", default=None)
    parser.add_argument("--profile", "-P", help="ipython profile to use, defaults to default profile.", default=None)
    parser.add_argument("--read", "-r", dest="read", help="read a binary file.", default="")
    parser.add_argument("--file", "-f", dest="file", help="python file path to interpret", default="")
    parser.add_argument("--cmd", "-c", dest="cmd", help="python command to interpret", default="")
    parser.add_argument("--terminal", "-t", dest="terminal", help="specify which terminal to be used. Default console host.", default="")  # can choose `wt`
    parser.add_argument("--shell", "-S", dest="shell", help="specify which shell to be used. Defaults to CMD.", default="")
    parser.add_argument("--jupyter", "-j", dest="jupyter", help="run in jupyter interactive console", action="store_true", default=False)
    parser.add_argument("--stViewer", "-s", dest="streamlit_viewer", help="view in streamlit app", action="store_true", default=False)

    args = parser.parse_args()
    # print(f"Crocodile.run: args of the firing command = {args.__dict__}")

    # ==================================================================================
    # flags processing
    interactivity = "" if args.nonInteratctive else "-i"
    interpreter = "python" if args.python else "ipython"
    ipython_profile: Optional[str] = args.profile
    file = PathExtended.cwd()  # initialization value, could be modified according to args.

    if args.cmd != "":
        text = "🖥️  Executing command from CLI argument"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        import textwrap

        program = textwrap.dedent(args.cmd)

    elif args.fzf:
        text = "🔍 Searching for Python files..."
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))
        options = [str(item) for item in PathExtended.cwd().search("*.py", r=True)]
        file = display_options(msg="Choose a python file to run", options=options, fzf=True, multi=False)
        assert isinstance(file, str)
        program = PathExtended(file).read_text(encoding="utf-8")
        text = f"📄 Selected file: {PathExtended(file).name}"
        console.print(Panel(text, title="[bold blue]Info[/bold blue]"))

    elif args.file != "":
        file = PathExtended(args.file.lstrip()).expanduser().absolute()
        program = get_read_pyfile_pycode(file, as_module=args.module, cmd=args.cmd)
        text1 = f"📄 Loading file: {file.name}"
        text2 = f"🔄 Mode: {'Module' if args.module else 'Script'}"
        console.print(Panel(f"{text1}\n{text2}", title="[bold blue]Info[/bold blue]"))

    elif args.read != "":
        if args.streamlit_viewer:
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
        file = PathExtended(str(args.read).lstrip()).expanduser().absolute()
        program = get_read_data_pycode(str(file))
        text = f"📄 Reading data from: {file.name}"
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
from crocodile.croshell import *
from pathlib import Path
print_header()
print_logo(logo="crocodile")
print(f"🐊 Crocodile Shell | Running @ {Path.cwd()}")
"""

    pyfile = PathExtended.tmp().joinpath(f"tmp_scripts/python/croshell/{randstr()}.py")
    pyfile.parent.mkdir(parents=True, exist_ok=True)

    if args.read != "":
        title = "Reading Data"
    elif args.file != "":
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
    if args.jupyter:
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

    # if platform.system() == "Windows":
    # return subprocess.run([f"powershell", "-Command", res], shell=True, capture_output=False, text=True, check=True)
    # else: return subprocess.run([res], shell=True, capture_output=False, text=True, check=True)


if __name__ == "__main__":
    build_parser()
