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


"""

import sys
from pathlib import Path
import platform
import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from machineconfig.utils.code import run_shell_script

console = Console()


def display_header() -> None:
    from machineconfig.utils.installer_utils.installer_runner import get_machineconfig_version
    from rich.align import Align

    # Fancy ASCII art header
    ascii_art = """
    ╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                             ║
    ║   ███╗   ███╗ █████╗  ██████╗██╗  ██╗██╗███╗   ██╗███████╗ ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗    ║
    ║   ████╗ ████║██╔══██╗██╔════╝██║  ██║██║████╗  ██║██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝    ║
    ║   ██╔████╔██║███████║██║     ███████║██║██╔██╗ ██║█████╗  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗   ║
    ║   ██║╚██╔╝██║██╔══██║██║     ██╔══██║██║██║╚██╗██║██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║   ║
    ║   ██║ ╚═╝ ██║██║  ██║╚██████╗██║  ██║██║██║ ╚████║███████╗╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝   ║
    ║   ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝    ║
    ║                                                                                                             ║
    ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
    """

    version = get_machineconfig_version()
    title = f"✨ MACHINE CONFIGURATION v{version} ✨"
    subtitle = "🎯 Your digital life manager. Dotfiles, data, code and more."
    bug_report = "🐛 Please report bugs to Alex Al-Saffar @ https://github.com/thisismygitrepo/machineconfig"

    # Print ASCII art
    console.print(Text(ascii_art, style="bold cyan"))
    console.print()
    
    # Print centered text elements
    console.print(Align.center(Text(title, style="bold bright_magenta")))
    console.print(Align.center(Text(subtitle, style="italic bright_blue")))
    console.print()
    console.print(Align.center(Text(bug_report, style="dim white")))
    console.print()
def display_completion_message() -> None:
    completion_text = Text("INSTALLATION COMPLETE", style="bold green")
    subtitle_text = Text("System setup finished successfully", style="italic green")
    console.print(Panel(f"✨ {completion_text}\n{subtitle_text}\n\n🎉 Your system has been configured successfully!\n🔄 You may need to reboot to apply all changes.", border_style="green", padding=(1, 2)))
def display_dotfiles_instructions() -> None:
    header_text = Text("DOTFILES MIGRATION", style="bold yellow")
    subtitle_text = Text("Configuration transfer options", style="italic yellow")
    instructions = """
    On remote, run:
    rm ~/dotfiles.zip || true
    ouch c ~/dotfiles dotfiles.zip --password rew
    # INSECURE OVER INTERNET: uvx wormhole-magic send ~/dotfiles.zip
    # LOCAL NETWORK:
    devops network share-server --no-auth ./dotfiles.zip
    On new machine, run:
    # INSECURE cd $HOME; uvx wormhole-magic receive dotfiles.zip --accept-file
    cd $HOME;
    rm ~/dotfiles.zip || true
    utils download $URL
    ouch d ~/dotfiles.zip

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
    cloud copy SHARE_URL . --config ss[/dim]
    (requires symlinks to be created first)
    """
    console.print(Panel(f"📂 {header_text}\n{subtitle_text}\n\n{instructions}", border_style="yellow", padding=(1, 2)))


def get_installation_choices() -> list[str]:
    """Get user choices for installation options."""
    choices = [
        Choice(value="install_machineconfig", title="🐍 Install machineconfig cli.", checked=False),
        Choice(value="sysabc", title="📥 Install System Package Manager (Needed for other apps to be installed).", checked=False),
        Choice(value="termabc", title="⚡ Install Terminal CLI apps essentials (group `termabc`)", checked=False),
        Choice(value="install_shell_profile", title="🐚 Configure Shell Profile And Map Other Configs.", checked=False),
        Choice(value="install_ssh_server", title="🔒 [ADVANCED] Configure SSH Server", checked=False),
        Choice(value="retrieve_repositories", title="📚 [ADVANCED] Retrieve Repositories", checked=False),
        Choice(value="retrieve_data", title="💾 [ADVANCED] Retrieve Data.", checked=False),
    ]
    selected = questionary.checkbox("Select the installation options you want to execute:", choices=choices, show_description=True).ask()
    return selected or []


def execute_installations(selected_options: list[str]) -> None:
    for maybe_a_group in selected_options:
        if maybe_a_group in ("termabc", "sysabc"):
            console.print(Panel("⚡ [bold bright_yellow]CLI APPLICATIONS[/bold bright_yellow]\n[italic]Command-line tools installation[/italic]", border_style="bright_yellow"))
            console.print("🔧 Installing CLI applications", style="bold cyan")
            try:
                from machineconfig.utils.installer_utils.installer_cli import main_installer_cli as devops_devapps_install_main
                devops_devapps_install_main(group=True, which=maybe_a_group, interactive=False)
                console.print("✅ CLI applications installed successfully", style="bold green")
            except Exception as e:
                console.print(f"❌ Error installing CLI applications: {e}", style="bold red")
            if platform.system() != "Windows":
                run_shell_script(". $HOME/.bashrc")

    if "install_machineconfig" in selected_options:
        console.print(Panel("🐍 [bold green]PYTHON ENVIRONMENT[/bold green]\n[italic]Virtual environment setup[/italic]", border_style="green"))
        from machineconfig.scripts.python.helpers.helpers_devops.cli_self import install
        install(copy_assets=True, dev=False)

    if "install_ssh_server" in selected_options:
        console.print(Panel("🔒 [bold red]SSH SERVER[/bold red]\n[italic]Remote access setup[/italic]", border_style="red"))
        if platform.system() == "Windows":
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
            from machineconfig.profile.create_shell_profile import create_default_shell_profile
            create_default_shell_profile()
            console.print("✅ Shell profile configured successfully", style="bold green")
            from machineconfig.profile.create_links_export import main_public_from_parser
            main_public_from_parser(method="copy", on_conflict="overwrite-default-path", which="all", interactive=False)
            if platform.system() == "Windows":
                from machineconfig.jobs.installer.python_scripts.nerfont_windows_helper import install_nerd_fonts
                install_nerd_fonts()
                from machineconfig.settings.wt.set_wt_settings import main as set_wt_settings_main
                set_wt_settings_main()
        except Exception as e:
            console.print(f"❌ Error configuring shell profile: {e}", style="bold red")

    if "retrieve_repositories" in selected_options:
        console.print(Panel("📚 [bold bright_magenta]REPOSITORIES[/bold bright_magenta]\n[italic]Project code retrieval[/italic]", border_style="bright_magenta"))
        from machineconfig.scripts.python.helpers.helpers_devops import cli_repos
        cli_repos.clone(directory=str(Path.home() / "code"), cloud=None)

    if "retrieve_data" in selected_options:
        console.print(Panel("💾 [bold bright_cyan]DATA RETRIEVAL[/bold bright_cyan]\n[italic]Backup restoration[/italic]", border_style="bright_cyan"))
        console.print("🔧 Retrieving backup data", style="bold cyan")
        try:
            from machineconfig.scripts.python.helpers.helpers_devops.devops_backup_retrieve import main_backup_retrieve
            main_backup_retrieve(direction="RETRIEVE", cloud=None, which=None)
            console.print("✅ Backup data retrieved successfully", style="bold green")
        except Exception as e:
            console.print(f"❌ Error retrieving backup data: {e}", style="bold red")


def main() -> None:
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
    execute_installations(selected_options=selected_options)
    display_completion_message()
    from machineconfig.utils.code import exit_then_run_shell_script
    if platform.system() == "Windows":
        reload_init_script = "pwsh $PROFILE"
    elif platform.system() == "Darwin":
        reload_init_script = "source $HOME/.zshrc"
    elif platform.system() == "Linux":
        reload_init_script = "source $HOME/.bashrc"
    else:
        reload_init_script = ""
    exit_then_run_shell_script(reload_init_script)



if __name__ == "__main__":
    pass
