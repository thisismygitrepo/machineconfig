from pathlib import Path
from typing import Optional, Annotated
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


def main(
    path: Annotated[str, typer.Argument(help="Path to the file or directory to share")],
    port: Annotated[Optional[int], typer.Option("--port", "-p", help="Port to run the share server on (default: 8080)")] = None,
    username: Annotated[Optional[str], typer.Option("--username", "-u", help="Username for share access (default: current user)")] = None,
    password: Annotated[Optional[str], typer.Option("--password", "-w", help="Password for share access (default: from ~/dotfiles/creds/passwords/quick_password)")] = None,
    over_internet: Annotated[bool, typer.Option("--over-internet", "-i", help="Expose the share server over the internet using ngrok")] = False
) -> None:
    from machineconfig.utils.installer_utils.installer import install_if_missing
    install_if_missing(which="easy-sharing")
    if over_internet: install_if_missing(which="ngrok", )
    if username is None:
        import getpass
        username = getpass.getuser()
    if password is None:
        pwd_path = Path.home().joinpath("dotfiles/creds/passwords/quick_password")
        if pwd_path.exists():
            password = pwd_path.read_text(encoding="utf-8").strip()
        else:
            # raise ValueError("Password not provided and default password file does not exist.")
            typer.echo(f"⚠️  WARNING: Password not provided and default password file does not exist.\nPath: {pwd_path}\nUsing default password: 'quick_password' (insecure!)", err=True)
            typer.Exit(code=1)

    if port is None:
        port = 8080  # Default port for ezshare

    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8',80))
    local_ip_v4 = s.getsockname()[0]
    s.close()

    # Display the flashy share announcement  
    protocol = "http"
    display_share_url(local_ip_v4, port, protocol)
    import subprocess
    import time
    # Build ezshare command
    ezshare_cmd = f"""easy-sharing --port {port} --username {username} --password "{password}" {path}"""
    ezshare_process = subprocess.Popen(ezshare_cmd, shell=True)
    processes = [ezshare_process]
    
    if over_internet:
        ngrok_process = subprocess.Popen(f"ngrok http {port}", shell=True)
        processes.append(ngrok_process)
        time.sleep(3)
        try:
            import requests
            response = requests.get("http://localhost:4040/api/tunnels")
            data = response.json()
            public_url = data['tunnels'][0]['public_url']
            print(f"🌐 Ngrok tunnel ready: {public_url}")
        except Exception as e:
            print(f"Could not retrieve ngrok URL: {e}")
    
    try:
        while True:
            print("Share server is running. Press Ctrl+C to stop.")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nTerminating processes...")
        for p in processes:
            p.terminate()
            p.wait()


def main_with_parser():
    typer.run(main)


if __name__ == "__main__":
    pass