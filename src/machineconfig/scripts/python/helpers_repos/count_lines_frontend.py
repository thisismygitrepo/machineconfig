
import typer
from typing import Annotated


def analyze_repo_development(repo_path: Annotated[str, typer.Argument(..., help="Path to the git repository")]):
    from machineconfig.scripts.python.helpers_repos import count_lines
    from pathlib import Path
    count_lines_path = Path(count_lines.__file__)
    # --project $HOME/code/ machineconfig --group plot
    cmd = f"""uv run --python 3.14 --with "machineconfig[plot]>=7.93" {count_lines_path} analyze-over-time {repo_path}"""
    from machineconfig.utils.code import run_shell_script
    run_shell_script(cmd)


if __name__ == "__main__":
    pass
