


import typer

from typing import Optional
from pathlib import Path
from typing import Annotated, Literal, TypedDict


def path():
    """📚 NAVIGATE PATH variable with TUI"""
    from machineconfig.scripts.python import env_manager as navigator
    from pathlib import Path
    path = Path(navigator.__file__).resolve().parent.joinpath("path_manager_tui.py")
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script
    uv_with = ["textual"]
    uv_project_dir = None
    if not Path.home().joinpath("code/machineconfig").exists():
        uv_with.append("machineconfig>=7.65")
    else:
        uv_project_dir = str(Path.home().joinpath("code/machineconfig"))
    run_shell_script(get_uv_command_executing_python_script(python_script=path.read_text(encoding="utf-8"), uv_with=uv_with, uv_project_dir=uv_project_dir)[0])


def init_project(python: Annotated[Literal["3.13", "3.14"], typer.Option("--python", "-p", help="Python version for the uv virtual environment.")]= "3.13") -> None:
    _ = python
    repo_root = Path.cwd()
    if not (repo_root / "pyproject.toml").exists():
        typer.echo("❌ Error: pyproject.toml not found.", err=True)
        raise typer.Exit(code=1)
    print("Adding group `plot` with common data science and plotting packages...")
    script = """
uv add --group plot \
    # Data & computation
    numpy pandas polars duckdb-engine python-magic \
    # Plotting / visualization
    matplotlib plotly kaleido \
    # Notebooks / interactive
    ipython ipykernel jupyterlab nbformat marimo \
    # Code analysis / type checking / linting
    mypy pyright ruff pylint pyrefly \
    # Packaging / build / dev
    cleanpy \
    # CLI / debugging / utilities
    ipdb pudb \
    # Type hints for packages
    types-python-dateutil types-pyyaml types-requests types-tqdm \
    types-mysqlclient types-paramiko types-pytz types-sqlalchemy types-toml types-urllib3 \

"""
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script)


def edit_file_with_hx(path: Annotated[Optional[str], typer.Argument(..., help="The root directory of the project to edit, or a file path.")] = None) -> None:
    if path is None:
        root_path = Path.cwd()
        print(f"No path provided. Using current working directory: {root_path}")
    else:
        root_path = Path(path).expanduser().resolve()
        print(f"Using provided path: {root_path}")
    from machineconfig.utils.accessories import get_repo_root
    repo_root = get_repo_root(root_path)
    if repo_root is not None and repo_root.joinpath("pyproject.toml").exists():
        code = f"""
cd {repo_root}
uv add --dev pylsp-mypy python-lsp-server[all] pyright ruff-lsp  # for helix editor.
source ./.venv/bin/activate
"""
    else:
        code = ""
    if root_path.is_file():
        code += f"hx {root_path}"
    else:
        code += "hx"
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(code)


class MachineSpecs(TypedDict):
    system: str
    distro: str
    home_dir: str


def get_machine_specs() -> MachineSpecs:
    """Write print and return the local machine specs."""
    import platform
    UV_RUN_CMD = "$HOME/.local/bin/uv run" if platform.system() != "Windows" else """& "$env:USERPROFILE/.local/bin/uv" run"""
    command = f"""{UV_RUN_CMD} --with distro python -c "import distro; print(distro.name(pretty=True))" """
    import subprocess
    distro = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    specs: MachineSpecs = {
        "system": platform.system(),
        "distro": distro,
        "home_dir": str(Path.home()),
    }
    print(specs)
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    path = CONFIG_ROOT.joinpath("machine_specs.json")
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    import json
    path.write_text(json.dumps(specs, indent=4), encoding="utf-8")
    return specs

