
import typer
from typing import Optional, Literal, Annotated
from pathlib import Path


def main(
    cloud: Annotated[Optional[str], typer.Option(..., "--cloud", "-c", help="Cloud storage profile name. If not provided, uses default from config.")] = None,
    repo: Annotated[Optional[str], typer.Option(..., "--repo", "-r", help="Path to the local repository. Defaults to cwd.")] = Path.cwd().as_posix(),
    message: Annotated[Optional[str], typer.Option(..., "--message", "-m", help="Commit message for local changes.")] = None,
    on_conflict: Annotated[Literal["ask", "push-local-merge", "overwrite-local", "stop-on-conflict", "remove-rclone-conflict"], typer.Option(..., "--on-conflict", "-oc", help="Action to take on merge conflict. Default is 'ask'.")] = "ask",
    pwd: Annotated[Optional[str], typer.Option(..., "--password", help="Password for encryption/decryption of the remote repository.")] = None,
):
    from machineconfig.scripts.python.helpers_repos.cloud_repo_sync import main as program_content
    program_content(cloud=cloud, repo=repo, message=message, on_conflict=on_conflict, pwd=pwd)
