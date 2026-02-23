

from typing import Literal, Annotated
from pathlib import Path
import typer
import machineconfig.scripts.python.helpers.helpers_devops.cli_config_dotfile as dotfile_module
import machineconfig.profile.create_links_export as create_links_export
from machineconfig.utils.ve import read_default_cloud_config


def dump_config(which: Annotated[Literal["ve"], typer.Option(..., "--which", "-w", help="Which config to dump")]):
    """🔗 Dump example configuration files."""
    match which:
        case "ve":
            _dump_ve_config()
            return
    msg = typer.style("Error: ", fg=typer.colors.RED) + f"Unknown config type: {which}"
    typer.echo(msg)


def _dump_ve_config():
    """Generate .ve.example.yaml with all options, sections, comments and default values."""
    cloud_defaults = read_default_cloud_config()
    def to_yaml_value(value: str | bool | None) -> str:
        """Convert Python values to YAML-compatible strings."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        return f'"{value}"'
    yaml_content = f"""# Virtual Environment Configuration File
# This file configures the virtual environment and cloud sync settings for this project
specs:
  ve_path: ".venv"  # Path to the virtual environment directory (e.g., /home/user/projects/myproject/.venv or ~/venvs/myproject)
  ipy_profile: null  # IPython profile name to use when launching IPython (e.g., myprofile creates/uses ~/.ipython/profile_myprofile)
cloud:
  cloud: {to_yaml_value(cloud_defaults["cloud"])}  # Cloud storage identifier/name
  root: {to_yaml_value(cloud_defaults["root"])}  # Root directory within the cloud storage
  rel2home: {to_yaml_value(cloud_defaults["rel2home"])}  # Whether paths are relative to home directory
  pwd: {to_yaml_value(cloud_defaults["pwd"])}  # Password for encryption (leave empty for no password)
  key: {to_yaml_value(cloud_defaults["key"])}  # Encryption key path (leave empty for no key-based encryption)
  encrypt: {to_yaml_value(cloud_defaults["encrypt"])}  # Enable encryption for cloud sync
  os_specific: {to_yaml_value(cloud_defaults["os_specific"])}  # Use OS-specific paths/configuration
  zip: {to_yaml_value(cloud_defaults["zip"])}  # Compress files before uploading
  share: {to_yaml_value(cloud_defaults["share"])}  # Enable sharing/public access
  overwrite: {to_yaml_value(cloud_defaults["overwrite"])}  # Overwrite existing files during sync
