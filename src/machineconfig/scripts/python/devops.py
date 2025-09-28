"""devops with emojis"""

import machineconfig.scripts.python.fire_agents as fire_agents
import machineconfig.scripts.python.fire_jobs_layout_helper as fire_jobs_layout_helper
import machineconfig.scripts.python.devops_devapps_install as installer_entry_point
import machineconfig.scripts.python.share_terminal as share_terminal
import machineconfig.scripts.python.repos as repos

import typer

app = typer.Typer(help="🛠️ DevOps operations with emojis", no_args_is_help=True)


agents_app = typer.Typer(help="🤖 AI Agents management subcommands")
agents_app.command("create")(fire_agents.create)
agents_app.command("collect")(fire_agents.collect)
app.add_typer(agents_app, name="agents")

layouts_app = typer.Typer(help="Layouts management subcommands")
layouts_app.command("launch")(fire_jobs_layout_helper.launch)
layouts_app.command("load-balance")(fire_jobs_layout_helper.load_balance)
app.add_typer(layouts_app, name="session")

app.command(name="install", help="📦 Install essential packages")(installer_entry_point.main)
app.command(name="share-terminal", help="📡 Share terminal via web browser")(share_terminal.main)
app.command(name="repos", help="📁 Manage git repositories")(repos.main)

ssh_app = typer.Typer(help="🔐 SSH operations subcommands", no_args_is_help=True)
app.add_typer(ssh_app, name="ssh")


@app.command()
def update():
    """🔄 UPDATE essential repos"""
    import machineconfig.scripts.python.devops_update_repos as helper
    helper.main()


@app.command()
def symlinks():
    """🔗 SYMLINKS of dotfiles."""
    import machineconfig.profile.create as helper
    helper.main_symlinks()


@app.command()
def profile():
    """🔗 Update shell profile."""
    import machineconfig.profile.create as helper
    helper.main_profile()


@app.command()
def symlinks_new():
    """🆕 SYMLINKS new"""
    import machineconfig.jobs.python.python_ve_symlink as helper
    helper.main()


@ssh_app.command()
def add_key():
    """🔑 SSH add pub key to this machine"""
    import machineconfig.scripts.python.devops_add_ssh_key as helper
    helper.main()
@ssh_app.command()
def add_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    import machineconfig.scripts.python.devops_add_identity as helper
    helper.main()
@ssh_app.command()
def connect():
    """🔐 SSH use key pair to connect two machines"""
    raise NotImplementedError
@ssh_app.command()
def setup():
    """📡 SSH setup"""
    _program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
    _program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
    import subprocess
    from platform import system
    subprocess.run(_program_linux if system() == "Linux" else _program_windows, shell=True, check=True)
@ssh_app.command()
def setup_wsl():
    """🐧 SSH setup wsl"""
    import subprocess
    subprocess.run("curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash", shell=True, check=True)


@app.command()
def backup():
    """💾 BACKUP"""
    from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="BACKUP")


@app.command()
def retrieve():
    """📥 RETRIEVE"""
    from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="RETRIEVE")


@app.command()
def scheduler():
    """⏰ SCHEDULER"""
    # from machineconfig.scripts.python.scheduler import main as helper
    # helper()

@app.command()
def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.interactive import main
    main()



if __name__ == "__main__":
    pass
