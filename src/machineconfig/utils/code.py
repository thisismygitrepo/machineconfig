from typing import Optional
import platform
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from crocodile.core import randstr
from crocodile.file_management import P
from crocodile.meta import Terminal


PROGRAM_PATH = (P.home().joinpath("tmp_results", "shells", "python_return_command") + (".ps1" if platform.system() == "Windows" else ".sh"))


def get_shell_script_executing_python_file(python_file: str, func: Optional[str] = None, ve_name: str="ve", strict_execution: bool=True):
    if func is None: exec_line = f"""python {python_file}"""
    else: exec_line = f"""python -m fire {python_file} {func}"""
    shell_script = f"""
. $HOME/scripts/activate_ve {ve_name}
echo "Executing {exec_line}"
{exec_line}
deactivate || true
"""

    if strict_execution:
        if platform.system() == "Windows": shell_script = """$ErrorActionPreference = "Stop" """ + "\n" + shell_script
        if platform.system() == "Linux": shell_script = "set -e" + "\n" + shell_script

    if platform.system() == "Linux": shell_script = "#!/bin/bash" + "\n" + shell_script  # vs #!/usr/bin/env bash
    return shell_script


def write_shell_script_to_file(shell_script: str):
    if platform.system() == "Linux": suffix = ".sh"
    elif platform.system() == "Windows": suffix = ".ps1"
    else: raise NotImplementedError(f"Platform {platform.system()} not implemented.")
    shell_file = P.tmp().joinpath("tmp_scripts", "shell", randstr() + suffix).create(parents_only=True).write_text(shell_script)
    return shell_file

# Enhanced print/log/error/exception statements for better clarity and consistency
# Improved formatting and language of messages
# Ensured consistent use of f-strings with triple quotes where applicable

def write_shell_script_to_default_program_path(program: str, desc: str, preserve_cwd: bool, display: bool, execute: bool):
    if preserve_cwd:
        if platform.system() == "Windows":
            program = "$orig_path = $pwd\n" + program + "\ncd $orig_path"
        else:
            program = 'orig_path=$(cd -- "." && pwd)\n' + program + '\ncd "$orig_path" || exit'
    if display:
        print(f"""
{'=' * 60}
⚙️  SHELL SCRIPT | Executing at {PROGRAM_PATH}
{'=' * 60}
""")
        print_code(code=program, lexer="shell", desc=desc)
    PROGRAM_PATH.create(parents_only=True).write_text(program)
    if execute:
        Terminal().run(f". {PROGRAM_PATH}", shell="powershell").capture().print_if_unsuccessful(desc="🛠️  EXECUTION | Shell script running", strict_err=True, strict_returncode=True)
    return None

def get_shell_file_executing_python_script(python_script: str, ve_name: str, verbose: bool=True):
    if verbose:
        python_script = f"""
code = r'''{python_script}'''
try:
    from machineconfig.utils.utils import print_code
    print_code(code=code, lexer="python", desc="Python Script")
except ImportError: print(f"\\n{'=' * 60}\\n📜 PYTHON SCRIPT:\\n\\n{{code}}\\n{'=' * 60}\\n")
""" + python_script
    python_file = P.tmp().joinpath("tmp_scripts", "python", randstr() + ".py").create(parents_only=True).write_text(python_script)
    shell_script = get_shell_script_executing_python_file(python_file=python_file.to_str(), ve_name=ve_name)
    shell_file = write_shell_script_to_file(shell_script)
    return shell_file

def print_code(code: str, lexer: str, desc: str):
    if lexer == "shell":
        if platform.system() == "Windows": lexer = "powershell"
        elif platform.system() == "Linux": lexer = "sh"
        else: raise NotImplementedError(f"Platform {platform.system()} not supported for lexer {lexer}")
    console = Console()
    console.print(Panel(Syntax(code=code, lexer=lexer), title=f"📄 {desc}"), style="bold red")

