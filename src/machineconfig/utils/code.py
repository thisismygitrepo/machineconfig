import platform
from typing import Optional
import subprocess
import os
# import time
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from machineconfig.utils.accessories import randstr
from machineconfig.utils.ve import get_ve_activate_line
from machineconfig.utils.path_extended import PathExtended


def get_shell_script_executing_python_file(python_file: str, func: Optional[str], ve_path: Optional[str], executable: Optional[str], strict_execution: bool = True):
    if executable is None: exe_resolved = "python"
    else: exe_resolved = executable
    if func is None: exec_line = f"""{exe_resolved} {python_file}"""
    else: exec_line = f"""{exe_resolved} -m fire {python_file} {func}"""
    if ve_path is None: ve_activate_line = ""
    else: ve_activate_line = get_ve_activate_line(ve_path)
    shell_script = f"""
echo "Executing `{exec_line}`"
{ve_activate_line}
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


def get_shell_file_executing_python_script(python_script: str, ve_path: Optional[str], executable: Optional[str], verbose: bool = True):
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
    shell_script = get_shell_script_executing_python_file(python_file=str(python_file), func=None, ve_path=ve_path, executable=executable)
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


def run_shell_script(script: str, display_script: bool = True, clean_env: bool = False):
    import tempfile
    if platform.system() == "Windows":
        suffix = ".ps1"
        lexer = "powershell"
    else:
        suffix = ".sh"
        lexer = "bash"
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as temp_file:
        temp_file.write(script)
        temp_script_path = PathExtended(temp_file.name)
    console = Console()
    if display_script:
        from rich.syntax import Syntax
        console.print(Panel(Syntax(code=script, lexer=lexer), title=f"📄 shell script @ {temp_script_path}", subtitle="shell script being executed"), style="bold red")
    env = {} if clean_env else None
    if platform.system() == "Windows":
        import subprocess
        proc = subprocess.run(f'powershell -ExecutionPolicy Bypass -File "{temp_script_path}"', check=True, shell=True, env=env)
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        import subprocess
        proc = subprocess.run(f"bash {str(temp_script_path)}", check=True, shell=True, env=env)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")
    # console.print(f"✅  [green]Script executed successfully:[/green] [blue]{temp_script_path}[/blue]")
    if proc.returncode != 0:
        console.print(f"❌  [red]Script execution failed with return code {proc.returncode}:[/red] [blue]{temp_script_path}[/blue]")
    elif proc.returncode == 0:
        console.print(f"✅  [green]Script executed successfully:[/green] [blue]{temp_script_path}[/blue]")
    else:
        console.print(f"⚠️  [yellow]Script executed with warnings (return code {proc.returncode}):[/yellow] [blue]{temp_script_path}[/blue]")    
    temp_script_path.unlink(missing_ok=True)
    console.print(f"🗑️  [blue]Temporary script deleted:[/blue] [green]{temp_script_path}[/green]")
    return proc


def run_shell_script_after_exit(script: str, check_interval: float = 0.1, display_script: bool = True) -> subprocess.Popen[bytes]:
    current_pid = os.getpid()
    console = Console()
    
    if platform.system() == "Windows":
        monitor_script = f"""$ErrorActionPreference = "Stop"
$targetPid = {current_pid}
$checkInterval = {check_interval}

Write-Host "🔍 Monitoring process PID: $targetPid"

while ($true) {{
    $process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if (-not $process) {{
        Write-Host "✅ Process $targetPid has exited. Running script..."
        break
    }}
    Start-Sleep -Seconds $checkInterval
}}

# Execute the provided script
{script}
"""
        suffix = ".ps1"
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-NoProfile", "-WindowStyle", "Hidden", "-File"]
    else:
        monitor_script = f"""#!/bin/bash
target_pid={current_pid}
check_interval={check_interval}

echo "🔍 Monitoring process PID: $target_pid"

while kill -0 $target_pid 2>/dev/null; do
    sleep $check_interval
done

echo "✅ Process $target_pid has exited. Running script..."

# Execute the provided script
{script}
"""
        suffix = ".sh"
        cmd = ["bash"]
    
    monitor_script_path = PathExtended.tmp().joinpath("tmp_scripts", "monitor", randstr() + suffix)
    monitor_script_path.parent.mkdir(parents=True, exist_ok=True)
    monitor_script_path.write_text(monitor_script, encoding="utf-8")
    
    if display_script:
        lexer = "powershell" if platform.system() == "Windows" else "bash"
        console.print(Panel(Syntax(code=monitor_script, lexer=lexer), title=f"📄 Monitor script @ {monitor_script_path}", subtitle="Will run after current process exits"), style="bold yellow")
    
    if platform.system() != "Windows":
        monitor_script_path.chmod(0o755)
    
    cmd.append(str(monitor_script_path))
    
    if platform.system() == "Windows":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS  # type: ignore
        process = subprocess.Popen(cmd, creationflags=creation_flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    else:
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
    if display_script:
        console.print(f"🚀 [green]Monitor process started with PID:[/green] [blue]{process.pid}[/blue]")
        console.print(f"📍 [yellow]Watching PID:[/yellow] [blue]{current_pid}[/blue]")
    
    return process

