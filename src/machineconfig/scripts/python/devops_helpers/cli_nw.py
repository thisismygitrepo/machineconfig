
import machineconfig.scripts.python.devops_helpers.cli_terminal as cli_terminal
import typer
nw_apps = typer.Typer(help="🔐 Network subcommands", no_args_is_help=True)


nw_apps.command(name="share-terminal", help="📡 Share terminal via web browser")(cli_terminal.main)


@nw_apps.command()
def add_key():
    """🔑 SSH add pub key to this machine"""
    import machineconfig.scripts.python.devops_helpers.devops_add_ssh_key as helper
    helper.main()
@nw_apps.command()
def add_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    import machineconfig.scripts.python.devops_helpers.devops_add_identity as helper
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
    run_shell_script(script=program)

