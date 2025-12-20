import typer
from typing import Optional, Annotated, Literal, TypedDict, cast


def tui_env(which: Annotated[Literal["PATH", "p", "ENV", "e"], typer.Argument(help="Which environment variable to display.")] = "ENV") -> None:
    """📚 NAVIGATE PATH variable with TUI"""
    from machineconfig.scripts.python.helpers import helper_env as navigator
    from pathlib import Path

    match which:
        case "PATH" | "p":
            path = Path(navigator.__file__).resolve().parent.joinpath("path_manager_tui.py")
        case "ENV" | "e":
            path = Path(navigator.__file__).resolve().parent.joinpath("env_manager_tui.py")
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script

    uv_with = ["textual"]
    uv_project_dir = None
    if not Path.home().joinpath("code/machineconfig").exists():
        uv_with.append("machineconfig>=8.37")
    else:
        uv_project_dir = str(Path.home().joinpath("code/machineconfig"))
    run_shell_script(
        get_uv_command_executing_python_script(python_script=path.read_text(encoding="utf-8"), uv_with=uv_with, uv_project_dir=uv_project_dir)[0]
    )


def init_project(
    name: Annotated[Optional[str], typer.Option("--name", "-n", help="Name of the project.")] = None,
    tmp_dir: Annotated[bool, typer.Option("--tmp-dir", "-t", help="Use a temporary directory for the project initialization.")] = False,
    python: Annotated[
        Literal["3.11", "3.12", "3.13", "3.14"], typer.Option("--python", "-p", help="Python sub version for the uv virtual environment.")
    ] = "3.13",
    libraries: Annotated[
        Optional[str], typer.Option("--libraries", "-l", help="Additional packages to include in the uv virtual environment (space separated).")
    ] = None,
    group: Annotated[
        Optional[str], typer.Option("--group", "-g", help="group of packages names (no separation) p:plot, t:types, l:linting, i:interactive, d:data")
    ] = "p,t,l,i,d",
) -> None:
    if libraries is not None:
        packages_add_line = f"uv add {libraries}"
    else:
        packages_add_line = ""
    from pathlib import Path

    if not tmp_dir:
        repo_root = Path.cwd()
        if not (repo_root / "pyproject.toml").exists():
            typer.echo(f"❌ Error: pyproject.toml not found in {repo_root}", err=True)
            raise typer.Exit(code=1)
        starting_code = ""
        agents_line = ""
    else:
        agents_line = """agents make-config"""
        if name is not None:
            from machineconfig.utils.accessories import randstr

            repo_root = Path.home().joinpath(f"tmp_results/tmp_projects/{name}")
        else:
            from machineconfig.utils.accessories import randstr

            repo_root = Path.home().joinpath(f"tmp_results/tmp_projects/{randstr(6)}")
        repo_root.mkdir(parents=True, exist_ok=True)
        print(f"Using temporary directory for project initialization: {repo_root}")
        starting_code = f"""
cd {repo_root}
uv init --python {python}
uv venv
"""
    print(f"Adding group `{group}` with common data science and plotting packages...")
    total_packages: dict[str, list[str]] = {}
    if group is not None:
        packages = group.split(",")
        if "t" in packages or "types" in packages:
            total_packages["types"] = [
                "types-python-dateutil",
                "types-pyyaml",
                "types-requests",
                "types-tqdm",
                "types-mysqlclient",
                "types-paramiko",
                "types-pytz",
                "types-sqlalchemy",
                "types-toml",
                "types-urllib3",
            ]
        if "l" in packages:
            total_packages["linting"] = ["mypy", "pyright", "ruff", "pylint", "pyrefly", "cleanpy", "ipdb", "pudb"]
        if "i" in packages:
            total_packages["interactive"] = ["ipython", "ipykernel", "jupyterlab", "nbformat", "marimo"]
        if "p" in packages:
            total_packages["plot"] = ["python-magic", "matplotlib", "plotly", "kaleido"]
        if "d" in packages:
            total_packages["data"] = ["numpy", "pandas", "polars", "duckdb-engine", "sqlalchemy", "psycopg2-binary", "pyarrow", "tqdm", "openpyxl"]
    from machineconfig.utils.ve import get_ve_activate_line
    groups_packages_lines = "\n".join(
        [f"uv add --group {group_name} {' '.join(packages)}" for group_name, packages in total_packages.items()]
    )   
    script = f"""
{starting_code}
{packages_add_line}
{groups_packages_lines}
{get_ve_activate_line(ve_root=str(repo_root.joinpath(".venv")))}
{agents_line}
ls
"""
    from machineconfig.utils.code import exit_then_run_shell_script, run_shell_script
    exit_then_run_shell_script(script)
    _ = exit_then_run_shell_script, run_shell_script
    # run_shell_script(script)
    # if tempdir:
    #     from machineconfig.scripts.python.ai.initai import add_ai_configs
    #     add_ai_configs(repo_root=repo_root)


def edit_file_with_hx(
    path: Annotated[Optional[str], typer.Argument(..., help="The root directory of the project to edit, or a file path.")] = None,
) -> None:
    from pathlib import Path

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
    system: Literal["Windows", "Linux", "Darwin"]
    distro: str
    home_dir: str
    hostname: str
    release: str
    version: str
    machine: str
    processor: str
    python_version: str
    user: str


def get_machine_specs(hardware: Annotated[bool, typer.Option(..., "--hardware", "-h", help="Show compute capability")] = False) -> MachineSpecs:
    """Write print and return the local machine specs."""
    if hardware:
        from machineconfig.scripts.python.helpers.helpers_utils.specs import main
        main()
        import sys
        sys.exit()

    import platform
    from machineconfig.utils.code import get_uv_command

    uv_cmd = get_uv_command(platform=platform.system())  # type: ignore
    command = f"""{uv_cmd} run --with distro python -c "import distro; print(distro.name(pretty=True))" """
    import subprocess
    from pathlib import Path
    import socket
    import os

    distro = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    system = platform.system()
    if system not in {"Windows", "Linux", "Darwin"}:
        system = "Linux"
    specs: MachineSpecs = {
        "system": cast(Literal["Windows", "Linux", "Darwin"], system),
        "distro": distro,
        "home_dir": str(Path.home()),
        "hostname": socket.gethostname(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor() or "Unknown",
        "python_version": platform.python_version(),
        "user": os.getenv("USER") or os.getenv("USERNAME") or "Unknown",
    }
    print(specs)
    from machineconfig.utils.source_of_truth import CONFIG_ROOT

    path = CONFIG_ROOT.joinpath("machine_specs.json")
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(specs, indent=4), encoding="utf-8")
    return specs


if __name__ == "__main__":
    get_machine_specs()
