from pathlib import Path
from machineconfig.utils.utils2 import randstr


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
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel

    console = Console()
    console.print(f"\n{'=' * 150}")
    console.print(Panel(Syntax(code, lexer="bash"), title="🔍 VS CODE API | Opening file in new instance", subtitle=f"📂 {file_path}"), style="bold blue")
    console.print(f"{'=' * 150}\n")

    code_path = Path.home().joinpath(".config", "machingconfig", "vscode_api", "code_temp")
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(code, encoding="utf-8")
    code_path.chmod(0o755)
    import subprocess

    subprocess.run([str(code_path)], shell=True, check=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Open file in new vscode instance")
    parser.add_argument("file_path", type=str, help="Path to the file to open")
    args = parser.parse_args()
    open_file_in_new_instance(args.file_path)


if __name__ == "__main__":
    main()
