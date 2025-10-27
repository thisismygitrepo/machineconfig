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


def share_file_send(path: Annotated[str, typer.Argument(help="Path to the file or directory to send")],
                    zip_folder: Annotated[bool, typer.Option("--zip", help="Zip folder before sending")] = False,
                    code: Annotated[str | None, typer.Option("--code", "-c", help="Codephrase used to connect to relay")] = None,
                    text: Annotated[str | None, typer.Option("--text", "-t", help="Send some text")] = None,
                    qrcode: Annotated[bool, typer.Option("--qrcode", "--qr", help="Show receive code as a qrcode")] = False,
                    ) -> None:
    """Send a file using croc with relay server."""
    from machineconfig.utils.installer_utils.installer import install_if_missing
    install_if_missing(which="croc")
    # Get relay server IP from environment or use default
    import socket
    import platform
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8',80))
    local_ip_v4 = s.getsockname()[0]
    s.close()
    relay_port = "443"
    is_windows = platform.system() == "Windows"
    
    # Build command parts
    relay_arg = f"--relay {local_ip_v4}:{relay_port} --ip {local_ip_v4}:{relay_port}"
    zip_arg = "--zip" if zip_folder else ""
    text_arg = f"--text '{text}'" if text else ""
    qrcode_arg = "--qrcode" if qrcode else ""
    path_arg = f"{path}" if not text else ""
    
    if is_windows:
        # Windows PowerShell format
        code_arg = f"--code {code}" if code else ""
        script = f"""croc {relay_arg} send {zip_arg} {code_arg} {qrcode_arg} {text_arg} {path_arg}"""
    else:
        # Linux/macOS Bash format
        if code:
            script = f"""export CROC_SECRET="{code}"
croc {relay_arg} send {zip_arg} {qrcode_arg} {text_arg} {path_arg}"""
        else:
            script = f"""croc {relay_arg} send {zip_arg} {qrcode_arg} {text_arg} {path_arg}"""
    
    typer.echo(f"🚀 Sending file: {path}. Use: devops network receive")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=script, display_script=True, clean_env=False)


def share_file_receive(code_args: Annotated[list[str], typer.Argument(help="Receive code or full relay command. Examples: '7121-donor-olympic-bicycle' or '--relay 10.17.62.206:443 0782-paris-pencil-torso'")],) -> None:
    """Receive a file using croc with relay server.
Usage examples:
    devops network receive 7121-donor-olympic-bicycle
    devops network receive --relay 10.17.62.206:443 0782-paris-pencil-torso
    devops network receive -- --relay 10.17.62.206:443 0782-paris-pencil-torso
"""
    from machineconfig.utils.installer_utils.installer import install_if_missing
    install_if_missing(which="croc")
    import platform
    import re
    
    is_windows = platform.system() == "Windows"
    
    # Join all arguments back into a single string
    code = " ".join(code_args)
    
    # Parse input to extract components
    secret_code: str | None = None
    relay_server: str | None = None
    
    # Check if it's Linux/macOS format with CROC_SECRET
    linux_match = re.match(r'CROC_SECRET\s*=\s*["\']?([^"\']+)["\']?\s+croc\s+--relay\s+(\S+)(?:\s+--yes)?', code)
    if linux_match:
        secret_code = linux_match.group(1)
        relay_server = linux_match.group(2)
    else:
        # Check if it's Windows format or partial command
        windows_match = re.match(r'(?:croc\s+)?(?:--relay\s+(\S+)\s+)?([a-z0-9-]+(?:-[a-z0-9-]+){3})(?:\s+--yes)?', code, re.IGNORECASE)
        if windows_match:
            relay_server = windows_match.group(1)
            secret_code = windows_match.group(2)
        else:
            # Fallback: treat entire code as secret if it looks like a code
            code_pattern = r'^[a-z0-9-]+(?:-[a-z0-9-]+){3}$'
            if re.match(code_pattern, code.strip(), re.IGNORECASE):
                secret_code = code.strip()
    
    if not secret_code:
        raise ValueError(f"Could not parse croc code from input: {code}")
    
    # Build the appropriate script for current OS
    if is_windows:
        # Windows PowerShell format: croc --relay server:port secret-code --yes
        relay_arg = f"--relay {relay_server}" if relay_server else ""
        script = f"""croc {relay_arg} {secret_code} --yes"""
    else:
        # Linux/macOS Bash format: CROC_SECRET="secret-code" croc --relay server:port --yes
        relay_arg = f"--relay {relay_server}" if relay_server else ""
        script = f"""export CROC_SECRET="{secret_code}"
croc {relay_arg} --yes"""
    
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=script, display_script=True, clean_env=False)


def get_share_file_app():
    app = typer.Typer(name="share-file", help="Send or receive files using croc with relay server.")
    app.command(name="send", no_args_is_help=True, hidden=False, help="[s] send files from here.")(share_file_send)
    app.command(name="s", no_args_is_help=True, hidden=True, help="[s] send files from here.")(share_file_send)
    app.command(name="receive", no_args_is_help=True, hidden=False, help="[r] receive files to here.")(share_file_receive)
    app.command(name="r", no_args_is_help=True, hidden=True, help="[r] receive files to here.")(share_file_receive)
    return app

def main_with_parser():
    typer.run(main)


if __name__ == "__main__":
    pass