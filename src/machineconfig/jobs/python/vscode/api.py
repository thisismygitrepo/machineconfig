from pathlib import Path
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from machineconfig.utils.accessories import randstr


def open_file_in_new_instance(file_path: str):
    import git

    repo = git.Repo(search_parent_directories=True)
    repo_path = repo.working_tree_dir
    # Ensure repo_path is not None before passing to Path
    repo_name = Path(repo_path if repo_path is not None else ".").name
    repo_copy_name = f"{repo_name}_{randstr(5)}"
    copy_path = Path.home().joinpath(".config", "machingconfig", "vscode_api", repo_name, repo_copy_name)
    copy_path.parent.mkdir(parents=True, exist_ok=True)
    code = f"""
ln -s {repo_path} {copy_path}
cd {copy_path}
code --profile bitProfile --new-window {file_path}
"""
    console = Console()
    panel = Panel(
        Syntax(code, lexer="bash"),
        title="🔍 VS CODE API | Opening file in new instance",
        subtitle=f"📂 {file_path}",
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2),
    )
    console.print(panel)

    code_path = Path.home().joinpath(".config", "machingconfig", "vscode_api", "code_temp")
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(code, encoding="utf-8")
    code_path.chmod(0o755)
    import subprocess

    subprocess.run([str(code_path)], shell=True, check=True)


def main(file_path: Annotated[str, typer.Argument(help="Path to the file to open")]) -> None:
    open_file_in_new_instance(file_path)


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
