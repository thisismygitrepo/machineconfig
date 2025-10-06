

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
    import machineconfig.profile.create_frontend as create_frontend
    create_frontend.main_private_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

@config_apps.command(no_args_is_help=True)
def public(method: Literal["symlink", "copy"] = typer.Option(..., "--method", "-m", help="Method to use for setting up the config file."),
                            on_conflict: Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option("throwError", "--on-conflict", "-o", help="Action to take on conflict"),
                            which: Optional[str] = typer.Option(None, "--which", "-w", help="Specific items to process"),
                            interactive: bool = typer.Option(False, "--interactive", "-ia", help="Run in interactive mode")):
    """🔗 Manage public configuration files."""
    import machineconfig.profile.create_frontend as create_frontend
    create_frontend.main_public_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

@config_apps.command(no_args_is_help=True)
def dotfile(file: Annotated[str, typer.Argument(help="file/folder path.")],
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite.")] = False,
    dest: Annotated[str, typer.Option("--dest", "-d", help="destination folder")] = "",
    ):
    """🔗 Manage dotfiles."""
    import machineconfig.scripts.python.devops_helpers.cli_config_dotfile as dotfile_module
    dotfile_module.main(file=file, overwrite=overwrite, dest=dest)


@config_apps.command(no_args_is_help=True)
def shell(method: Annotated[Literal["copy", "reference"], typer.Argument(help="Choose the method to configure the shell profile: 'copy' copies the init script directly, 'reference' references machineconfig for dynamic updates.")]):
    """🔗 Configure your shell profile."""
    from machineconfig.profile.shell import create_default_shell_profile
    create_default_shell_profile(method=method)


@config_apps.command(no_args_is_help=False)
def pwsh_theme():
    """🔗 Configure your shell profile."""
    import machineconfig.scripts.python.devops_helpers.themes as themes
    file = Path(themes.__file__).parent / "choose_pwsh_theme.ps1"
    import subprocess
    # subprocess.run(["pwsh", "-File", str(file)])
    subprocess.run(["pwsh", "-File", str(file)])
