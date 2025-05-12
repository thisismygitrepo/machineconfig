"""
croshell
"""

import argparse
from crocodile.file_management import P
from crocodile.core_modules.core_1 import randstr
from machineconfig.utils.utils import PROGRAM_PATH, display_options
from machineconfig.utils.ve_utils.ve1 import get_ve_name_and_ipython_profile, get_ve_activate_line
from typing import Optional

BOX_WIDTH = 150  # width for box drawing


def _get_padding(text: str, padding_before: int = 2, padding_after: int = 1) -> str:
    """Calculate the padding needed to align the box correctly.
    
    Args:
        text: The text to pad
        padding_before: The space taken before the text (usually "║ ")
        padding_after: The space needed after the text (usually " ║")
    
    Returns:
        A string of spaces for padding
    """
    # Count visible characters (might not be perfect for all Unicode characters)
    text_length = len(text)
    padding_length = BOX_WIDTH - padding_before - text_length - padding_after
    return ' ' * max(0, padding_length)


def add_print_header_pycode(path: str, title: str):
    return f"""
pycode = P(r'{path}').read_text(encoding="utf-8")
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
p = P(r\'{path}\').absolute()
try:
    dat = p.readit()
    if isinstance(dat, dict): 
        text = "📄 File Data: " + str(p.name)
        spaces = ' ' * (150 - len(text) - 3)
        print(f'''
╔{'═' * 150}╗
║ {{text}}{{spaces}}║
╚{'═' * 150}╝
''')
        Struct(dat).print(as_config=True, title=p.name)
    else: 
        text = "📄 Successfully read the file: " + str(p.name)
        spaces = ' ' * (150 - len(text) - 3)
        print(f'''
╔{'═' * 150}╗
║ {{text}}{{spaces}}║
╚{'═' * 150}╝
''')
except Exception as e:
    error_text = "❌ ERROR READING FILE"
    error_spaces = ' ' * (150 - len(error_text) - 3)
    file_text = "File: " + str(p.name)
    file_spaces = ' ' * (150 - len(file_text) - 3)
    err_text = "Error: " + str(e)
    err_spaces = ' ' * (150 - len(err_text) - 3)
    print(f'''
╔{'═' * 150}╗
║ {{error_text}}{{error_spaces}}║
╠{'═' * 150}╣
║ {{file_text}}{{file_spaces}}║
║ {{err_text}}{{err_spaces}}║
╚{'═' * 150}╝
''')
"""


def get_read_pyfile_pycode(path: P, as_module: bool, cmd: str=""):
    if as_module: pycode = fr"""
import sys
sys.path.append(r'{path.parent}')
from {path.stem} import *
{cmd}
"""
    else: pycode = f"""
__file__ = P(r'{path}')
{path.read_text(encoding="utf-8")}
"""
    return pycode


def build_parser():
    parser = argparse.ArgumentParser(description="Generic Parser to launch crocodile shell.")
    # A FLAG:
    parser.add_argument("--module", '-m', help="flag to run the file as a module as opposed to main.", action="store_true", default=False)  # default is running as main, unless indicated by --module flag.
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
    interactivity = '' if args.nonInteratctive else '-i'
    interpreter = 'python' if args.python else 'ipython'
    ipython_profile: Optional[str] = args.profile
    file = P.cwd()  # initialization value, could be modified according to args.

    if args.cmd != "":
        text = "🖥️  Executing command from CLI argument"
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ {text}{_get_padding(text)}│
╰{'─' * BOX_WIDTH}╯
""")
        import textwrap
        program = textwrap.dedent(args.cmd)

    elif args.fzf:
        text = "🔍 Searching for Python files..."
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ {text}{_get_padding(text)}│
╰{'─' * BOX_WIDTH}╯
""")
        options = P.cwd().search("*.py", r=True).apply(str).list
        file = display_options(msg="Choose a python file to run", options=options, fzf=True, multi=False, )
        assert isinstance(file, str)
        program = P(file).read_text(encoding='utf-8')
        text = f"📄 Selected file: {P(file).name}"
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ {text}{_get_padding(text)}│
╰{'─' * BOX_WIDTH}╯
""")

    elif args.file != "":
        file = P(args.file.lstrip()).expanduser().absolute()
        program = get_read_pyfile_pycode(file, as_module=args.module, cmd=args.cmd)
        text1 = f"📄 Loading file: {file.name}"
        text2 = f"🔄 Mode: {'Module' if args.module else 'Script'}"
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ {text1}{_get_padding(text1)}│
│ {text2}{_get_padding(text2)}│
╰{'─' * BOX_WIDTH}╯
""")

    elif args.read != "":
        if args.streamlit_viewer:
            text = "📊 STARTING STREAMLIT VIEWER"
            print(f"""
╔{'═' * BOX_WIDTH}╗
║ {text}{_get_padding(text)}║
╚{'═' * BOX_WIDTH}╝
""")
            from machineconfig.scripts.python.viewer import run
            py_file_path = run(data_path=args.read, data=None, get_figure=None)
            final_program = f"""
#!/bin/bash
. $HOME/scripts/activate_ve 've'
streamlit run {py_file_path}
"""
            PROGRAM_PATH.write_text(data=final_program)
            return None
        file = P(str(args.read).lstrip()).expanduser().absolute()
        program = get_read_data_pycode(str(file))
        text = f"📄 Reading data from: {file.name}"
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ {text}{_get_padding(text)}│
╰{'─' * BOX_WIDTH}╯
""")

    else:  # just run croshell.py interactively
        program = ""

        # from IPython import start_ipython
        # start_ipython(argv=program.split(' ')[1:])
        # return
        # Clear-Host;
        # # --autocall 1 in order to enable shell-like behaviour: e.g.: P x is interpretred as P(x)

    preprogram = """

#%%
from crocodile.croshell import *
print_header()
print_logo(logo="crocodile")
"""

    pyfile = P.tmp().joinpath(f"tmp_scripts/python/croshell/{randstr()}.py").create(parents_only=True)

    if args.read != "": title = "Reading Data"
    elif args.file != "": title = "Running Python File"
    else: title = "Executed code"
    total_program = preprogram + add_print_header_pycode(str(pyfile), title=title) + program

    pyfile.write_text(total_program, encoding='utf-8')

    ve_profile_suggested: Optional[str] = None
    if ipython_profile is None:
        ve_profile_suggested, ipython_profile = get_ve_name_and_ipython_profile(P(file))
        ipython_profile = ipython_profile if ipython_profile is not None else "default"
    ve_activateion_line = get_ve_activate_line(ve_name=args.ve or ve_profile_suggested, a_path=P.cwd())
    final_program = f"""
#!/bin/bash

{ve_activateion_line}

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
    print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}   {PROGRAM_PATH}{_get_padding(f"{title}   {PROGRAM_PATH}")}║
╠{'═' * BOX_WIDTH}╣
║ {text1}{_get_padding(text1)}║
║ {text2}{_get_padding(text2)}║
╚{'═' * BOX_WIDTH}╝
""")
    
    PROGRAM_PATH.write_text(data=final_program)
    # (PROGRAM_PATH + ".py").write_text(str(pyfile), encoding='utf-8')

    # if platform.system() == "Windows":
        # return subprocess.run([f"powershell", "-Command", res], shell=True, capture_output=False, text=True, check=True)
    # else: return subprocess.run([res], shell=True, capture_output=False, text=True, check=True)


if __name__ == "__main__":
    build_parser()
