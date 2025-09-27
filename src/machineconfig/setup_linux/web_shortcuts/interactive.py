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

import subprocess
import sys

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


console = Console()


def run_command(command: str, description: str) -> bool:
    """Execute a shell command and return success status."""
    console.print(f"\n🔧 {description}", style="bold cyan")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Error executing command: {e}", style="bold red")
        return False


def display_header() -> None:
    """Display the script header."""
    header_text = Text("MACHINE CONFIGURATION", style="bold magenta")
    subtitle_text = Text("Interactive Installation Script", style="italic cyan")
    console.print(Panel(
        f"📦 {header_text}\n{subtitle_text}",
        border_style="blue",
        padding=(1, 2)
    ))


def display_completion_message() -> None:
    """Display completion message."""
    completion_text = Text("INSTALLATION COMPLETE", style="bold green")
    subtitle_text = Text("System setup finished successfully", style="italic green")
    console.print(Panel(
        f"✨ {completion_text}\n{subtitle_text}\n\n🎉 Your system has been configured successfully!\n🔄 You may need to reboot to apply all changes.",
        border_style="green",
        padding=(1, 2)
    ))


def display_dotfiles_instructions() -> None:
    """Display instructions for dotfiles migration."""
    header_text = Text("DOTFILES MIGRATION", style="bold yellow")
    subtitle_text = Text("Configuration transfer options", style="italic yellow")
    
    instructions = """🖱️  [bold blue]Method 1: USING MOUSE WITHOUT KB OR BROWSER SHARE[/bold blue]
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
    
    console.print(Panel(
        f"📂 {header_text}\n{subtitle_text}\n\n{instructions}",
        border_style="yellow",
        padding=(1, 2)
    ))


def get_installation_choices() -> list[str]:
    """Get user choices for installation options."""
    choices = [
        Choice(value="install_apps",          title="📥 Install Apps                    - Install base system applications", checked=False),
        Choice(value="upgrade_system",        title="🔄 Upgrade System Packages        - Update all system packages", checked=False),
        Choice(value="install_uv_repos",      title="🐍 Install UV and Repos           - Set up Python environment and repositories", checked=False),
        Choice(value="install_ssh_server",    title="🔒 Install SSH Server             - Set up remote access", checked=False),
        Choice(value="create_symlinks",       title="🔗 Create Symlinks                - Set up configuration symlinks (finish dotfiles transfer first)", checked=False),
        Choice(value="install_cli_apps",      title="⚡ Install CLI Apps               - Command-line tools installation", checked=False),
        Choice(value="install_dev_tools",     title="🛠️  Install Development Tools      - rust, libssl-dev, ffmpeg, wezterm, brave, code", checked=False),
        Choice(value="retrieve_repositories", title="📚 Retrieve Repositories          - Clone repositories to ~/code", checked=False),
        Choice(value="retrieve_data",         title="💾 Retrieve Data                  - Backup restoration", checked=False),
        Choice(value="install_ascii_art",     title="🎨 Install ASCII Art Libraries    - Terminal visualization tools", checked=False),
    ]
    
    selected = questionary.checkbox(
        "Select the installation options you want to execute:",
        choices=choices,
        show_description=True,
    ).ask()
    
    return selected or []


def execute_installations(selected_options: list[str]) -> None:
    """Execute the selected installation options."""
    # Always start with VE setup
    console.print(Panel(
        "🐍 [bold green]PYTHON ENVIRONMENT[/bold green]\n[italic]Setting up base virtual environment[/italic]",
        border_style="green"
    ))
    run_command(
        "curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash",
        "Setting up base virtual environment"
    )
    
    if "install_apps" in selected_options:
        console.print(Panel(
            "📦 [bold blue]APPLICATIONS[/bold blue]\n[italic]Installing base system applications[/italic]",
            border_style="blue"
        ))
        run_command(
            "curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash",
            "Installing base system applications"
        )
    
    if "upgrade_system" in selected_options:
        console.print(Panel(
            "🔄 [bold magenta]SYSTEM UPDATE[/bold magenta]\n[italic]Package management[/italic]",
            border_style="magenta"
        ))
        run_command("sudo nala upgrade -y", "Upgrading system packages")
    
    if "install_uv_repos" in selected_options:
        console.print(Panel(
            "🐍 [bold green]PYTHON ENVIRONMENT[/bold green]\n[italic]Virtual environment setup[/italic]",
            border_style="green"
        ))
        run_command(
            "curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash",
            "Setting up Python environment and repositories"
        )
    
    if "install_ssh_server" in selected_options:
        console.print(Panel(
            "🔒 [bold red]SSH SERVER[/bold red]\n[italic]Remote access setup[/italic]",
            border_style="red"
        ))
        run_command("sudo nala install openssh-server -y", "Installing SSH server")
    
    # Always display dotfiles instructions if symlinks are selected
    if "create_symlinks" in selected_options:
        display_dotfiles_instructions()
        
        dotfiles_ready = questionary.confirm(
            "📂 Have you finished copying dotfiles?", 
            default=True
        ).ask()
        
        if dotfiles_ready:
            console.print(Panel(
                "🔗 [bold cyan]SYMLINK CREATION[/bold cyan]\n[italic]Configuration setup[/italic]",
                border_style="cyan"
            ))
            run_command(
                "uv run --python 3.13 --with machineconfig python -m fire machineconfig.profile.create main_symlinks --choice=all",
                "Creating symlinks"
            )
            run_command("sudo chmod 600 $HOME/.ssh/*", "Setting SSH key permissions")
            run_command("sudo chmod 700 $HOME/.ssh", "Setting SSH directory permissions")
        else:
            console.print("⏭️  Skipping symlink creation - finish dotfiles transfer first", style="yellow")
    
    if "install_cli_apps" in selected_options:
        console.print(Panel(
            "⚡ [bold bright_yellow]CLI APPLICATIONS[/bold bright_yellow]\n[italic]Command-line tools installation[/italic]",
            border_style="bright_yellow"
        ))
        run_command(
            "uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_devapps_install main --which=essentials",
            "Installing CLI applications"
        )
        run_command(". $HOME/.bashrc", "Reloading bash configuration")
    
    if "install_dev_tools" in selected_options:
        console.print(Panel(
            "🛠️  [bold bright_blue]DEVELOPMENT TOOLS[/bold bright_blue]\n[italic]Software development packages[/italic]",
            border_style="bright_blue"
        ))
        run_command(
            "(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true",
            "Installing Rust toolchain"
        )
        run_command("sudo nala install libssl-dev -y", "Installing libssl-dev")
        run_command("sudo nala install ffmpeg -y", "Installing ffmpeg")
        run_command(
            "uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_devapps_install main --which=wezterm,brave,code",
            "Installing development applications"
        )
    
    if "retrieve_repositories" in selected_options:
        console.print(Panel(
            "📚 [bold bright_magenta]REPOSITORIES[/bold bright_magenta]\n[italic]Project code retrieval[/italic]",
            border_style="bright_magenta"
        ))
        run_command("repos ~/code --clone --cloud odg1", "Cloning repositories")
    
    if "retrieve_data" in selected_options:
        console.print(Panel(
            "💾 [bold bright_cyan]DATA RETRIEVAL[/bold bright_cyan]\n[italic]Backup restoration[/italic]",
            border_style="bright_cyan"
        ))
        run_command(
            "uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_backup_retrieve main --direction=RETRIEVE",
            "Retrieving backup data"
        )
    
    if "install_ascii_art" in selected_options:
        console.print(Panel(
            "🎨 [bold bright_green]ASCII ART[/bold bright_green]\n[italic]Terminal visualization tools[/italic]",
            border_style="bright_green"
        ))
        run_command("curl bit.ly/cfgasciiartlinux -L | sudo bash", "Installing ASCII art libraries")


def main() -> None:
    """Main function to run the interactive installation."""
    display_header()
    
    # Get user selections
    selected_options = get_installation_choices()
    
    if not selected_options:
        console.print("❌ No options selected. Exiting...", style="bold red")
        sys.exit(0)
    
    console.print(f"\n✅ Selected options: {', '.join(selected_options)}", style="bold green")
    
    # Confirm before proceeding
    proceed = questionary.confirm("🚀 Proceed with installation?", default=True).ask()
    
    if not proceed:
        console.print("❌ Installation cancelled.", style="bold red")
        sys.exit(0)
    
    # Execute installations
    execute_installations(selected_options)
    
    display_completion_message()


if __name__ == "__main__":
    main()