"""Repos CLI powered by Typer.

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""

from pathlib import Path
from typing import Annotated, Optional
import typer


app = typer.Typer(help="� Manage development repositories", no_args_is_help=True)
sync_app = typer.Typer(help="� Manage repository specifications and syncing", no_args_is_help=True)
app.add_typer(sync_app, name="sync", help="� Sync repositories using saved specs")


DirectoryArgument = Annotated[Optional[str], typer.Argument(help="📁 Folder containing repos or the specs JSON file to use.")]
RecursiveOption = Annotated[bool, typer.Option("--recursive", "-r", help="🔍 Recurse into nested repositories.")]
NoSyncOption = Annotated[bool, typer.Option("--no-sync", help="🚫 Disable automatic uv sync after pulls.")]
CloudOption = Annotated[Optional[str], typer.Option("--cloud", "-c", help="☁️ Upload to or download from this cloud remote.")]


@app.command(no_args_is_help=True)
def push(directory: DirectoryArgument = None, recursive: RecursiveOption = False, no_sync: NoSyncOption = False) -> None:
    """🚀 Push changes across repositories."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import git_operations

    git_operations(directory, pull=False, commit=False, push=True, recursive=recursive, no_sync=no_sync)


@app.command(no_args_is_help=True)
def pull(directory: DirectoryArgument = None, recursive: RecursiveOption = False, no_sync: NoSyncOption = False) -> None:
    """⬇️ Pull changes across repositories."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import git_operations

    git_operations(directory, pull=True, commit=False, push=False, recursive=recursive, no_sync=no_sync)


@app.command(no_args_is_help=True)
def commit(directory: DirectoryArgument = None, recursive: RecursiveOption = False, no_sync: NoSyncOption = False) -> None:
    """💾 Commit changes across repositories."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import git_operations

    git_operations(directory, pull=False, commit=True, push=False, recursive=recursive, no_sync=no_sync)


@app.command(no_args_is_help=True)
def cleanup(directory: DirectoryArgument = None, recursive: RecursiveOption = False, no_sync: NoSyncOption = False) -> None:
    """🔄 Pull, commit, and push changes across repositories."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import git_operations

    git_operations(directory, pull=True, commit=True, push=True, recursive=recursive, no_sync=no_sync)


@sync_app.command(no_args_is_help=True)
def capture(directory: DirectoryArgument = None, cloud: CloudOption = None) -> None:
    """📝 Record repositories into a repos.json specification."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import resolve_directory
    repos_root = resolve_directory(directory)
    from machineconfig.scripts.python.repos_helpers.repos_helper_record import main as record_repos

    save_path = record_repos(repos_root=repos_root)
    from machineconfig.utils.path_extended import PathExtended

    if cloud is not None:
        PathExtended(save_path).to_cloud(rel2home=True, cloud=cloud)


@sync_app.command(no_args_is_help=True)
def clone(directory: DirectoryArgument = None, cloud: CloudOption = None) -> None:
    """📥 Clone repositories described by a repos.json specification."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import clone_from_specs

    
    clone_from_specs(directory, cloud, checkout_branch_flag=False, checkout_commit_flag=False)


@sync_app.command(name="checkout-to-commit", no_args_is_help=True)
def checkout_command(directory: DirectoryArgument = None, cloud: CloudOption = None) -> None:
    """🔀 Check out specific commits listed in the specification."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import clone_from_specs

    
    clone_from_specs(directory, cloud, checkout_branch_flag=False, checkout_commit_flag=True)


@sync_app.command(name="checkout-to-branch", no_args_is_help=True)
def checkout_to_branch_command(directory: DirectoryArgument = None, cloud: CloudOption = None) -> None:
    """🔀 Check out to the main branch defined in the specification."""
    from machineconfig.scripts.python.repos_helpers.repos_helper import clone_from_specs
    clone_from_specs(directory, cloud, checkout_branch_flag=True, checkout_commit_flag=False)


@app.command(no_args_is_help=True)
def analyze(directory: DirectoryArgument = None) -> None:
    """📊 Analyze repository development over time."""
    repo_path = directory if directory is not None else "."
    from machineconfig.scripts.python.repos_helpers.count_lines_frontend import analyze_repo_development

    analyze_repo_development(repo_path=repo_path)


@app.command(no_args_is_help=True)
def viz(
    repo: str = typer.Option(Path.cwd().__str__(), "--repo", "-r", help="Path to git repository to visualize"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output video file (e.g., output.mp4). If specified, gource will render to video."),
    resolution: str = typer.Option("1920x1080", "--resolution", "-res", help="Video resolution (e.g., 1920x1080, 1280x720)"),
    seconds_per_day: float = typer.Option(0.1, "--seconds-per-day", "-spd", help="Speed of simulation (lower = faster)"),
    auto_skip_seconds: float = typer.Option(1.0, "--auto-skip-seconds", "-as", help="Skip to next entry if nothing happens for X seconds"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Title for the visualization"),
    hide_items: list[str] = typer.Option([], "--hide", "-h", help="Items to hide: bloom, date, dirnames, files, filenames, mouse, progress, root, tree, users, usernames"),
    key_items: bool = typer.Option(False, "--key", "-k", help="Show file extension key"),
    fullscreen: bool = typer.Option(False, "--fullscreen", "-f", help="Run in fullscreen mode"),
    viewport: Optional[str] = typer.Option(None, "--viewport", "-v", help="Camera viewport (e.g., '1000x1000')"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Start date (YYYY-MM-DD)"),
    stop_date: Optional[str] = typer.Option(None, "--stop-date", help="Stop date (YYYY-MM-DD)"),
    user_image_dir: Optional[Path] = typer.Option(None, "--user-image-dir", help="Directory with user avatar images"),
    max_files: int = typer.Option(0, "--max-files", help="Maximum number of files to show (0 = no limit)"),
    max_file_lag: float = typer.Option(5.0, "--max-file-lag", help="Max time files remain on screen after last change"),
    file_idle_time: int = typer.Option(0, "--file-idle-time", help="Time in seconds files remain idle before being removed"),
    framerate: int = typer.Option(60, "--framerate", help="Frames per second for video output"),
    background_color: str = typer.Option("000000", "--background-color", help="Background color in hex (e.g., 000000 for black)"),
    font_size: int = typer.Option(22, "--font-size", help="Font size"),
    camera_mode: str = typer.Option("overview", "--camera-mode", help="Camera mode: overview or track"),
        ) -> None:
    """🎬 Visualize repository activity using Gource."""
    from machineconfig.scripts.python.helpers_repos.grource import visualize
    visualize(repo=repo, output_file=output_file, resolution=resolution, seconds_per_day=seconds_per_day,
              auto_skip_seconds=auto_skip_seconds, title=title, hide_items=hide_items, key_items=key_items,
              fullscreen=fullscreen, viewport=viewport, start_date=start_date, stop_date=stop_date,
              user_image_dir=user_image_dir, max_files=max_files, max_file_lag=max_file_lag,
              file_idle_time=file_idle_time, framerate=framerate, background_color=background_color,
              font_size=font_size, camera_mode=camera_mode)
