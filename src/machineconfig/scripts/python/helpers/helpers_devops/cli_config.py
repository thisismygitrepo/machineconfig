

from typing import Literal, Annotated
from pathlib import Path
import typer
import machineconfig.scripts.python.helpers.helpers_devops.cli_config_dotfile as dotfile_module
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
    import machineconfig.scripts.python.helpers.helpers_devops.themes as themes
    file = Path(themes.__file__).parent / "choose_pwsh_theme.ps1"
    import subprocess
    subprocess.run(["pwsh", "-File", str(file)])


def starship_theme():
    """🔗 Select starship prompt theme."""
    import subprocess
    import shutil
    import os
    from machineconfig.utils.code import run_shell_script
    
    # Presets with descriptions
    presets = {
        "nerd-font-symbols": "Changes the symbols for each module to use Nerd Font symbols.",
        "no-nerd-font": "Changes the symbols so that no Nerd Font symbols are used.",
        "bracketed-segments": "Changes the format to show segments in brackets.",
        "plain-text-symbols": "Changes the symbols for each module into plain text.",
        "no-runtime-versions": "Hides the version of language runtimes.",
        "no-empty-icons": "Does not show icons if the toolset is not found.",
        "pure-preset": "Emulates the look and behavior of Pure.",
        "pastel-powerline": "Inspired by M365Princess.",
        "tokyo-night": "Inspired by tokyo-night-vscode-theme.",
        "gruvbox-rainbow": "Inspired by Pastel Powerline and Tokyo Night.",
        "jetpack": "Pseudo minimalist preset inspired by geometry and spaceship.",
    }

    # Check if fzf is available
    fzf_path = shutil.which("fzf")
    
    if fzf_path:
        # Prepare input for fzf
        fzf_input = "\n".join([f"{name}\t{desc}" for name, desc in presets.items()])
        
        # Preview command
        preview_config = "/tmp/starship_preview.toml"
        # Use STARSHIP_SHELL=fish to get raw ANSI codes without bash/zsh specific escaping
        preview_cmd = f"starship preset {{1}} > {preview_config} && STARSHIP_CONFIG={preview_config} STARSHIP_SHELL=fish starship prompt"
        
        # Run fzf
        try:
            process = subprocess.Popen(
                ["fzf", "--ansi", "--delimiter", "\t", "--with-nth", "1,2", "--preview", preview_cmd, "--preview-window", "bottom:30%"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            stdout, _ = process.communicate(input=fzf_input)
            
            if process.returncode == 0 and stdout.strip():
                selected_line = stdout.strip()
                selected_preset = selected_line.split("\t")[0]
            else:
                typer.echo("No selection made.")
                return
        except Exception as e:
            typer.echo(f"Error running fzf: {e}")
            return
            
    else:
        # Fallback to simple menu if fzf is not installed
        typer.echo("\n🚀 Starship Theme Selector (Install 'fzf' for interactive preview)\n")
        preset_list = list(presets.keys())
        for idx, preset in enumerate(preset_list, start=1):
            typer.echo(f"{idx}. {preset}: {presets[preset]}")
        
        choice = typer.prompt("Select a preset")
        try:
            choice_idx = int(choice)
            if 1 <= choice_idx <= len(preset_list):
                selected_preset = preset_list[choice_idx - 1]
            else:
                typer.echo("❌ Invalid selection")
                return
        except ValueError:
            typer.echo("❌ Please enter a valid number")
            return

    # Apply selection
    config_path = Path.home() / ".config" / "starship.toml"
    typer.echo(f"\n✨ Applying {selected_preset}...")
    run_shell_script(f"starship preset {selected_preset} -o {config_path}")
    typer.echo(f"\n✅ {selected_preset} applied!")
    
    # Show final preview
    typer.echo("\n📋 Current Prompt Preview:")
    # Use fish shell to avoid bash/zsh specific escaping in the output
    subprocess.run(["starship", "prompt"], env={**os.environ, "STARSHIP_SHELL": "fish"}, check=False)


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



def get_app():
    config_apps = typer.Typer(help="⚙️ [c] configuration subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)
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


    return config_apps
