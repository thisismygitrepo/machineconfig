"""shell"""

from pathlib import Path



def get_shell_profile_path() -> Path:
    import platform
    import subprocess
    from rich.console import Console
    from rich.panel import Panel
    system = platform.system()
    console = Console()
    if system == "Windows":
        result = subprocess.run(["pwsh", "-Command", "$PROFILE"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            profile_path = Path(result.stdout.strip())
        else:
            print(f"Command failed with return code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            raise ValueError(f"""Could not get profile path for Windows. Got stdout: {result.stdout}, stderr: {result.stderr}""")
    elif system == "Linux":
        profile_path = Path.home().joinpath(".bashrc")
    elif system == "Darwin":
        profile_path = Path.home().joinpath(".zshrc")
    else:
        raise ValueError(f"""Not implemented for this system {system}""")
    console.print(Panel(f"""🐚 SHELL PROFILE | Working with path: `{profile_path}`""", title="[bold blue]Shell Profile[/bold blue]", border_style="blue"))
    return profile_path


def get_nu_shell_profile_path() -> Path:
    import platform
    from rich.console import Console
    from rich.panel import Panel
    system = platform.system()
    console = Console()
    if system == "Windows":
        profile_path = Path.home().joinpath(r"AppData\Roaming\nushell")
    elif system == "Linux":
        profile_path = Path.home().joinpath(".config/nushell")
    elif system == "Darwin":
        profile_path = Path.home().joinpath("Library/Application Support/nushell")
    else:
        raise ValueError(f"""Not implemented for this system {system}""")
    console.print(Panel(f"""🐚 NU SHELL PROFILE | Working with path: `{profile_path}`""", title="[bold cyan]Nu Shell Profile[/bold cyan]", border_style="cyan"))
    return profile_path


def create_default_shell_profile() -> None:
    shell_profile_path = get_shell_profile_path()
    import platform
    import subprocess
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    from machineconfig.utils.path_extended import PathExtended
    system = platform.system()
    console = Console()
    if not shell_profile_path.exists():
        console.print(Panel(f"""🆕 PROFILE | Profile does not exist at `{shell_profile_path}`. Creating a new one.""", title="[bold blue]Profile[/bold blue]", border_style="blue"))
        shell_profile_path.parent.mkdir(parents=True, exist_ok=True)
        shell_profile_path.write_text("", encoding="utf-8")
    shell_profile = shell_profile_path.read_text(encoding="utf-8")
    from machineconfig.profile.create_helper import copy_assets_to_machine
    copy_assets_to_machine("settings")  # init.ps1 or init.sh live here
    copy_assets_to_machine("scripts")  # init scripts are going to reference those scripts.
    shell_name = ""
    if system == "Windows":
        shell_name = "pwsh"
        init_script = PathExtended(CONFIG_ROOT).joinpath("settings/shells/pwsh/init.ps1")
        source_line = f""". {str(init_script.collapseuser(placeholder="$HOME"))}"""
    elif system == "Linux":
        shell_name = "bash"
        init_script = PathExtended(CONFIG_ROOT).joinpath("settings/shells/bash/init.sh")
        source_line = f"""source {str(init_script.collapseuser(placeholder="$HOME"))}"""
    elif system == "Darwin":
        shell_name = "zsh"
        init_script = PathExtended(CONFIG_ROOT).joinpath("settings/shells/zsh/init.sh")
        source_line = f"""source {str(init_script.collapseuser(placeholder="$HOME"))}"""
    else:
        raise ValueError(f"""Not implemented for this system {system}""")

    was_shell_updated = False
    if source_line in shell_profile:
        console.print(Panel("🔄 PROFILE | Skipping init script sourcing - already present in profile", title="[bold blue]Profile[/bold blue]", border_style="blue"))
    else:
        console.print(Panel("📝 PROFILE | Adding init script sourcing to profile", title="[bold blue]Profile[/bold blue]", border_style="blue"))
        shell_profile += "\n" + source_line + "\n"
        if shell_name == "bash":
            result = subprocess.run(["cat", "/proc/version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0 and result.stdout:
                version_info = result.stdout.lower()
                is_wsl = "microsoft" in version_info or "wsl" in version_info
                if is_wsl:
                    shell_profile += "\ncd $HOME"
                    console.print("📌 WSL detected - adding 'cd $HOME' to profile to avoid Windows filesystem")
                    # Sync shell history between Windows and WSL
                    # https://www.hanselman.com/blog/sharing-powershell-history-between-windows-and-wsl
                    shell_profile += """
# Sync shell history between Windows and WSL
export PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND$'\\n'}history -a; history -c; history -r"
"""
        was_shell_updated = True
    if was_shell_updated:
        shell_profile_path.parent.mkdir(parents=True, exist_ok=True)
        shell_profile_path.write_text(shell_profile, encoding="utf-8")
        console.print(Panel("✅ Profile updated successfully", title="[bold blue]Profile[/bold blue]", border_style="blue"))


def create_nu_shell_profile() -> None:
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    from machineconfig.utils.path_extended import PathExtended
    console = Console()
    nu_profile_path = get_nu_shell_profile_path()
    config_dir = nu_profile_path
    config_file = config_dir.joinpath("config.nu")
    if not config_dir.exists():
        console.print(Panel(f"""🆕 NU SHELL CONFIG | Config directory does not exist at `{config_dir}`. Creating a new one.""", title="[bold cyan]Nu Shell Config[/bold cyan]", border_style="cyan"))
        config_dir.mkdir(parents=True, exist_ok=True)
    if not config_file.exists():
        console.print(Panel(f"""🆕 NU SHELL CONFIG | config.nu file does not exist at `{config_file}`. Creating a new one.""", title="[bold cyan]Nu Shell Config[/bold cyan]", border_style="cyan"))
        config_file.write_text("", encoding="utf-8")
    config_content = config_file.read_text(encoding="utf-8")
    from machineconfig.profile.create_helper import copy_assets_to_machine
    copy_assets_to_machine("settings")
    copy_assets_to_machine("scripts")
    init_script = PathExtended(CONFIG_ROOT).joinpath("settings/shells/nushell/init.nu")
    source_line = f"""use {str(init_script)}"""
    was_config_updated = False
    if source_line in config_content:
        console.print(Panel("🔄 NU SHELL CONFIG | Skipping init script sourcing - already present in config.nu", title="[bold cyan]Nu Shell Config[/bold cyan]", border_style="cyan"))
    else:
        console.print(Panel("📝 NU SHELL CONFIG | Adding init script sourcing to config.nu", title="[bold cyan]Nu Shell Config[/bold cyan]", border_style="cyan"))
        config_content += "\n" + source_line + "\n"
        was_config_updated = True
    if was_config_updated:
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(config_content, encoding="utf-8")
        console.print(Panel("✅ Nu shell config updated successfully", title="[bold cyan]Nu Shell Config[/bold cyan]", border_style="cyan"))


if __name__ == "__main__":
    pass
