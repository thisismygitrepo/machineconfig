
import machineconfig.scripts.python.devops_helpers.cli_terminal as cli_terminal
import machineconfig.scripts.python.devops_helpers.cli_share_server as cli_share_server
import typer
from typing import Optional



def install_ssh_server():
    """📡 SSH install server"""
    import platform
    if platform.system() == "Windows":
        from machineconfig.setup_windows import SSH_SERVER
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        from machineconfig.setup_linux import SSH_SERVER
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=SSH_SERVER.read_text(encoding="utf-8"))

def add_ssh_key(path: Optional[str] = typer.Option(None, help="Path to the public key file"),
         choose: bool = typer.Option(False, "--choose", "-c", help="Choose from available public keys in ~/.ssh/*.pub"),
         value: bool = typer.Option(False, "--value", "-v", help="Paste the public key content manually"),
         github: Optional[str] = typer.Option(None, "--github", "-g", help="Fetch public keys from a GitHub username")
):
    """🔑 SSH add pub key to this machine so its accessible by owner of corresponding private key."""
    import machineconfig.scripts.python.devops_helpers.devops_add_ssh_key as helper
    helper.main(pub_path=path, pub_choose=choose, pub_val=value, from_github=github)
def add_ssh_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    import machineconfig.scripts.python.devops_helpers.devops_add_identity as helper
    helper.main()

def get_app():
    nw_apps = typer.Typer(help="🔐 [n] Network subcommands", no_args_is_help=True)
    nw_apps.command(name="share-terminal", help="📡  [t] Share terminal via web browser")(cli_terminal.main)
    nw_apps.command(name="t", help="Share terminal via web browser", hidden=True)(cli_terminal.main)
    nw_apps.command(name="share-server", help="🌐  [s] Start local/global server to share files/folders via web browser", no_args_is_help=True)(cli_share_server.main)
    nw_apps.command(name="s", help="Start local/global server to share files/folders via web browser", hidden=True, no_args_is_help=True)(cli_share_server.main)
    nw_apps.command(name="install-ssh-server", help="📡  [i] Install SSH server")(install_ssh_server)
    nw_apps.command(name="i", help="Install SSH server", hidden=True)(install_ssh_server)
    nw_apps.command(name="add-ssh-key", help="🔑  [k] Add SSH public key to this machine")(add_ssh_key)
    nw_apps.command(name="k", help="Add SSH public key to this machine", hidden=True)(add_ssh_key)
    nw_apps.command(name="add-ssh-identity", help="🗝️  [a] Add SSH identity (private key) to this machine")(add_ssh_identity)
    nw_apps.command(name="a", help="Add SSH identity (private key) to this machine", hidden=True)(add_ssh_identity)
    return nw_apps
