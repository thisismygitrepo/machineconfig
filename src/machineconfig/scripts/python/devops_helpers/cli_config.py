

from typing import Literal, Annotated, Optional
from pathlib import Path
import typer

config_apps = typer.Typer(help="⚙️ Configuration subcommands", no_args_is_help=True)


@config_apps.command(no_args_is_help=True)
def private(method: Literal["symlink", "copy"] = typer.Option(..., "--method", "-m", help="Method to use for linking files"),
                             on_conflict: Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option("throwError", "--on-conflict", "-o", help="Action to take on conflict"),
                             which: Optional[str] = typer.Option(None, "--which", "-w", help="Specific items to process"),
                             interactive: bool = typer.Option(False, "--interactive", "-ia", help="Run in interactive mode")):
    """🔗 Manage private configuration files."""
    import machineconfig.profile.create_links_export as create_links_export
    create_links_export.main_private_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

@config_apps.command(no_args_is_help=True)
def public(method: Literal["symlink", "copy"] = typer.Option(..., "--method", "-m", help="Method to use for setting up the config file."),
                            on_conflict: Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option("throwError", "--on-conflict", "-o", help="Action to take on conflict"),
                            which: Optional[str] = typer.Option(None, "--which", "-w", help="Specific items to process"),
                            interactive: bool = typer.Option(False, "--interactive", "-ia", help="Run in interactive mode")):
    """🔗 Manage public configuration files."""
    import machineconfig.profile.create_links_export as create_links_export
    create_links_export.main_public_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

@config_apps.command(no_args_is_help=True)
def dotfile(file: Annotated[str, typer.Argument(help="file/folder path.")],
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite.")] = False,
    dest: Annotated[str, typer.Option("--dest", "-d", help="destination folder")] = "",
    ):
    """🔗 Manage dotfiles."""
    import machineconfig.scripts.python.devops_helpers.cli_config_dotfile as dotfile_module
    dotfile_module.main(file=file, overwrite=overwrite, dest=dest)


@config_apps.command(no_args_is_help=False)
def shell():
    """🔗 Configure your shell profile."""
    from machineconfig.profile.create_shell_profile import create_default_shell_profile
    create_default_shell_profile()


@config_apps.command(no_args_is_help=False)
def pwsh_theme():
    """🔗 Select powershell prompt theme."""
    import machineconfig.scripts.python.devops_helpers.themes as themes
    file = Path(themes.__file__).parent / "choose_pwsh_theme.ps1"
    import subprocess
    subprocess.run(["pwsh", "-File", str(file)])

@config_apps.command(no_args_is_help=False)
def copy_assets(which: Literal["scripts", "settings", "both"] = typer.Option(..., "--which", "-w", help="Which assets to copy")):
    """🔗 Copy asset files from library to machine."""
    import machineconfig.profile.create_helper as create_helper
    if which == "both":
        create_helper.copy_assets_to_machine(which="scripts")
        create_helper.copy_assets_to_machine(which="settings")
    else:
        create_helper.copy_assets_to_machine(which=which)
