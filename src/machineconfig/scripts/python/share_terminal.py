

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align


"""
uv run --python 3.13 --with machineconfig 
reference:
# https://github.com/tsl0922/ttyd/wiki/Serving-web-fonts
# -t "fontFamily=CaskaydiaCove" bash
# --terminal-type xterm-kitty

"""


def display_terminal_url(local_ip_v4: str, port: int) -> None:
    """Display a flashy, unmissable terminal URL announcement."""
    console = Console()
    
    # Create the main message with styling
    url_text = Text(f"http://{local_ip_v4}:{port}", style="bold bright_cyan underline")
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
    console.print("\n" + "🔥" * 60 + "\n", style="bright_red bold")
    console.print(panel)
    console.print("🔥" * 60 + "\n", style="bright_red bold")


def main(port: Optional[int]=None, password: Optional[str]=None) -> None:
    if password is None:
        pwd_path = Path.home().joinpath("dotfiles/creds/passwords/quick_password")
        if pwd_path.exists():
            password = pwd_path.read_text(encoding="utf-8").strip()
        else:
            raise ValueError("Password not provided and default password file does not exist.")

    if port is None:
        port = 7681  # Default port for ttyd

    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8',80))
    local_ip_v4 = s.getsockname()[0]
    s.close()

    # Display the flashy terminal announcement
    display_terminal_url(local_ip_v4, port)

    code = f"""
#!/bin/bash
uv run --python 3.13 --with machineconfig install -ttyd
ttyd --writable -t enableSixel=true --port {port} --credential "$USER:{password}" -t 'theme={"background": "black"}' bash
"""
    import subprocess
    subprocess.run(code, shell=True, check=True)


def main_with_parser():
    typer.run(main)


if __name__ == "__main__":
    pass
