"""Repos CLI powered by Typer.

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""


from typing import Annotated, Optional
import typer



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



@app.command()
def push(directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """🚀 Push changes across repositories."""
    from machineconfig.scripts.python.repos_helper import git_operations
    git_operations(directory, pull=False, commit=False, push=True, recursive=recursive, no_sync=no_sync)
@app.command()
def pull(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """⬇️ Pull changes across repositories."""
    from machineconfig.scripts.python.repos_helper import git_operations
    git_operations(directory, pull=True, commit=False, push=False, recursive=recursive, no_sync=no_sync)
@app.command()
def commit(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """💾 Commit changes across repositories."""
    from machineconfig.scripts.python.repos_helper import git_operations
    git_operations(directory, pull=False, commit=True, push=False, recursive=recursive, no_sync=no_sync)
@app.command()
def all(
    directory: DirectoryArgument = None,
    recursive: RecursiveOption = False,
    no_sync: NoSyncOption = False,
) -> None:
    """🔄 Pull, commit, and push changes across repositories."""
    from machineconfig.scripts.python.repos_helper import git_operations
    git_operations(directory, pull=True, commit=True, push=True, recursive=recursive, no_sync=no_sync)


@sync_app.command()
def capture(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """📝 Record repositories into a repos.json specification."""
    from machineconfig.scripts.python.repos_helper import print_banner, resolve_directory
    print_banner()
    repos_root = resolve_directory(directory)
    from machineconfig.scripts.python.repos_helper_record import main as record_repos
    save_path = record_repos(repos_root=repos_root)
    from machineconfig.utils.path_extended import PathExtended
    if cloud is not None:
        PathExtended(save_path).to_cloud(rel2home=True, cloud=cloud)
@sync_app.command()
def clone(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """📥 Clone repositories described by a repos.json specification."""
    from machineconfig.scripts.python.repos_helper import print_banner, clone_from_specs
    print_banner()
    clone_from_specs(directory, cloud, checkout_branch_flag=False, checkout_commit_flag=False)


@sync_app.command(name="checkout-to-commit")
def checkout_command(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """🔀 Check out specific commits listed in the specification."""
    from machineconfig.scripts.python.repos_helper import print_banner, clone_from_specs
    print_banner()
    clone_from_specs(directory, cloud, checkout_branch_flag=False, checkout_commit_flag=True)


@sync_app.command(name="checkout-to-branch")
def checkout_to_branch_command(
    directory: DirectoryArgument = None,
    cloud: CloudOption = None,
) -> None:
    """🔀 Check out to the main branch defined in the specification."""
    from machineconfig.scripts.python.repos_helper import print_banner, clone_from_specs
    print_banner()
    clone_from_specs(directory, cloud, checkout_branch_flag=True, checkout_commit_flag=False)


@app.command()
def analyze(
    directory: DirectoryArgument = None,
) -> None:
    """📊 Analyze repository development over time."""
    from machineconfig.scripts.python.repos_helper import print_banner
    print_banner()
    repo_path = directory if directory is not None else "."
    from machineconfig.scripts.python.count_lines_frontend import analyze_repo_development
    analyze_repo_development(repo_path=repo_path)

