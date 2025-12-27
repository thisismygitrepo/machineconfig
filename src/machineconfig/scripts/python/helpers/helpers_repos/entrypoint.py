


from typing import Optional
from pathlib import Path
import typer


def resolve_directory(directory: Optional[str]) -> Path:
    if directory is None:
        directory = Path.cwd().as_posix()
        typer.echo(f"📁 Using directory: {directory}")
    return Path(directory).expanduser().absolute()


def git_operations(
    directory: Optional[str],
    *,
    pull: bool,
    commit: bool,
    push: bool,
    recursive: bool,
    auto_uv_sync: bool,
) -> None:
    
    repos_root = resolve_directory(directory)
    from machineconfig.scripts.python.helpers.helpers_repos.action import perform_git_operations
    from machineconfig.utils.path_extended import PathExtended
    perform_git_operations(
        repos_root=PathExtended(repos_root),
        pull=pull,
        commit=commit,
        push=push,
        recursive=recursive,
        auto_uv_sync=auto_uv_sync,
    )


def clone_from_specs(
    directory: Optional[str],
    *,
    checkout_branch_flag: bool,
    checkout_commit_flag: bool,
) -> None:
    
    typer.echo("\n📥 Cloning or checking out repositories...")
    # spec_path = resolve_spec_path(directory, cloud)
    # /home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/helpers_devops/cli_config_dotfile.py
    dir_obj = resolve_directory(directory)
    spec_path_default = dir_obj.joinpath("repos.json")
    from machineconfig.scripts.python.helpers.helpers_devops.cli_config_dotfile import get_backup_path
    spec_path_self_managed = get_backup_path(
        orig_path=spec_path_default,
        sensitivity="v",
        destination=None,
        shared=False,
    )

    from machineconfig.scripts.python.helpers.helpers_repos.clone import clone_repos
    clone_repos(
        spec_path=spec_path_self_managed,
        preferred_remote=None,
        checkout_branch_flag=checkout_branch_flag,
        checkout_commit_flag=checkout_commit_flag,
    )
