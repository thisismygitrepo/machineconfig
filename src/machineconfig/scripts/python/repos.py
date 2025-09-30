"""Repos CLI powered by Typer.

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""


from pathlib import Path
from typing import Annotated, Optional

import typer


from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH
from pathlib import Path


def _print_banner() -> None:
    typer.echo("\n" + "=" * 50)
    typer.echo("📂 Welcome to the Repository Manager")
    typer.echo("=" * 50 + "\n")



app = typer.Typer(help="� Manage development repositories", no_args_is_help=True)
sync_app = typer.Typer(help="� Manage repository specifications and syncing", no_args_is_help=True)
app.add_typer(sync_app, name="sync", help="� Sync repositories using saved specs")


DirectoryArgument = Annotated[
    Optional[str],
    typer.Argument(help="📁 Folder containing repos or the specs JSON file to use."),
]
RecursiveOption = Annotated[
    bool,
    typer.Option("--recursive", "-r", help="🔍 Recurse into nested repositories."),
]
NoSyncOption = Annotated[
    bool,
    typer.Option("--no-sync", help="🚫 Disable automatic uv sync after pulls."),
]
CloudOption = Annotated[
    Optional[str],
    typer.Option("--cloud", "-c", help="☁️ Upload to or download from this cloud remote."),
]




def _resolve_directory(directory: Optional[str]) -> Path:
    if directory is None:
        directory = Path.cwd().as_posix()
        typer.echo(f"📁 Using directory: {directory}")
    return Path(directory).expanduser().absolute()


def _git_operations(
    directory: Optional[str],
    *,
    pull: bool,
    commit: bool,
    push: bool,
    recursive: bool,
    no_sync: bool,
) -> None:
    _print_banner()
    repos_root = _resolve_directory(directory)
    auto_sync = not no_sync
    from machineconfig.scripts.python.repos_helper_action import perform_git_operations
    from machineconfig.utils.path_extended import PathExtended
    perform_git_operations(
        repos_root=PathExtended(repos_root),
        pull=pull,
        commit=commit,
        push=push,
        recursive=recursive,
        auto_sync=auto_sync,
    )


def _resolve_spec_path(directory: Optional[str], cloud: Optional[str]) -> Path:
    repos_root = _resolve_directory(directory)
    from machineconfig.utils.path_extended import PathExtended
    if not repos_root.exists() or repos_root.name != "repos.json":
        candidate = Path(CONFIG_PATH).joinpath("repos").joinpath(PathExtended(repos_root).rel2home()).joinpath("repos.json")
        repos_root = candidate
        if not repos_root.exists():
            cloud_name: Optional[str]
            if cloud is None:
                from machineconfig.utils.io import read_ini
                cloud_name = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
                typer.echo(f"⚠️ Using default cloud: {cloud_name}")
            else:
                cloud_name = cloud
            assert cloud_name is not None, (
                f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
            )
            from machineconfig.utils.path_extended import PathExtended
            PathExtended(repos_root).from_cloud(cloud=cloud_name, rel2home=True)
    assert repos_root.exists() and repos_root.name == "repos.json", (
        f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
    )
    return repos_root


def _clone_from_specs(
    directory: Optional[str],
    cloud: Optional[str],
    *,
    checkout_branch_flag: bool,
    checkout_commit_flag: bool,
) -> None:
    _print_banner()
    typer.echo("\n📥 Cloning or checking out repositories...")
    spec_path = _resolve_spec_path(directory, cloud)
    from machineconfig.scripts.python.repos_helper_clone import clone_repos

    clone_repos(
        spec_path=spec_path,
        preferred_remote=None,
        checkout_branch_flag=checkout_branch_flag,
        checkout_commit_flag=checkout_commit_flag,
    )


@app.command()
def push(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """🚀 Push changes across repositories."""
    _git_operations(directory, pull=False, commit=False, push=True, recursive=recursive, no_sync=no_sync)


@app.command()
def pull(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """⬇️ Pull changes across repositories."""
    _git_operations(directory, pull=True, commit=False, push=False, recursive=recursive, no_sync=no_sync)


@app.command()
def commit(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """💾 Commit changes across repositories."""
    _git_operations(directory, pull=False, commit=True, push=False, recursive=recursive, no_sync=no_sync)


@app.command()
def all(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """🔄 Pull, commit, and push changes across repositories."""
    _git_operations(directory, pull=True, commit=True, push=True, recursive=recursive, no_sync=no_sync)


@sync_app.command()
def record(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """📝 Record repositories into a repos.json specification."""
    _print_banner()
    repos_root = _resolve_directory(directory)
    from machineconfig.scripts.python.repos_helper_record import main as record_repos
    save_path = record_repos(repos_root=repos_root)
    from machineconfig.utils.path_extended import PathExtended
    if cloud is not None:
        PathExtended(save_path).to_cloud(rel2home=True, cloud=cloud)


@sync_app.command()
def capture(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """📥 Clone repositories described by a repos.json specification."""
    _clone_from_specs(directory, cloud, checkout_branch_flag=False, checkout_commit_flag=False)


@sync_app.command(name="checkout")
def checkout_command(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """🔀 Check out specific commits listed in the specification."""
    _clone_from_specs(directory, cloud, checkout_branch_flag=False, checkout_commit_flag=True)


@sync_app.command(name="checkout-to-branch")
def checkout_to_branch_command(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """🔀 Check out to the main branch defined in the specification."""
    _clone_from_specs(directory, cloud, checkout_branch_flag=True, checkout_commit_flag=False)


@app.command()
def analyze(
    directory: DirectoryArgument = None,
) -> None:
    """📊 Analyze repository development over time."""
    _print_banner()
    repo_path = directory if directory is not None else "."
    from machineconfig.scripts.python.count_lines_frontend import analyze_repo_development as _analyze

    _analyze(repo_path=repo_path)

