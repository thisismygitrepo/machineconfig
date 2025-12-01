


from typing import Optional
from pathlib import Path
from machineconfig.utils.source_of_truth import CONFIG_ROOT, DEFAULTS_PATH

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
def resolve_spec_path(directory: Optional[str], cloud: Optional[str]) -> Path:
    repos_root = resolve_directory(directory)
    from machineconfig.utils.path_extended import PathExtended
    if not repos_root.exists() or repos_root.name != "repos.json":
        relative_repos_root = PathExtended(repos_root).expanduser().absolute().relative_to(Path.home())
        candidate = Path(CONFIG_ROOT).joinpath("repos").joinpath(relative_repos_root).joinpath("repos.json")
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
def clone_from_specs(
    directory: Optional[str],
    cloud: Optional[str],
    *,
    checkout_branch_flag: bool,
    checkout_commit_flag: bool,
) -> None:
    
    typer.echo("\n📥 Cloning or checking out repositories...")
    spec_path = resolve_spec_path(directory, cloud)
    from machineconfig.scripts.python.helpers.helpers_repos.clone import clone_repos
    clone_repos(
        spec_path=spec_path,
        preferred_remote=None,
        checkout_branch_flag=checkout_branch_flag,
        checkout_commit_flag=checkout_commit_flag,
    )