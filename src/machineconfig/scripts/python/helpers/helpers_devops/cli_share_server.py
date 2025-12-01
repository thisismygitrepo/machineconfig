from pathlib import Path
from typing import Optional, Annotated
from machineconfig.scripts.python.helpers.helpers_devops.cli_share_file import share_file_receive, share_file_send
import typer


def display_share_url(local_ip_v4: str, port: int, protocol: str = "http") -> None:
    """Display a flashy, unmissable share URL announcement."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    console = Console()
    # Create the main message with styling
    url_text = Text(f"{protocol}://{local_ip_v4}:{port}", style="bold bright_cyan underline")
    message = Text.assemble(
        ("🚀 ", "bright_red"),
        ("Share server is now accessible at: ", "bright_white bold"),
        url_text,
        (" 🚀", "bright_red")
    )
    # Create a fancy panel with borders and styling
    panel = Panel(
        Align.center(message),
        title="[bold bright_green]🌐 SHARE SERVER READY 🌐[/bold bright_green]",
        subtitle="[italic bright_yellow]⚡ Click the link above to access your shared files! ⚡[/italic bright_yellow]",
        border_style="bright_magenta",
        padding=(1, 2),
        expand=False
    )
    # Print with extra spacing and attention-grabbing elements
    console.print(panel)


def web_file_explorer(
    path: Annotated[str, typer.Argument(help="Path to the file or directory to share")],
    port: Annotated[Optional[int], typer.Option("--port", "-p", help="Port to run the share server on (default: 8080)")] = None,
    username: Annotated[Optional[str], typer.Option("--username", "-u", help="Username for share access (default: current user)")] = None,
    no_auth: Annotated[bool, typer.Option("--no-auth", "-na", help="Disable authentication for share access")] = False,
    password: Annotated[Optional[str], typer.Option("--password", "-w", help="Password for share access (default: from ~/dotfiles/creds/passwords/quick_password)")] = None,
    bind_address: Annotated[str, typer.Option("--bind", "-a", help="Address to bind the server to")] = "0.0.0.0",
    over_internet: Annotated[bool, typer.Option("--over-internet", "-i", help="Expose the share server over the internet using ngrok")] = False,
    backend: Annotated[str, typer.Option("--backend", "-b", help="Backend to use: filebrowser (default), miniserve, qrcp, or easy-sharing")] = "miniserve",
) -> None:
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing

    if backend not in ["filebrowser", "miniserve", "qrcp", "easy-sharing"]:
        typer.echo(f"❌ ERROR: Invalid backend '{backend}'. Must be one of: filebrowser, miniserve, qrcp, easy-sharing", err=True)
        raise typer.Exit(code=1)
    install_if_missing(which=backend)
    if over_internet:
        install_if_missing(which="ngrok")
    if password is None and not no_auth:
        pwd_path = Path.home().joinpath("dotfiles/creds/passwords/quick_password")
        if pwd_path.exists():
            password = pwd_path.read_text(encoding="utf-8").strip()
            if username is None:
                import getpass
                username = getpass.getuser()
        # else:
        #     typer.echo(f"⚠️  WARNING: Password not provided and default password file does not exist.\nPath: {pwd_path}\nUsing default password: 'quick_password' (insecure!)", err=True)
        #     raise typer.Exit(code=1)


    if port is None:
        port = 8080

    import machineconfig.scripts.python.helpers.helpers_network.address as helper
    res = helper.select_lan_ipv4(prefer_vpn=False)
    if res is None:
        typer.echo("❌ ERROR: Could not determine local LAN IPv4 address for share server.", err=True)
        raise typer.Exit(code=1)
    local_ip_v4 = res

    protocol = "http"
    display_share_url(local_ip_v4, port, protocol)
    
    path_obj = Path(path).resolve()
    if not path_obj.exists():
        typer.echo(f"❌ ERROR: Path does not exist: {path}", err=True)
        raise typer.Exit(code=1)
    
    if backend == "filebrowser":
        db_path = Path.home().joinpath(".config/filebrowser/filebrowser.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        command = f"""
filebrowser users add {username} "{password}" --database {db_path}
filebrowser --address {bind_address} --port {port} --root "{path_obj}" --database {db_path}
"""
    elif backend == "miniserve":
        if username and password:
            auth_line = f"""--auth "{username}:{password}" """
        else:
            auth_line = ""
        command = f"""miniserve --port {port} --interfaces {bind_address} {auth_line} --upload-files --mkdir --enable-tar --enable-tar-gz --enable-zip --qrcode "{path_obj}" """
    elif backend == "easy-sharing":
        if username is None and password is None:
            auth_line = ""
        else:
            auth_line = f'--username "{username}" --password "{password}"'
        command = f"""easy-sharing --port {port} {auth_line} "{path_obj}" """
    elif backend == "qrcp":
        command = f"""qrcp --port {port} --bind {bind_address} "{path_obj}" """
    else:
        typer.echo(f"❌ ERROR: Unknown backend '{backend}'", err=True)
        raise typer.Exit(code=1)

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=command, strict=False)
    # import subprocess
    # import time
    # server_process: subprocess.Popen[bytes]
    # server_process = subprocess.Popen(command, shell=True)
    # processes = [server_process]
    # if over_internet:
    #     ngrok_process = subprocess.Popen(f"ngrok http {port}", shell=True)
    #     processes.append(ngrok_process)
    #     time.sleep(3)
    #     try:
    #         import requests
    #         response = requests.get("http://localhost:4040/api/tunnels")
    #         data = response.json()
    #         public_url = data['tunnels'][0]['public_url']
    #         print(f"🌐 Ngrok tunnel ready: {public_url}")
    #     except Exception as e:
    #         print(f"Could not retrieve ngrok URL: {e}")
    
    # try:
    #     while True:
    #         print(f"Share server ({backend}) is running. Press Ctrl+C to stop.")
    #         time.sleep(2)
    # except KeyboardInterrupt:
    #     print("\nTerminating processes...")
    #     for p in processes:
    #         p.terminate()
    #         p.wait()


def get_share_file_app():
    app = typer.Typer(name="share-file", help="Send or receive files using croc with relay server.")
    app.command(name="send", no_args_is_help=True, hidden=False, help="[s] send files from here.")(share_file_send)
    app.command(name="s", no_args_is_help=True, hidden=True, help="[s] send files from here.")(share_file_send)
    app.command(name="receive", no_args_is_help=True, hidden=False, help="[r] receive files to here.")(share_file_receive)
    app.command(name="r", no_args_is_help=True, hidden=True, help="[r] receive files to here.")(share_file_receive)
    return app

def main_with_parser():
    typer.run(web_file_explorer)


if __name__ == "__main__":
    pass