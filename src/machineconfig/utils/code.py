from typing import Optional
import platform
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from machineconfig.utils.utils2 import randstr
from machineconfig.utils.path_reduced import P as PathExtended


PROGRAM_PATH = (PathExtended.home().joinpath("tmp_results", "shells", "python_return_command") + (".ps1" if platform.system() == "Windows" else ".sh"))


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
        if platform.system() in ["Linux", "Darwin"]: shell_script = "set -e" + "\n" + shell_script

    if platform.system() in ["Linux", "Darwin"]: shell_script = "#!/bin/bash" + "\n" + shell_script  # vs #!/usr/bin/env bash
    return shell_script


def write_shell_script_to_file(shell_script: str):
    if platform.system() in ["Linux", "Darwin"]: suffix = ".sh"
    elif platform.system() == "Windows": suffix = ".ps1"
    else: raise NotImplementedError(f"Platform {platform.system()} not implemented.")
    shell_file = PathExtended.tmp().joinpath("tmp_scripts", "shell", randstr() + suffix)
    shell_file.parent.mkdir(parents=True, exist_ok=True)
    shell_file.write_text(shell_script, encoding="utf-8")
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
    if display: print_code(code=program, lexer="shell", desc=desc, subtitle=str(PROGRAM_PATH))
    PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRAM_PATH.write_text(program, encoding="utf-8")
    if execute:
        result = subprocess.run(f". {PROGRAM_PATH}", shell=True, capture_output=True, text=True)
        success = result.returncode == 0 and result.stderr == ""
        if not success:
            print(f"❌ 🛠️  EXECUTION | Shell script running failed")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            print(f"Return code: {result.returncode}")
    return None

def get_shell_file_executing_python_script(python_script: str, ve_name: str, verbose: bool=True):
    if verbose:
        python_script = f"""
code = r'''{python_script}''' """ + """
try:
    from machineconfig.utils.utils import print_code
    print_code(code=code, lexer="python", desc="Python Script")
except ImportError:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    console.print(Panel(f'''📜 PYTHON SCRIPT:\n\n{{code}}''', title="Python Script", expand=False))
""" + python_script
    python_file = PathExtended.tmp().joinpath("tmp_scripts", "python", randstr() + ".py")
    python_file.parent.mkdir(parents=True, exist_ok=True)
    python_file.write_text(python_script, encoding="utf-8")
    shell_script = get_shell_script_executing_python_file(python_file=str(python_file), ve_name=ve_name)
    shell_file = write_shell_script_to_file(shell_script)
    return shell_file

def print_code(code: str, lexer: str, desc: str, subtitle: str=""):
    if lexer == "shell":
        if platform.system() == "Windows": lexer = "powershell"
        elif platform.system() in ["Linux", "Darwin"]: lexer = "sh"
        else: raise NotImplementedError(f"Platform {platform.system()} not supported for lexer {lexer}")
    console = Console()
    console.print(Panel(Syntax(code=code, lexer=lexer), title=f"📄 {desc}", subtitle=subtitle), style="bold red")
