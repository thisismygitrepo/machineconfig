"""devops with emojis"""

import machineconfig.scripts.python.share_terminal as share_terminal
import machineconfig.scripts.python.repos as repos
from machineconfig.jobs.installer.package_groups import PACKAGE_GROUPS
# import machineconfig.scripts.python.dotfile as dotfile_module
import typer
from typing import Literal, Annotated, Optional, get_args


app = typer.Typer(help="🛠️ DevOps operations", no_args_is_help=True)
@app.command(no_args_is_help=True)
def install(    which: Optional[str] = typer.Option(None, "--which", "-w", help="Comma-separated list of program names to install."),
    group: Optional[PACKAGE_GROUPS] = typer.Option(None, "--group", "-g", help=f"Group name (one of {list(get_args(PACKAGE_GROUPS))})"),
    interactive: bool = typer.Option(False, "--interactive", "-ia", help="Interactive selection of programs to install."),
) -> None:
    """📦 Install essential packages"""
    import machineconfig.utils.installer_utils.installer as installer_entry_point
    installer_entry_point.main(which=which, group=group, interactive=interactive)


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
@self_app.command()
def clone():
    """📋 CLONE machienconfig locally for faster execution and nightly updates. """
    import platform
    from machineconfig.utils.code import run_shell_script
    if platform.system() == "Windows":
        from machineconfig.setup_windows import REPOS
    else:
        from machineconfig.setup_linux import REPOS
    run_shell_script(REPOS.read_text(encoding="utf-8"))


@config_apps.command(no_args_is_help=True)
def private(method: Literal["symlink", "copy"] = typer.Option(..., help="Method to use for linking files"),
                             on_conflict: Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option("throwError", help="Action to take on conflict"),
                             which: Optional[str] = typer.Option(None, help="Specific items to process"),
                             interactive: bool = typer.Option(False, help="Run in interactive mode")):
    """🔗 Manage private configuration files."""
    import machineconfig.profile.create_frontend as create_frontend
    create_frontend.main_private_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

@config_apps.command(no_args_is_help=True)
def public(method: Literal["symlink", "copy"] = typer.Option(..., help="Method to use for setting up the config file."),
                            on_conflict: Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option(..., help="Action to take on conflict"),
                            which: Optional[str] = typer.Option(None, help="Specific items to process"),
                            interactive: bool = typer.Option(False, help="Run in interactive mode")):
    """🔗 Manage public configuration files."""
    import machineconfig.profile.create_frontend as create_frontend
    create_frontend.main_public_from_parser(method=method, on_conflict=on_conflict, which=which, interactive=interactive)

# @config_apps.command(no_args_is_help=True)
# def dotfile():
#     """🔗 Manage dotfiles."""
#     dotfile_module.main()


@config_apps.command(no_args_is_help=True)
def shell(method: Annotated[Literal["copy", "reference"], typer.Argument(help="Choose the method to configure the shell profile: 'copy' copies the init script directly, 'reference' references machineconfig for dynamic updates.")]):
    """🔗 Configure your shell profile."""
    from machineconfig.profile.shell import create_default_shell_profile
    create_default_shell_profile(method=method)


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
    import platform
    if platform.system() == "Windows":
        from machineconfig.setup_windows import SSH_SERVER
        program = SSH_SERVER.read_text(encoding="utf-8")
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        from machineconfig.setup_linux import SSH_SERVER
        program = SSH_SERVER.read_text(encoding="utf-8")
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(program=program)


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
