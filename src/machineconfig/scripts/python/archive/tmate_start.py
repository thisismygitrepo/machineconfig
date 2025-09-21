"""Tmate"""

import argparse
import configparser
from pathlib import Path
import random
import string
import os
from rich.console import Console
from rich.panel import Panel


def main():
    console = Console()

    console.print(Panel("📡 Tmate Session Launcher", title="[bold blue]Welcome[/bold blue]", subtitle="Manage your tmate sessions effortlessly"))

    console.print("[bold yellow]Loading credentials...[/bold yellow]")
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath("dotfiles/creds/tmate/creds.ini"))
    console.print("[green]Credentials loaded[/green]")

    parser = argparse.ArgumentParser(description="Tmate launcher")
    random_sess = random.choices(list(string.digits + string.ascii_letters), k=20)
    _ = random_sess
    parser.add_argument("sess_name", help="session name (new only with random string will be chosen if not passed)", default=None)

    args = parser.parse_args()

    console.print(f"🔍 Looking up session configuration: {args.sess_name}")
    sess_name = creds["sessions_names"][args.sess_name]
    api_key = creds["keys"]["api_key"]

    console.print(Panel(f"🚀 Starting tmate session: {sess_name}", title="[bold green]Session Info[/bold green]"))

    res = f"tmate -a ~/.ssh/authorized_keys -k {api_key} -n {sess_name} -F"
    console.print("[bold cyan]Running:[/bold cyan] tmate with configured API key and session name")
    os.system(res)

    console.print("[green]Tmate session ended[/green]")


if __name__ == "__main__":
    main()
