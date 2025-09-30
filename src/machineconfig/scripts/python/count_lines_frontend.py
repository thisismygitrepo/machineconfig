
import typer


def analyze_repo_development(repo_path: str = typer.Argument(..., help="Path to the git repository")):
    from machineconfig.scripts.python import count_lines
    from pathlib import Path
    count_lines_path = Path(count_lines.__file__).resolve().parent.joinpath("count_lines.py")
    # --project $HOME/code/machineconfig 
    cmd = f"""uv run --python 3.13 --with machineconfig--group plot {count_lines_path} analyze-over-time {repo_path}"""
    from machineconfig.utils.code import run_script
    run_script(cmd)


if __name__ == "__main__":
    pass
