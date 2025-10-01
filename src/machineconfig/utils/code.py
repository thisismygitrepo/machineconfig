import platform
from typing import Optional
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from machineconfig.utils.accessories import randstr
from machineconfig.utils.ve import get_ve_activate_line
from machineconfig.utils.path_extended import PathExtended


def get_shell_script_executing_python_file(python_file: str, func: Optional[str], ve_path: str, strict_execution: bool = True):
    if func is None:
        exec_line = f"""python {python_file}"""
    else:
        exec_line = f"""python -m fire {python_file} {func}"""
    shell_script = f"""
echo "Executing `{exec_line}`"
{get_ve_activate_line(ve_path)}
{exec_line}
deactivate || true
"""
    if strict_execution:
        if platform.system() == "Windows":
            shell_script = """$ErrorActionPreference = "Stop" """ + "\n" + shell_script
        if platform.system() in ["Linux", "Darwin"]:
            shell_script = "set -e" + "\n" + shell_script
    if platform.system() in ["Linux", "Darwin"]:
        shell_script = "#!/bin/bash" + "\n" + shell_script  # vs #!/usr/bin/env bash
    return shell_script


def get_shell_file_executing_python_script(python_script: str, ve_path: str, verbose: bool = True):
    if verbose:
        python_script = f"""
code = r'''{python_script}'''
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
    shell_script = get_shell_script_executing_python_file(python_file=str(python_file), func=None, ve_path=ve_path)
    shell_file = write_shell_script_to_file(shell_script)
    return shell_file


def write_shell_script_to_file(shell_script: str):
    if platform.system() in ["Linux", "Darwin"]:
        suffix = ".sh"
    elif platform.system() == "Windows":
        suffix = ".ps1"
    else:
        raise NotImplementedError(f"Platform {platform.system()} not implemented.")
    shell_file = PathExtended.tmp().joinpath("tmp_scripts", "shell", randstr() + suffix)
    shell_file.parent.mkdir(parents=True, exist_ok=True)
    shell_file.write_text(shell_script, encoding="utf-8")
    return shell_file


def write_shell_script_to_default_program_path(program: str, desc: str, preserve_cwd: bool, display: bool, execute: bool):
    if preserve_cwd:
        if platform.system() == "Windows":
            program = "$orig_path = $pwd\n" + program + "\ncd $orig_path"
        else:
            program = 'orig_path=$(cd -- "." && pwd)\n' + program + '\ncd "$orig_path" || exit'
    if display:
        print_code(code=program, lexer="shell", desc=desc, subtitle="PROGRAM")
    if execute:
        result = subprocess.run(program, shell=True, capture_output=True, text=True)
        success = result.returncode == 0 and result.stderr == ""
        if not success:
            print("❌ 🛠️  EXECUTION | Shell script running failed")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            print(f"Return code: {result.returncode}")
    return None


def print_code(code: str, lexer: str, desc: str, subtitle: str = ""):
    if lexer == "shell":
        if platform.system() == "Windows":
            lexer = "powershell"
        elif platform.system() in ["Linux", "Darwin"]:
            lexer = "sh"
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported for lexer {lexer}")
    console = Console()
    console.print(Panel(Syntax(code=code, lexer=lexer), title=f"📄 {desc}", subtitle=subtitle), style="bold red")


def run_shell_script(program: str, display_script: bool = True):
    import tempfile
    if platform.system() == "Windows":
        suffix = ".ps1"
        lexer = "powershell"
    else:
        suffix = ".sh"
        lexer = "bash"
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as temp_file:
        temp_file.write(program)
        temp_script_path = PathExtended(temp_file.name)
    console = Console()
    if display_script:
        from rich.syntax import Syntax
        console.print(Panel(Syntax(code=program, lexer=lexer), title=f"📄 shell script @ {temp_script_path}", subtitle="shell script being executed"), style="bold red")

    if platform.system() == "Windows":
        import subprocess
        subprocess.run(f'powershell -ExecutionPolicy Bypass -File "{temp_script_path}"', check=True, shell=True)
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        import subprocess
        subprocess.run(f"bash {str(temp_script_path)}", check=True, shell=True)

    temp_script_path.unlink(missing_ok=True)

# def run_command(command: str, description: str) -> bool:
#     """Execute a shell command and return success status."""
#     console.print(f"\n🔧 {description}", style="bold cyan")
#     try:
#         result = subprocess.run(command, shell=True, check=True, capture_output=False)
#         return result.returncode == 0
#     except subprocess.CalledProcessError as e:
#         console.print(f"❌ Error executing command: {e}", style="bold red")
#         return False
