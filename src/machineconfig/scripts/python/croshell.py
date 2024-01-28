

"""
croshell
"""

import argparse
# import subprocess
# import platform
from crocodile.file_management import P, randstr
from machineconfig.utils.ve import get_ipython_profile, get_ve_profile
from machineconfig.utils.utils import PROGRAM_PATH, display_options


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
    pycode = f"""
p = P(r\'{path}\').absolute()
try:
    dat = p.readit()
    if type(dat) == Struct: dat.print(as_config=True, title=p.name)
    else: print(f"Succcesfully read the file {{p.name}}")
except Exception as e:
    print(e)

"""
    return pycode


def get_read_pyfile_pycode(path: P, as_module: bool, cmd: str = ""):
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
    parser.add_argument("--terminal", "-t", dest="terminal", help=f"specify which terminal to be used. Default console host.", default="")  # can choose `wt`
    parser.add_argument("--shell", "-S", dest="shell", help=f"specify which shell to be used. Defaults to CMD.", default="")

    args = parser.parse_args()
    # print(f"Crocodile.run: args of the firing command = {args.__dict__}")

    # ==================================================================================
    # flags processing
    interactivity = '' if args.nonInteratctive else '-i'
    interpreter = 'python' if args.python else 'ipython'
    profile = args.profile
    file = P.cwd()  # initialization value, could be modified according to args.

    if args.cmd != "":
        import textwrap
        program = textwrap.dedent(args.cmd)

    elif args.fzf:
        options = P.cwd().search("*.py", r=True).apply(str).list
        file = display_options(msg="Choose a python file to run", options=options, fzf=True, multi=False, )
        assert isinstance(file, str)
        if profile is None: profile = profile = get_ipython_profile(P(file))
        program = P(file).read_text(encoding='utf-8')

    elif args.file != "":
        file = P(args.file.lstrip()).expanduser().absolute()
        if profile is None: profile = profile = get_ipython_profile(P(file))
        program = get_read_pyfile_pycode(file, as_module=args.module, cmd=args.cmd)

    elif args.read != "":
        file = P(str(args.read).lstrip()).expanduser().absolute()
        if profile is None: profile = profile = get_ipython_profile(P(file))
        program = get_read_data_pycode(str(file))

    else:  # just run croshell.py interactively
        program = ""
        # program = f" --profile {get_ipython_profile(P.cwd())} --no-banner -m crocodile.croshell"  # --term-title croshell
        # from IPython import start_ipython
        # start_ipython(argv=program.split(' ')[1:])
        # return
        # Clear-Host;
        # # --autocall 1 in order to enable shell-like behaviour: e.g.: P x is interpretred as P(x)

    preprogram = """
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
    if profile is None: profile = "default"

    ve = get_ve_profile(P(file)) if args.ve is None else str(args.ve)

    final_program = f"""
# deactivate
. activate_ve {ve}
{interpreter} """
    if interpreter == "ipython": final_program += f"{interactivity} --profile {profile} --no-banner"
    final_program += f" {str(pyfile)}"
    print(f"🔥 sourcing  ... {pyfile}")
    PROGRAM_PATH.write_text(final_program)

    # if platform.system() == "Windows":
        # return subprocess.run([f"powershell", "-Command", res], shell=True, capture_output=False, text=True, check=True)
    # else: return subprocess.run([res], shell=True, capture_output=False, text=True, check=True)


if __name__ == "__main__":
    build_parser()
