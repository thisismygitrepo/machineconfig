import typer
from typing import Optional, Annotated


def install_ssh_server() -> None:
    """📡 Install SSH server"""
    import platform
    if platform.system() == "Windows":
        from machineconfig.setup_windows import SSH_SERVER
        script = SSH_SERVER.read_text(encoding="utf-8")
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        script = """
sudo nala install openssh-server -y || true  # try to install first
# sudo nala purge openssh-server -y
# sudo nala install openssh-server -y
echo "✅ FINISHED installing openssh-server."""
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=script)


def add_ssh_key(
    path: Annotated[Optional[str], typer.Option(..., help="Path to the public key file")] = None,
    choose: Annotated[bool, typer.Option(..., "--choose", "-c", help="Choose from available public keys in ~/.ssh/*.pub")] = False,
    value: Annotated[bool, typer.Option(..., "--value", "-v", help="Paste the public key content manually")] = False,
    github: Annotated[Optional[str], typer.Option(..., "--github", "-g", help="Fetch public keys from a GitHub username")] = None,
) -> None:
    """🔑 Add SSH public key to this machine so its accessible by owner of corresponding private key."""
    import machineconfig.scripts.python.helpers_network.ssh_add_ssh_key as helper
    helper.main(pub_path=path, pub_choose=choose, pub_val=value, from_github=github)


def add_ssh_identity() -> None:
    """🗝️ Add SSH identity (private key) to this machine"""
    import machineconfig.scripts.python.helpers_network.ssh_add_identity as helper
    helper.main()


def debug_ssh() -> None:
    """🐛 Debug SSH connection"""
    from platform import system
    if system() == "Linux" or system() == "Darwin":
        import machineconfig.scripts.python.helpers_network.ssh_debug_linux as helper
        helper.ssh_debug_linux()
    elif system() == "Windows":
        import machineconfig.scripts.python.helpers_network.ssh_debug_windows as helper
        helper.ssh_debug_windows()
    else:
        raise NotImplementedError(f"Platform {system()} is not supported.")


def get_app() -> typer.Typer:
    ssh_app = typer.Typer(help="🔐 SSH subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    ssh_app.command(name="install-server", help="📡 [i] Install SSH server")(install_ssh_server)
    ssh_app.command(name="i", help="Install SSH server", hidden=True)(install_ssh_server)
    ssh_app.command(name="add-key", help="🔑 [k] Add SSH public key to this machine", no_args_is_help=True)(add_ssh_key)
    ssh_app.command(name="k", help="Add SSH public key to this machine", hidden=True, no_args_is_help=True)(add_ssh_key)
    ssh_app.command(name="add-identity", help="🗝️ [A] Add SSH identity (private key) to this machine")(add_ssh_identity)
    ssh_app.command(name="A", help="Add SSH identity (private key) to this machine", hidden=True)(add_ssh_identity)
    ssh_app.command(name="debug", help="🐛 [d] Debug SSH connection")(debug_ssh)
    ssh_app.command(name="d", help="Debug SSH connection", hidden=True)(debug_ssh)
    return ssh_app
