"""devops with emojis"""

from machineconfig.utils.options import choose_from_options

from platform import system
from typing import Optional, Literal, TypeAlias
from rich.console import Console
from rich.panel import Panel
import typer

console = Console()
app = typer.Typer(help="🛠️ DevOps operations with emojis", invoke_without_command=True, no_args_is_help=True)

BOX_WIDTH = 150  # width for box drawing


COMMANDS: TypeAlias = Literal["🔄 UPDATE essential repos", "⚙️ DEVAPPS install", "🔗 SYMLINKS, SHELL PROFILE, FONT, TERMINAL SETTINGS.", "🆕 SYMLINKS new", "🔑 SSH add pub key to this machine", "🗝️ SSH add identity (private key) to this machine", "🔐 SSH use key pair to connect two machines", "📡 SSH setup", "🐧 SSH setup wsl", "💾 BACKUP", "📥 RETRIEVE", "⏰ SCHEDULER"]

options_list = list(COMMANDS.__args__)


@app.command()
def update():
    """🔄 UPDATE essential repos"""
    console.print(Panel("🔄 Updating essential repositories...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.scripts.python.devops_update_repos as helper
    helper.main()


@app.command()
def install():
    """⚙️ DEVAPPS install"""
    console.print(Panel("⚙️  Installing development applications...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.scripts.python.devops_devapps_install as helper
    helper.main(which=None)


@app.command()
def symlinks():
    """🔗 SYMLINKS of dotfiles."""
    console.print(Panel("🔗 Setting up symlinks, PATH, and shell profile...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.profile.create as helper
    helper.main_symlinks()


@app.command()
def profile():
    """🔗 Update shell profile."""
    console.print(Panel("🔗 Setting up symlinks, PATH, and shell profile...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.profile.create as helper
    helper.main_profile()


@app.command()
def symlinks_new():
    """🆕 SYMLINKS new"""
    console.print(Panel("🔄 Creating new symlinks...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.jobs.python.python_ve_symlink as helper
    helper.main()


@app.command()
def ssh_add_key():
    """🔑 SSH add pub key to this machine"""
    console.print(Panel("🔑 Adding public SSH key to this machine...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.scripts.python.devops_add_ssh_key as helper
    helper.main()


@app.command()
def ssh_add_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    console.print(Panel("🗝️  Adding SSH identity (private key) to this machine...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.scripts.python.devops_add_identity as helper
    helper.main()


@app.command()
def ssh_connect():
    """🔐 SSH use key pair to connect two machines"""
    console.print(Panel("❌ ERROR: Not Implemented\nSSH key pair connection feature is not yet implemented", title_align="left", border_style="red", width=BOX_WIDTH))
    raise NotImplementedError


@app.command()
def ssh_setup():
    """📡 SSH setup"""
    console.print(Panel("📡 Setting up SSH...", width=BOX_WIDTH, border_style="blue"))
    _program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
    _program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
    import subprocess
    subprocess.run(_program_linux if system() == "Linux" else _program_windows, shell=True, check=True)


@app.command()
def ssh_setup_wsl():
    """🐧 SSH setup wsl"""
    console.print(Panel("🐧 Setting up SSH for WSL...", width=BOX_WIDTH, border_style="blue"))
    import subprocess
    subprocess.run("curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash", shell=True, check=True)


@app.command()
def backup():
    """💾 BACKUP"""
    console.print(Panel("💾 Creating backup...", width=BOX_WIDTH, border_style="blue"))
    from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="BACKUP")


@app.command()
def retrieve():
    """📥 RETRIEVE"""
    console.print(Panel("📥 Retrieving backup...", width=BOX_WIDTH, border_style="blue"))
    from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="RETRIEVE")


@app.command()
def scheduler():
    """⏰ SCHEDULER"""
    console.print(Panel("⏰ Setting up scheduler...", width=BOX_WIDTH, border_style="blue"))
    # from machineconfig.scripts.python.scheduler import main as helper
    # helper()


def args_parser():
    app()


@app.command()
def interactive(which: Optional[COMMANDS] = None):
    """🛠️ Interactive menu mode (legacy)"""
    console.print(Panel("🚀 Initializing DevOps operation...", width=BOX_WIDTH, border_style="blue"))
    options = options_list
    if which is None:
        try:
            choice_key = choose_from_options(msg="", options=options, header="🛠️ DEVOPS", default=options[0], multi=False, fzf=False)
        except KeyboardInterrupt:
            console.print(Panel("❌ Operation cancelled by user", title_align="left", border_style="red", width=BOX_WIDTH))
            return
    else:
        choice_key = which

    console.print(Panel(f"🔧 SELECTED OPERATION\n{choice_key}", title_align="left", border_style="green", width=BOX_WIDTH))

    if choice_key == "🔄 UPDATE essential repos":
        update()
    elif choice_key == "⚙️ DEVAPPS install":
        install()
    elif choice_key == "🆕 SYMLINKS new":
        symlinks_new()
    elif choice_key == "🔗 SYMLINKS, SHELL PROFILE, FONT, TERMINAL SETTINGS.":
        symlinks()
    elif choice_key == "🔑 SSH add pub key to this machine":
        ssh_add_key()
    elif choice_key == "🔐 SSH use key pair to connect two machines":
        ssh_connect()
    elif choice_key == "🗝️ SSH add identity (private key) to this machine":
        ssh_add_identity()
    elif choice_key == "📡 SSH setup":
        ssh_setup()
    elif choice_key == "🐧 SSH setup wsl":
        ssh_setup_wsl()
    elif choice_key == "💾 BACKUP":
        backup()
    elif choice_key == "📥 RETRIEVE":
        retrieve()
    elif choice_key == "⏰ SCHEDULER":
        scheduler()
    else:
        console.print(Panel("❌ ERROR: Invalid choice", title_align="left", border_style="red", width=BOX_WIDTH))
        raise ValueError(f"Unimplemented choice: {choice_key}")


if __name__ == "__main__":
    args_parser()
