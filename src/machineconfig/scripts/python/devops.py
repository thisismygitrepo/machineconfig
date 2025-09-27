"""devops with emojis"""

from machineconfig.scripts.python.share_terminal import main as share_terminal_main
import machineconfig.scripts.python.devops_devapps_install as installer_entry_point

from platform import system
from rich.console import Console
from rich.panel import Panel
import typer

console = Console()
app = typer.Typer(help="🛠️ DevOps operations with emojis", no_args_is_help=True)


BOX_WIDTH = 150  # width for box drawing


@app.command()
def update():
    """🔄 UPDATE essential repos"""
    console.print(Panel("🔄 Updating essential repositories...", width=BOX_WIDTH, border_style="blue"))
    import machineconfig.scripts.python.devops_update_repos as helper
    helper.main()


app.command(name="install", help="📦 Install essential packages")(installer_entry_point.main)
app.command(name="share-terminal", help="📡 Share terminal via web browser")(share_terminal_main)



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

@app.command("ia")
def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.interactive import main
    main()


if __name__ == "__main__":
    pass