""" 
    output_path = Path.cwd() / ".ve.example.yaml"
    output_path.write_text(yaml_content, encoding="utf-8")   
    msg = typer.style("✅ Success: ", fg=typer.colors.GREEN) + f"Created {output_path}"
    typer.echo(msg)


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
    msg = typer.style("Error: ", fg=typer.colors.RED) + f"Unknown shell profile type: {which}"
    typer.echo(msg)



def pwsh_theme():
    """🔗 Select powershell prompt theme."""
    import machineconfig.scripts.python.helpers.helpers_devops.themes as themes
    file_path = themes.__file__
    # if file_path is None:
    #     typer.echo("❌ ERROR: Could not locate themes module file.", err=True)
    #     raise typer.Exit(code=1)
    file = Path(file_path).parent / "choose_pwsh_theme.ps1"
    # import subprocess
    # subprocess.run(["pwsh", "-File", str(file)])
    from machineconfig.utils.code import exit_then_run_shell_file
    exit_then_run_shell_file(script_path=str(file), strict=False)


def starship_theme():
    """🔗 Select starship prompt theme."""
    import subprocess
    import platform
    import os    
    current_dir = Path(__file__).parent.joinpath("themes")
    
    if platform.system() == "Windows":
        script_path = current_dir / "choose_starship_theme.ps1"
        try:
            subprocess.run(["pwsh", "-File", str(script_path)], check=True)
        except FileNotFoundError:
             # Fallback to powershell if pwsh is not available
            subprocess.run(["powershell", "-File", str(script_path)], check=True)
    else:
        script_path = current_dir / "choose_starship_theme.sh"
        # Ensure executable
        os.chmod(script_path, 0o755)
        subprocess.run(["bash", str(script_path)], check=True)


def configure_wezterm_theme() -> None:
    """🔗 Select WezTerm theme with interactive live preview."""
    import machineconfig.scripts.python.helpers.helpers_devops.themes.choose_wezterm_theme as choose_wezterm_theme
    choose_wezterm_theme.main()


def configure_ghostty_theme() -> None:
    """🔗 Select Ghostty theme with interactive preview."""
    import os
    import platform
    import subprocess

    ghostty_config_path = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "ghostty" / "config"
    auto_theme_include = "config-file = ?auto/theme.ghostty"

    existing_lines = ghostty_config_path.read_text(encoding="utf-8").splitlines() if ghostty_config_path.exists() else []
    existing_lines_stripped = [line.strip() for line in existing_lines]
    if auto_theme_include not in existing_lines_stripped:
        ghostty_config_path.parent.mkdir(parents=True, exist_ok=True)
        if existing_lines and existing_lines[-1].strip():
            existing_lines.append("")
        existing_lines.append(auto_theme_include)
        ghostty_config_path.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")

    reload_hint = "cmd+shift+," if platform.system() == "Darwin" else "ctrl+shift+,"
    typer.echo("🎨 Opening Ghostty interactive theme preview. Use arrows/j/k to browse, Enter then w to save.")
    typer.echo(f"💡 After saving, reload Ghostty config with {reload_hint} to apply.")
    subprocess.run(["ghostty", "+list-themes"], check=True)


def configure_windows_terminal_theme() -> None:
    """🔗 Select Windows Terminal color scheme with interactive live preview."""
    import platform
    import subprocess

    if platform.system().lower() != "windows":
        typer.echo("Error: Windows Terminal theme selection is only supported on Windows systems.", err=True)
        raise typer.Exit(code=1)
    script_path = Path(__file__).parent.joinpath("themes", "choose_windows_terminal_theme.ps1")
    try:
        subprocess.run(["pwsh", "-File", str(script_path)], check=True)
    except FileNotFoundError:
        subprocess.run(["powershell", "-File", str(script_path)], check=True)


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
    msg = typer.style("Error: ", fg=typer.colors.RED) + f"Unknown asset type: {which}"
    typer.echo(msg)


def list_devices() -> None:
    """🔗 List available mountable devices."""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_config_mount as mount_module
    mount_module.list_devices()


def mount_device(
    device_query: Annotated[str | None, typer.Option("--device", "-d", help="Device query (path, key, or label).")] = None,
    mount_point: Annotated[str | None, typer.Option("--mount-point", "-p", help="Mount point (use '-' for default on macOS).")] = None,
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Pick device and mount point interactively.")] = False,
) -> None:
    """🔗 Mount a device to a mount point."""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_config_mount as mount_module
    if interactive:
        mount_module.mount_interactive()
        return
    if device_query is None or mount_point is None:
        msg = typer.style("Error: ", fg=typer.colors.RED) + "--device and --mount-point are required unless --interactive is set"
        typer.echo(msg)
        raise typer.Exit(2)
    mount_module.mount_device(device_query=device_query, mount_point=mount_point)


def get_app():
    config_apps = typer.Typer(help="⚙️ <c> configuration subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)
    config_apps.command("sync", no_args_is_help=True, help="🔗 <s> Sync dotfiles.")(create_links_export.main_from_parser)
    config_apps.command("s", no_args_is_help=True, help="Sync dotfiles.", hidden=True)(create_links_export.main_from_parser)

    config_apps.command("register", no_args_is_help=True, help="🔗 <r> Register dotfiles agains user mapper.toml")(dotfile_module.register_dotfile)
    config_apps.command("r", no_args_is_help=True,  hidden=True)(dotfile_module.register_dotfile)

    config_apps.command("export-dotfiles", no_args_is_help=True, help="🔗 <e> Export dotfiles for migration to new machine.")(dotfile_module.export_dotfiles)
    config_apps.command("e", no_args_is_help=True, help="Export dotfiles for migration to new machine.", hidden=True)(dotfile_module.export_dotfiles)
    config_apps.command("import-dotfiles", no_args_is_help=False, help="🔗 <i> Import dotfiles from exported archive.")(dotfile_module.import_dotfiles)
    config_apps.command("i", no_args_is_help=False, help="Import dotfiles from exported archive.", hidden=True)(dotfile_module.import_dotfiles)

    config_apps.command("shell", no_args_is_help=False, help="🔗 <S> Configure your shell profile.")(configure_shell_profile)
    config_apps.command("S", no_args_is_help=False, help="Configure your shell profile.", hidden=True)(configure_shell_profile)
    config_apps.command("starship-theme", no_args_is_help=False, help="🔗 <t> Select starship prompt theme.")(starship_theme)
    config_apps.command("t", no_args_is_help=False, help="Select starship prompt theme.", hidden=True)(starship_theme)
    config_apps.command("pwsh-theme", no_args_is_help=False, help="🔗 <T> Select powershell prompt theme.")(pwsh_theme)
    config_apps.command("T", no_args_is_help=False, help="Select powershell prompt theme.", hidden=True)(pwsh_theme)
    config_apps.command("wezterm-theme", no_args_is_help=False, help="🔗 <W> Select WezTerm terminal theme.")(configure_wezterm_theme)
    config_apps.command("W", no_args_is_help=False, help="Select WezTerm terminal theme.", hidden=True)(configure_wezterm_theme)
    config_apps.command("ghostty-theme", no_args_is_help=False, help="🔗 <g> Select Ghostty terminal theme.")(configure_ghostty_theme)
    config_apps.command("g", no_args_is_help=False, help="Select Ghostty terminal theme.", hidden=True)(configure_ghostty_theme)
    config_apps.command("windows-terminal-theme", no_args_is_help=False, help="🔗 <x> Select Windows Terminal color scheme.")(configure_windows_terminal_theme)
    config_apps.command("x", no_args_is_help=False, help="Select Windows Terminal color scheme.", hidden=True)(configure_windows_terminal_theme)
    config_apps.command("wt-theme", no_args_is_help=False, help="Select Windows Terminal color scheme.", hidden=True)(configure_windows_terminal_theme)

    config_apps.command("copy-assets", no_args_is_help=True, help="🔗 <c> Copy asset files from library to machine.", hidden=False)(copy_assets)
    config_apps.command("c", no_args_is_help=True, help="Copy asset files from library to machine.", hidden=True)(copy_assets)

    config_apps.command("dump", no_args_is_help=True, help="🔗 <d> Dump example configuration files.")(dump_config)
    config_apps.command("d", no_args_is_help=True, help="Dump example configuration files.", hidden=True)(dump_config)

    config_apps.command("list-devices", no_args_is_help=False, help="🔗 <l> List available devices for mounting.")(list_devices)
    config_apps.command("l", no_args_is_help=False, help="List available devices for mounting.", hidden=True)(list_devices)
    config_apps.command("mount", no_args_is_help=True, help="🔗 <m> Mount a device to a mount point.")(mount_device)
    config_apps.command("m", no_args_is_help=True, help="Mount a device to a mount point.", hidden=True)(mount_device)


    return config_apps
