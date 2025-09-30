
import typer


def analyze_repo_development(repo_path: str = typer.Argument(..., help="Path to the git repository")):
    cmd = f"""uv run --python 3.13 --with machineconfig machineconfig.scripts.python.count_lines analyze-over-time {repo_path}"""
    from machineconfig.utils.code import run_script
    run_script(cmd)


if __name__ == "__main__":
    pass
