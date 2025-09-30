#!/usr/bin/env python3
"""
Interactive Machine Configuration Setup Script

A Python version of the interactive installation script that uses questionary
for better user experience with checkbox selections.


# echo # 📧 Thunderbird Setup Note:
# Run after installing Thunderbird and starting it once:
# cd ~/AppData/Roaming/ThunderBird/Profiles
# $res = ls
# $name = $res[0].Name
# mv $backup_folder $name
#


"""

import sys
from pathlib import Path
from platform import system
from typing import cast

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from machineconfig.utils.code import run_shell_script

_ = cast
console = Console()


def display_header() -> None:
    header_text = Text("MACHINE CONFIGURATION", style="bold magenta")
    subtitle_text = Text("Interactive Installation Script", style="italic cyan")
    console.print(Panel(f"📦 {header_text}\n{subtitle_text}", border_style="blue", padding=(1, 2)))
def display_completion_message() -> None:
    completion_text = Text("INSTALLATION COMPLETE", style="bold green")
    subtitle_text = Text("System setup finished successfully", style="italic green")
    console.print(Panel(f"✨ {completion_text}\n{subtitle_text}\n\n🎉 Your system has been configured successfully!\n🔄 You may need to reboot to apply all changes.", border_style="green", padding=(1, 2)))
def display_dotfiles_instructions() -> None:
    header_text = Text("DOTFILES MIGRATION", style="bold yellow")
    subtitle_text = Text("Configuration transfer options", style="italic yellow")
    instructions = """
🖱️  [bold blue]Method 1: USING MOUSE WITHOUT KB OR BROWSER SHARE[/bold blue]
    On original machine, run:
    [dim]cd ~/dotfiles/creds/msc
    easy-sharing . --password rew --username al[/dim]
    Then open brave on new machine to get MouseWithoutBorders password

🔐 [bold blue]Method 2: USING SSH[/bold blue]
    FROM REMOTE, RUN:
    [dim]fptx ~/dotfiles $USER@$(hostname):^ -z
    # OR, using IP address if router has not yet found the hostname:
    fptx ~/dotfiles $USER@$(hostname -I | awk '{print $1}'):^ -z[/dim]

☁️  [bold blue]Method 3: USING INTERNET SECURE SHARE[/bold blue]
    [dim]cd ~
    cloud_copy SHARE_URL . --config ss[/dim]
    (requires symlinks to be created first)"""
    console.print(Panel(f"📂 {header_text}\n{subtitle_text}\n\n{instructions}", border_style="yellow", padding=(1, 2)))


def get_installation_choices() -> list[str]:
    """Get user choices for installation options."""
    choices = [
        Choice(value="upgrade_system", title="🔄 Upgrade System Packages        - Update all system packages", checked=False),
        Choice(value="ESSENTIAL_SYSTEM", title="📥 Install Apps                    - Install base system applications", checked=False),
        Choice(value="ESSENTIAL", title="⚡ Install CLI Apps               - Command-line tools installation", checked=False),
        Choice(value="DEV_SYSTEM", title="🛠️  Install Development Tools      - rust, libssl-dev, ffmpeg, wezterm, brave, code", checked=False),
        Choice(value="TerminalEyeCandy", title="🎨 Install ASCII Art Libraries    - Terminal visualization tools", checked=False),
        Choice(value="install_repos", title="🐍 Install Repos                - Set up Python environment and repositories permanently.", checked=False),
        Choice(value="install_ssh_server", title="🔒 Install SSH Server             - Set up remote access", checked=False),
        Choice(value="install_shell_profile", title="🐚 Configure Shell Profile         - Source machineconfig shell initialization", checked=False),
        Choice(value="create_symlinks", title="🔗 Create Symlinks                - Set up configuration symlinks (finish dotfiles transfer first)", checked=False),
        Choice(value="retrieve_repositories", title="📚 Retrieve Repositories          - Clone repositories to ~/code", checked=False),
        Choice(value="retrieve_data", title="💾 Retrieve Data                  - Backup restoration", checked=False),
    ]
    # Add Windows-specific options
    if system() == "Windows":
        choices.append(Choice(value="install_windows_desktop", title="💻 Install Windows Desktop Apps   - Brave, Windows Terminal, PowerShell, VSCode (Windows only)", checked=False))
    selected = questionary.checkbox("Select the installation options you want to execute:", choices=choices, show_description=True).ask()
    return selected or []


