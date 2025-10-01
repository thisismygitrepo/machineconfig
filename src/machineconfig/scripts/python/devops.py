"""devops with emojis"""

import machineconfig.utils.installer_utils.installer as installer_entry_point
import machineconfig.scripts.python.share_terminal as share_terminal
import machineconfig.scripts.python.repos as repos

import machineconfig.profile.creator_frontend as creator_frontend
from machineconfig.scripts.python import dotfile

from machineconfig.utils.installer import get_machineconfig_version
import typer


app = typer.Typer(help=f"🛠️ DevOps operations @ machineconfig {get_machineconfig_version()}", no_args_is_help=True)
app.command(name="install", help="📦 Install essential packages")(installer_entry_point.main)
app.add_typer(repos.app, name="repos", help="📁 Manage git repositories")


config_apps = typer.Typer(help="⚙️ Configuration subcommands", no_args_is_help=True)
app.add_typer(config_apps, name="config")



app_data = typer.Typer(help="💾 Data subcommands", no_args_is_help=True)
app.add_typer(app_data, name="data")

nw_apps = typer.Typer(help="🔐 Network subcommands", no_args_is_help=True)
nw_apps.command(name="share-terminal", help="📡 Share terminal via web browser")(share_terminal.main)
app.add_typer(nw_apps, name="network")


self_app = typer.Typer(help="🔄 SELF operations subcommands", no_args_is_help=True)
app.add_typer(self_app, name="self")


@self_app.command()
def update():
    """🔄 UPDATE essential repos"""
    import machineconfig.scripts.python.devops_update_repos as helper
    helper.main()
@self_app.command()
def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.interactive import main
    main()
@self_app.command()
def status():
    """📊 STATUS of machine, shell profile, apps, symlinks, dotfiles, etc."""
    pass


config_apps.command(name="private", help="🔗 Manage private configuration files.")(creator_frontend.mail_private_from_parser)
config_apps.command(name="public", help="🔗 Manage public configuration files.")(creator_frontend.mail_public_from_parser)
config_apps.command(name="dotfile", help="🔗 Manage dotfiles.")(dotfile.main)


@config_apps.command()
def shell():
    """🔗 Configure your shell profile."""
    import machineconfig.profile.create as helper
    helper.main_profile()


@nw_apps.command()
def add_key():
    """🔑 SSH add pub key to this machine"""
    import machineconfig.scripts.python.devops_add_ssh_key as helper
    helper.main()
@nw_apps.command()
def add_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    import machineconfig.scripts.python.devops_add_identity as helper
    helper.main()
@nw_apps.command()
def connect():
    """🔐 SSH use key pair to connect two machines"""
    raise NotImplementedError
@nw_apps.command()
def setup():
    """📡 SSH setup"""
    _program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
    _program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
    import subprocess
    from platform import system
    subprocess.run(_program_linux if system() == "Linux" else _program_windows, shell=True, check=True)
@nw_apps.command()
def setup_wsl():
    """🐧 SSH setup wsl"""
    import subprocess
    subprocess.run("curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash", shell=True, check=True)


@app_data.command()
def backup():
    """💾 BACKUP"""
    from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="BACKUP")


@app_data.command()
def retrieve():
    """📥 RETRIEVE"""
    from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="RETRIEVE")


# @app.command()
# def scheduler():
#     """⏰ SCHEDULER"""
#     # from machineconfig.scripts.python.scheduler import main as helper
#     # helper()



# @app.command()
# def scheduler():
#     """⏰ SCHEDULER"""
#     # from machineconfig.scripts.python.scheduler import main as helper
#     # helper()


if __name__ == "__main__":
    pass


if __name__ == "__main__":
    pass
