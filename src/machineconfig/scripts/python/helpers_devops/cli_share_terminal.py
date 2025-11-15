
from typing import Optional, Annotated
import typer

"""
reference:
# https://github.com/tsl0922/ttyd/wiki/Serving-web-fonts
# -t "fontFamily=CaskaydiaCove" bash
# --terminal-type xterm-kitty

"""


def display_terminal_url(local_ip_v4: str, port: int, protocol: str = "http") -> None:
    """Display a flashy, unmissable terminal URL announcement."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    console = Console()
    # Create the main message with styling
    url_text = Text(f"{protocol}://{local_ip_v4}:{port}", style="bold bright_cyan underline")
    message = Text.assemble(
        ("🚀 ", "bright_red"),
        ("Terminal is now accessible at: ", "bright_white bold"),
        url_text,
        (" 🚀", "bright_red")
    )
    
    # Create a fancy panel with borders and styling
    panel = Panel(
        Align.center(message),
        title="[bold bright_green]🌐 WEB TERMINAL READY 🌐[/bold bright_green]",
        subtitle="[italic bright_yellow]⚡ Click the link above to access your terminal! ⚡[/italic bright_yellow]",
        border_style="bright_magenta",
        padding=(1, 2),
        expand=False
    )
    # Print with extra spacing and attention-grabbing elements
    # console.print("\n" + "🔥" * 60 + "\n", style="bright_red bold")
    console.print(panel)
    # console.print("🔥" * 60 + "\n", style="bright_red bold")


def share_terminal(
    port: Annotated[Optional[int], typer.Option("--port", "-p", help="Port to run the terminal server on (default: 7681)")] = None,
    username: Annotated[Optional[str], typer.Option("--username", "-u", help="Username for terminal access (default: current user)")] = None,
    password: Annotated[Optional[str], typer.Option("--password", "-w", help="Password for terminal access (default: from ~/dotfiles/creds/passwords/quick_password)")] = None,
    start_command: Annotated[Optional[str], typer.Option("--start-command", "-s", help="Command to run on terminal start (default: bash/powershell)")] = None,
    ssl: Annotated[bool, typer.Option("--ssl", "-S", help="Enable SSL")] = False,
    ssl_cert: Annotated[Optional[str], typer.Option("--ssl-cert", "-C", help="SSL certificate file path")] = None,
    ssl_key: Annotated[Optional[str], typer.Option("--ssl-key", "-K", help="SSL key file path")] = None,
    ssl_ca: Annotated[Optional[str], typer.Option("--ssl-ca", "-A", help="SSL CA file path for client certificate verification")] = None,
    over_internet: Annotated[bool, typer.Option("--over-internet", "-i", help="Expose the terminal over the internet using ngrok")] = False
) -> None:
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    install_if_missing("ttyd")
    if over_internet: install_if_missing("ngrok")

    from pathlib import Path
    if username is None:
        import getpass
        username = getpass.getuser()
    if password is None:
        pwd_path = Path.home().joinpath("dotfiles/creds/passwords/quick_password")
        if pwd_path.exists():
            password = pwd_path.read_text(encoding="utf-8").strip()
        else:
            raise ValueError("Password not provided and default password file does not exist.")

    if port is None:
        port = 7681  # Default port for ttyd

    # Handle SSL certificate defaults
    if ssl:
        if ssl_cert is None:
            ssl_cert = str(Path.home().joinpath("dotfiles/creds/passwords/ssl/origin_server/cert.pem"))
        if ssl_key is None:
            ssl_key = str(Path.home().joinpath("dotfiles/creds/passwords/ssl/origin_server/key.pem"))
        
        # Verify SSL files exist
        cert_path = Path(ssl_cert)
        key_path = Path(ssl_key)
        
        if not cert_path.exists():
            raise FileNotFoundError(f"SSL certificate file not found: {ssl_cert}")
        if not key_path.exists():
            raise FileNotFoundError(f"SSL key file not found: {ssl_key}")
        
        if ssl_ca and not Path(ssl_ca).exists():
            raise FileNotFoundError(f"SSL CA file not found: {ssl_ca}")

    import machineconfig.scripts.python.helpers_network.address as helper
    res = helper.select_lan_ipv4(prefer_vpn=False)
    if res is None:
        print("❌ Error: Could not determine local LAN IPv4 address for terminal.")
        raise typer.Exit(code=1)
    local_ip_v4 = res

    # Display the flashy terminal announcement  
    protocol = "https" if ssl else "http"
    display_terminal_url(local_ip_v4, port, protocol)
    
    # Build ttyd command with SSL options
    ssl_args = ""
    if ssl:
        ssl_args = f"--ssl --ssl-cert {ssl_cert} --ssl-key {ssl_key}"
        if ssl_ca:
            ssl_args += f" --ssl-ca {ssl_ca}"

    if start_command is None:
        import platform
        if platform.system().lower() == "windows":
            start_command = "powershell"
        else:
            start_command = "bash"

    import subprocess
    import time

    ttyd_cmd = f"ttyd --writable -t enableSixel=true {ssl_args} --port {port} --credential \"{username}:{password}\" -t 'theme={{\"background\": \"black\"}}' {start_command}"
    ttyd_process = subprocess.Popen(ttyd_cmd, shell=True)
    processes = [ttyd_process]
    
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
            print("Terminal server is running. Press Ctrl+C to stop.")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nTerminating processes...")
        for p in processes:
            p.terminate()
            p.wait()


def main_with_parser():
    typer.run(share_terminal)


if __name__ == "__main__":
    pass
