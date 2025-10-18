
import machineconfig.scripts.python.helpers_devops.cli_terminal as cli_terminal
import machineconfig.scripts.python.helpers_devops.cli_share_server as cli_share_server
import typer
from typing import Optional, Annotated



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


def add_ssh_key(path: Annotated[Optional[str], typer.Option(..., help="Path to the public key file")] = None,
         choose: Annotated[bool, typer.Option(..., "--choose", "-c", help="Choose from available public keys in ~/.ssh/*.pub")] = False,
         value: Annotated[bool, typer.Option(..., "--value", "-v", help="Paste the public key content manually")] = False,
         github: Annotated[Optional[str], typer.Option(..., "--github", "-g", help="Fetch public keys from a GitHub username")] = None
):
    """🔑 SSH add pub key to this machine so its accessible by owner of corresponding private key."""
    import machineconfig.scripts.python.nw.devops_add_ssh_key as helper
    helper.main(pub_path=path, pub_choose=choose, pub_val=value, from_github=github)
def add_ssh_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    import machineconfig.scripts.python.nw.devops_add_identity as helper
    helper.main()


def show_address():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8',80))
    local_ip_v4 = s.getsockname()[0]
    s.close()
    print(f"This computer is @ {local_ip_v4}")


def debug_ssh():
    """🐛 SSH debug"""
    from platform import system
    if system() == "Linux" or system() == "Darwin":
        import machineconfig.scripts.python.nw.ssh_debug_linux as helper
        helper.ssh_debug_linux()
    elif system() == "Windows":
        import machineconfig.scripts.python.nw.ssh_debug_windows as helper
        helper.ssh_debug_windows()
    else:
        raise NotImplementedError(f"Platform {system()} is not supported.")

def get_app():
    nw_apps = typer.Typer(help="🔐 [n] Network subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    nw_apps.command(name="share-terminal", help="📡  [t] Share terminal via web browser")(cli_terminal.main)
    nw_apps.command(name="t", help="Share terminal via web browser", hidden=True)(cli_terminal.main)
    nw_apps.command(name="share-server", help="🌐  [s] Start local/global server to share files/folders via web browser", no_args_is_help=True)(cli_share_server.main)
    nw_apps.command(name="s", help="Start local/global server to share files/folders via web browser", hidden=True, no_args_is_help=True)(cli_share_server.main)
    nw_apps.command(name="install-ssh-server", help="📡  [i] Install SSH server")(install_ssh_server)
    nw_apps.command(name="i", help="Install SSH server", hidden=True)(install_ssh_server)
    nw_apps.command(name="add-ssh-key", help="🔑  [k] Add SSH public key to this machine", no_args_is_help=True)(add_ssh_key)
    nw_apps.command(name="k", help="Add SSH public key to this machine", hidden=True, no_args_is_help=True)(add_ssh_key)
    nw_apps.command(name="add-ssh-identity", help="🗝️  [A] Add SSH identity (private key) to this machine")(add_ssh_identity)
    nw_apps.command(name="A", help="Add SSH identity (private key) to this machine", hidden=True)(add_ssh_identity)
    nw_apps.command(name="show-address", help="📌  [a] Show this computer addresses on network")(show_address)
    nw_apps.command(name="a", help="Show this computer addresses on network", hidden=True)(show_address)
    nw_apps.command(name="debug-ssh", help="🐛  [d] Debug SSH connection")(debug_ssh)
    nw_apps.command(name="d", help="Debug SSH connection", hidden=True)(debug_ssh)
    return nw_apps