def execute_installations(selected_options: list[str]) -> None:
    if system() == "Windows":
        from machineconfig import setup_windows as module
        script_path = Path(module.__file__).parent / "ve.ps1"
        run_shell_script(script_path.read_text(encoding="utf-8"))
    else:
        from machineconfig import setup_linux as module
        script_path = Path(module.__file__).parent / "ve.sh"
        run_shell_script(script_path.read_text(encoding="utf-8"))

    for maybe_a_group in selected_options:
        if maybe_a_group in ("ESSENTIAL", "DEV", "ESSENTIAL_SYSTEM", "DEV_SYSTEM", "TerminalEyeCandy"):
            console.print(Panel("⚡ [bold bright_yellow]CLI APPLICATIONS[/bold bright_yellow]\n[italic]Command-line tools installation[/italic]", border_style="bright_yellow"))
            console.print("🔧 Installing CLI applications", style="bold cyan")
            try:
                from machineconfig.utils.installer_utils.installer import main as devops_devapps_install_main
                devops_devapps_install_main(group=maybe_a_group)  # type: ignore
                console.print("✅ CLI applications installed successfully", style="bold green")
            except Exception as e:
                console.print(f"❌ Error installing CLI applications: {e}", style="bold red")
            run_shell_script(". $HOME/.bashrc")

    if "upgrade_system" in selected_options:
        if system() == "Windows":
            console.print("❌ System upgrade is not applicable on Windows via this script.", style="bold red")
        elif system() == "Linux":
            console.print(Panel("🔄 [bold magenta]SYSTEM UPDATE[/bold magenta]\n[italic]Package management[/italic]", border_style="magenta"))
            run_shell_script("sudo nala upgrade -y")
        else:
            console.print(f"❌ System upgrade not supported on {system()}.", style="bold red")
    if "install_repos" in selected_options:
        console.print(Panel("🐍 [bold green]PYTHON ENVIRONMENT[/bold green]\n[italic]Virtual environment setup[/italic]", border_style="green"))
        if system() == "Windows":
            from machineconfig import setup_windows as module
            script_path = Path(module.__file__).parent / "repos.ps1"
        else:
            from machineconfig import setup_linux as module
            script_path = Path(module.__file__).parent / "repos.sh"
        run_shell_script(script_path.read_text(encoding="utf-8"))

    if "install_ssh_server" in selected_options:
        console.print(Panel("🔒 [bold red]SSH SERVER[/bold red]\n[italic]Remote access setup[/italic]", border_style="red"))
        if system() == "Windows":
            powershell_script = """Write-Host "🔧 Installing and configuring SSH server..."
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'"""
            run_shell_script(f'powershell -Command "{powershell_script}"')
        else:
            run_shell_script("sudo nala install openssh-server -y")

    if "install_shell_profile" in selected_options:
        console.print(Panel("🐚 [bold green]SHELL PROFILE[/bold green]\n[italic]Shell configuration setup[/italic]", border_style="green"))
        console.print("🔧 Configuring shell profile", style="bold cyan")
        try:
            from machineconfig.profile.create import main_profile

            main_profile()
            console.print("✅ Shell profile configured successfully", style="bold green")
        except Exception as e:
            console.print(f"❌ Error configuring shell profile: {e}", style="bold red")

    if "create_symlinks" in selected_options:
        display_dotfiles_instructions()
        dotfiles_ready = questionary.confirm("📂 Have you finished copying dotfiles?", default=True).ask()
        if dotfiles_ready:
            console.print(Panel("🔗 [bold cyan]SYMLINK CREATION[/bold cyan]\n[italic]Configuration setup[/italic]", border_style="cyan"))
            console.print("🔧 Creating symlinks", style="bold cyan")
            try:
                from machineconfig.profile.create import main_symlinks
                main_symlinks()
                console.print("✅ Symlinks created successfully", style="bold green")
            except Exception as e:
                console.print(f"❌ Error creating symlinks: {e}", style="bold red")
            run_shell_script("sudo chmod 600 $HOME/.ssh/*")
            run_shell_script("sudo chmod 700 $HOME/.ssh")
        else:
            console.print("⏭️  Skipping symlink creation - finish dotfiles transfer first", style="yellow")

    if "retrieve_repositories" in selected_options:
        console.print(Panel("📚 [bold bright_magenta]REPOSITORIES[/bold bright_magenta]\n[italic]Project code retrieval[/italic]", border_style="bright_magenta"))
        from machineconfig.scripts.python import repos
        repos.clone(directory=str(Path.home() / "code"), cloud="odg1")

    if "retrieve_data" in selected_options:
        console.print(Panel("💾 [bold bright_cyan]DATA RETRIEVAL[/bold bright_cyan]\n[italic]Backup restoration[/italic]", border_style="bright_cyan"))
        console.print("🔧 Retrieving backup data", style="bold cyan")
        try:
            from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
            main_backup_retrieve(direction="RETRIEVE")
            console.print("✅ Backup data retrieved successfully", style="bold green")
        except Exception as e:
            console.print(f"❌ Error retrieving backup data: {e}", style="bold red")

    if "install_windows_desktop" in selected_options:
        from machineconfig.jobs.installer.custom_dev.nerfont_windows_helper import install_nerd_fonts
        install_nerd_fonts()
        from machineconfig.setup_windows.wt_and_pwsh.set_wt_settings import main as set_wt_settings_main
        set_wt_settings_main()


def main() -> None:
    """Main function to run the interactive installation."""
    display_header()
    selected_options = get_installation_choices()
    if not selected_options:
        console.print("❌ No options selected. Exiting...", style="bold red")
        sys.exit(0)
    console.print(f"\n✅ Selected options: {'\n'.join(selected_options)}", style="bold green")
    proceed = questionary.confirm("🚀 Proceed with installation?", default=True).ask()
    if not proceed:
        console.print("❌ Installation cancelled.", style="bold red")
        sys.exit(0)
    execute_installations(selected_options)
    display_completion_message()


if __name__ == "__main__":
    pass
