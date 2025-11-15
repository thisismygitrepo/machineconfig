

from typing import Literal, Annotated
from pathlib import Path
import typer
import machineconfig.scripts.python.helpers_devops.cli_config_dotfile as dotfile_module
import machineconfig.profile.create_links_export as create_links_export


def configure_shell_profile(which: Annotated[Literal["default", "d", "nushell", "n"], typer.Option(..., "--which", "-w", help="Which shell profile to create/configure")]="default"):
    """🔗 Configure your shell profile."""
    from machineconfig.profile.create_shell_profile import create_default_shell_profile,  create_nu_shell_profile
    match which:
        case "nushell" | "n":
            create_nu_shell_profile()
            return
        case "default" | "d":
            create_default_shell_profile()
            return
    typer.echo(f"[red]Error:[/] Unknown shell profile type: {which}")



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


def copy_assets(which: Annotated[Literal["scripts", "s", "settings", "t", "both", "b"], typer.Argument(..., help="Which assets to copy")]):
    """🔗 Copy asset files from library to machine."""
    import machineconfig.profile.create_helper as create_helper
    match which:
        case "both" | "b":
            create_helper.copy_assets_to_machine(which="scripts")
            create_helper.copy_assets_to_machine(which="settings")
            return
        case "scripts" | "s":
            create_helper.copy_assets_to_machine(which="scripts")
            return
        case "settings" | "t":
            create_helper.copy_assets_to_machine(which="settings")
            return
    typer.echo(f"[red]Error:[/] Unknown asset type: {which}")


def link_wsl_and_windows_home():
    """🔗 Link WSL home and Windows home directories."""
    import machineconfig.utils.ssh_utils.wsl as wsl_utils
    wsl_utils.link_wsl_and_windows()


def get_app():
    config_apps = typer.Typer(help="⚙️ [c] configuration subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    config_apps.command("private", no_args_is_help=True, help="🔗 [v] Manage private configuration files.")(create_links_export.main_private_from_parser)
    config_apps.command("v", no_args_is_help=True, hidden=True)(create_links_export.main_private_from_parser)
    config_apps.command("public", no_args_is_help=True, help="🔗 [b] Manage public configuration files.")(create_links_export.main_public_from_parser)
    config_apps.command("b", no_args_is_help=True, help="Manage public configuration files.", hidden=True)(create_links_export.main_public_from_parser)
    config_apps.command("dotfile", no_args_is_help=True, help="🔗 [d] Manage dotfiles.")(dotfile_module.main)
    config_apps.command("d", no_args_is_help=True,  hidden=True)(dotfile_module.main)
    config_apps.command("shell", no_args_is_help=False, help="🔗 [s] Configure your shell profile.")(configure_shell_profile)
    config_apps.command("s", no_args_is_help=False, help="Configure your shell profile.", hidden=True)(configure_shell_profile)
    config_apps.command("starship-theme", no_args_is_help=False, help="🔗 [t] Select starship prompt theme.")(starship_theme)
    config_apps.command("t", no_args_is_help=False, help="Select starship prompt theme.", hidden=True)(starship_theme)
    config_apps.command("pwsh-theme", no_args_is_help=False, help="🔗 [T] Select powershell prompt theme.")(pwsh_theme)
    config_apps.command("T", no_args_is_help=False, help="Select powershell prompt theme.", hidden=True)(pwsh_theme)

    config_apps.command("copy-assets", no_args_is_help=True, help="🔗 [c] Copy asset files from library to machine.", hidden=False)(copy_assets)
    config_apps.command("c", no_args_is_help=True, help="Copy asset files from library to machine.", hidden=True)(copy_assets)

    config_apps.command("link-wsl-windows", no_args_is_help=False, help="🔗 [l] Link WSL home and Windows home directories.", hidden=False)(link_wsl_and_windows_home)
    config_apps.command("l", no_args_is_help=False, help="Link WSL home and Windows home directories.", hidden=True)(link_wsl_and_windows_home)

    return config_apps
