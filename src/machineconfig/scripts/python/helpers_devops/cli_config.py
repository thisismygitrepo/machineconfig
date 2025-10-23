

from typing import Literal, Annotated, Optional
from pathlib import Path
import typer



def private(method: Annotated[Literal["symlink", "copy"], typer.Option(..., "--method", "-m", help="Method to use for linking files")],
                             on_conflict: Annotated[Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"], typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throwError",
                             which: Annotated[Optional[str], typer.Option(..., "--which", "-w", help="Specific items to process")] = None,
                             interactive: Annotated[bool, typer.Option(..., "--interactive", "-ia", help="Run in interactive mode")] = False):
    """🔗 Manage private configuration files."""
    import machineconfig.profile.create_links_export as create_links_export
    create_links_export.main_private_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

def public(method: Annotated[Literal["symlink", "copy"], typer.Option(..., "--method", "-m", help="Method to use for setting up the config file.")],
                            on_conflict: Annotated[Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"], typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throwError",
                            which: Annotated[Optional[str], typer.Option(..., "--which", "-w", help="Specific items to process")] = None,
                            interactive: Annotated[bool, typer.Option(..., "--interactive", "-ia", help="Run in interactive mode")] = False):
    """🔗 Manage public configuration files."""
    import machineconfig.profile.create_links_export as create_links_export
    create_links_export.main_public_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

def dotfile(file: Annotated[str, typer.Argument(help="file/folder path.")],
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite.")] = False,
    dest: Annotated[str, typer.Option("--dest", "-d", help="destination folder")] = "",
    ):
    """🔗 Manage dotfiles."""
    import machineconfig.scripts.python.helpers_devops.cli_config_dotfile as dotfile_module
    dotfile_module.main(file=file, overwrite=overwrite, dest=dest)


def shell():
    """🔗 Configure your shell profile."""
    from machineconfig.profile.create_shell_profile import create_default_shell_profile
    create_default_shell_profile()


def path():
    """📚 NAVIGATE PATH variable with TUI"""
    from machineconfig.scripts.python import env_manager as navigator
    from pathlib import Path
    path = Path(navigator.__file__).resolve().parent.joinpath("path_manager_tui.py")
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script
    uv_with = ["textual"]
    uv_project_dir = None
    if not Path.home().joinpath("code/machineconfig").exists():
        uv_with.append("machineconfig>=6.81")
    else:
        uv_project_dir = str(Path.home().joinpath("code/machineconfig"))
    run_shell_script(get_uv_command_executing_python_script(python_script=path.read_text(encoding="utf-8"), uv_with=uv_with, uv_project_dir=uv_project_dir)[0])


def pwsh_theme():
    """🔗 Select powershell prompt theme."""
    import machineconfig.scripts.python.helpers_devops.themes as themes
    file = Path(themes.__file__).parent / "choose_pwsh_theme.ps1"
    import subprocess
    subprocess.run(["pwsh", "-File", str(file)])

def starship_theme():
    """🔗 Select starship prompt theme."""
    import subprocess
    from machineconfig.utils.code import run_shell_script
    
    presets: list[str] = ["catppuccin-powerline", "pastel-powerline", "tokyo-night", "gruvbox-rainbow", "jetpack"]
    config_path: Path = Path.home() / ".config" / "starship.toml"
    
    typer.echo("\n🚀 Starship Theme Selector\n")
    for idx, preset in enumerate(presets, start=1):
        typer.echo(f"{idx}. {preset}")
    
    choice: str = typer.prompt("Select a preset")
    
    try:
        choice_idx: int = int(choice)
        if 1 <= choice_idx <= len(presets):
            selected_preset: str = presets[choice_idx - 1]
            typer.echo(f"\n✨ Applying {selected_preset}...")
            run_shell_script(f"""starship preset {selected_preset} -o {config_path}""")
            typer.echo("\n📋 Preview:")
            subprocess.run(["starship", "module", "all"], check=False)
            typer.echo(f"\n✅ {selected_preset} applied!")
        else:
            typer.echo("❌ Invalid selection")
    except ValueError:
        typer.echo("❌ Please enter a valid number")

def copy_assets(which: Annotated[Literal["scripts", "settings", "both"], typer.Argument(..., help="Which assets to copy")]):
    """🔗 Copy asset files from library to machine."""
    import machineconfig.profile.create_helper as create_helper
    match which:
        case "both":
            create_helper.copy_assets_to_machine(which="scripts")
            create_helper.copy_assets_to_machine(which="settings")
        case _:
            create_helper.copy_assets_to_machine(which=which)


def get_app():
    config_apps = typer.Typer(help="⚙️ [c] configuration subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    config_apps.command("private", no_args_is_help=True, help="🔗  [v] Manage private configuration files.")(private)
    config_apps.command("v", no_args_is_help=True, hidden=True)(private)
    config_apps.command("public", no_args_is_help=True, help="🔗  [b] Manage public configuration files.")(public)
    config_apps.command("b", no_args_is_help=True, help="Manage public configuration files.", hidden=True)(public)
    config_apps.command("dotfile", no_args_is_help=True, help="🔗  [d] Manage dotfiles.")(dotfile)
    config_apps.command("d", no_args_is_help=True,  hidden=True)(dotfile)
    config_apps.command("shell", no_args_is_help=False, help="🔗  [s] Configure your shell profile.")(shell)
    config_apps.command("s", no_args_is_help=False, help="Configure your shell profile.", hidden=True)(shell)
    config_apps.command("path", no_args_is_help=False, help="📚  [p] NAVIGATE PATH variable with TUI")(path)
    config_apps.command("p", no_args_is_help=False, help="NAVIGATE PATH variable with TUI", hidden=True)(path)
    config_apps.command("starship-theme", no_args_is_help=False, help="🔗  [t] Select starship prompt theme.")(starship_theme)
    config_apps.command("t", no_args_is_help=False, help="Select starship prompt theme.", hidden=True)(starship_theme)
    config_apps.command("pwsh-theme", no_args_is_help=False, help="🔗  [T] Select powershell prompt theme.")(pwsh_theme)
    config_apps.command("T", no_args_is_help=False, help="Select powershell prompt theme.", hidden=True)(pwsh_theme)

    config_apps.command("copy-assets", no_args_is_help=True, help="🔗  [c] Copy asset files from library to machine.", hidden=False)(copy_assets)
    config_apps.command("c", no_args_is_help=True, help="Copy asset files from library to machine.", hidden=True)(copy_assets)
    return config_apps
