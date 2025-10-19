import atexit
import platform
from typing import Optional
import subprocess
from machineconfig.utils.accessories import randstr
from machineconfig.utils.path_extended import PathExtended
from pathlib import Path


def print_code(code: str, lexer: str, desc: str, subtitle: str = ""):
    import platform
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    if lexer == "shell":
        if platform.system() == "Windows":
            lexer = "powershell"
        elif platform.system() in ["Linux", "Darwin"]:
            lexer = "sh"
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported for lexer {lexer}")
    console = Console()
    console.print(Panel(Syntax(code=code, lexer=lexer), title=f"📄 {desc}", subtitle=subtitle), style="bold red")


def get_shell_file_executing_python_script(python_script: str, uv_with: Optional[list[str]], uv_project_dir: Optional[str]) -> Path:
    python_file = PathExtended.tmp().joinpath("tmp_scripts", "python", randstr() + ".py")
    python_file.parent.mkdir(parents=True, exist_ok=True)
    python_file.write_text(python_script, encoding="utf-8")
    if uv_with is not None and len(uv_with) > 0:
        uv_with_arg = "--with " + '"' + ",".join(uv_with) + '"'
    else:
        uv_with_arg = ""
    if uv_project_dir is not None:
        uv_project_dir_arg = "--project" + f' "{uv_project_dir}"'
    else:
        uv_project_dir_arg = ""
    
    from machineconfig.utils.meta import lambda_to_defstring
    print_code_string = lambda_to_defstring(lambda: print_code(code=python_script, lexer="python", desc="Temporary Python Script", subtitle="Executing via shell script"), in_global=True)
    python_file_tmp = PathExtended.tmp().joinpath("tmp_scripts", "python", randstr() + ".py")
    python_file_tmp.parent.mkdir(parents=True, exist_ok=True)
    python_file_tmp.write_text(print_code_string, encoding="utf-8")

    shell_script = f"""
uv run --with rich {python_file_tmp}
uv run {uv_with_arg} {uv_project_dir_arg}  {str(python_file)} 
"""
    
    shell_path = PathExtended.tmp().joinpath("tmp_scripts", "shell", randstr() + (".ps1" if platform.system() == "Windows" else ".sh"))
    shell_path.parent.mkdir(parents=True, exist_ok=True)
    shell_path.write_text(shell_script, encoding="utf-8")    
    return shell_path


def run_shell_script(script: str, display_script: bool = True, clean_env: bool = False):
    import tempfile
    import platform
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

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


def run_shell_script_after_exit(script: str, display_script: bool = True) -> None:
    import platform
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

    console = Console()
    def execute_script_at_exit() -> None:
        if platform.system() == "Windows":
            suffix = ".ps1"
            lexer = "powershell"
        else:
            suffix = ".sh"
            lexer = "bash"
        
        script_path = PathExtended.tmp().joinpath("tmp_scripts", "exit", randstr() + suffix)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script, encoding="utf-8")
        
        if display_script:
            console.print(Panel(Syntax(code=script, lexer=lexer), title=f"📄 Exit script @ {script_path}", subtitle="Running at exit"), style="bold yellow")
        
        if platform.system() != "Windows":
            script_path.chmod(0o755)
        
        if platform.system() == "Windows":
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", str(script_path)], check=False)
        else:
            subprocess.run(["bash", str(script_path)], check=False)
        
        script_path.unlink(missing_ok=True)
    
    atexit.register(execute_script_at_exit)

