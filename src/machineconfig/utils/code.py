
from typing import Any, Optional, Callable
from machineconfig.utils.accessories import randstr
from machineconfig.utils.meta import lambda_to_python_script
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


def get_uv_command_executing_python_script(python_script: str, uv_with: Optional[list[str]], uv_project_dir: Optional[str]) -> tuple[str, Path]:
    python_file = Path.home().joinpath("tmp_results", "tmp_scripts", "python", randstr() + ".py")
    python_file.parent.mkdir(parents=True, exist_ok=True)
    if uv_with is not None and len(uv_with) > 0:
        uv_with.append("rich")
        uv_with_arg = "--with " + '"' + ",".join(uv_with) + '"'
    else:
        uv_with_arg = "--with rich"
    if uv_project_dir is not None:
        uv_project_dir_arg = "--project" + f' "{uv_project_dir}"'
    else:
        uv_project_dir_arg = ""
    print_code_string = lambda_to_python_script(lambda: print_code(code=python_script, lexer="python", desc="Temporary Python Script", subtitle="Executing via shell script"), in_global=True, import_module=False)
    python_file.write_text(print_code_string + "\n" + python_script, encoding="utf-8")
    shell_script = f"""uv run {uv_with_arg} {uv_project_dir_arg}  {str(python_file)} """
    return shell_script, python_file


def run_lambda_function(lmb: Callable[[], Any], uv_with: Optional[list[str]], uv_project_dir: Optional[str]) -> None:
    code = lambda_to_python_script(lmb, in_global=True, import_module=False)
    uv_command, _py_file = get_uv_command_executing_python_script(python_script=code, uv_with=uv_with, uv_project_dir=uv_project_dir)
    run_shell_script(uv_command)
def run_python_script_in_marimo(py_script: str, uv_project_with: Optional[str]):
    tmp_dir = Path.home().joinpath("tmp_results", "tmp_scripts", "marimo", randstr())
    tmp_dir.mkdir(parents=True, exist_ok=True)
    pyfile = tmp_dir / "marimo_db_explore.py"
    pyfile.write_text(py_script, encoding="utf-8")
    if uv_project_with is not None:
        requirements = f"""--with "marimo" --project {uv_project_with} """
    else:
        requirements = f"""--with "marimo" """
    fire_line = f"""
cd {tmp_dir}
uv run {requirements} marimo convert {pyfile.name} -o marimo_nb.py
bat marimo_nb.py
uv run  {requirements} marimo edit --host 0.0.0.0 marimo_nb.py
"""
    print_code(code=py_script, desc="Generated Marimo DB Explore Script", lexer="python")
    exit_then_run_shell_script(fire_line)


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
        temp_script_path = Path(temp_file.name)
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


def exit_then_run_shell_script(script: str):
    import os
    op_program_path = os.environ.get("OP_PROGRAM_PATH", None)
    if op_program_path is not None:
        op_program_path = Path(op_program_path)
        op_program_path.parent.mkdir(parents=True, exist_ok=True)
        op_program_path.write_text(script, encoding="utf-8")
    else:
        run_shell_script(script)
