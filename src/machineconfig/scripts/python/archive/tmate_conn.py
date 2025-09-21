import argparse
import configparser
from pathlib import Path
import random
import string
import os
from rich.console import Console
from rich.panel import Panel


console = Console()


def get_conn_string(sess_name: str) -> str:
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath("dotfiles/creds/tmate/creds.ini"))
    sess_name = creds["sessions_names"][sess_name]
    user_name = creds["keys"]["username"]
    return f"{user_name}/{sess_name}@sgp1.tmate.io"


def main():
    console.print(Panel("🔌 Tmate Connection Manager", title="[bold]Welcome[/bold]"))

    parser = argparse.ArgumentParser(description="Tmate launcher")
    parser.add_argument("sess_name", help="session name", default=random.choices(list(string.digits + string.ascii_letters), k=20))
    args = parser.parse_args()

    console.print(f"🔍 Looking up session: {args.sess_name}")
    conn_string = get_conn_string(args.sess_name)

    console.print(Panel(f"SSH Connection String: ssh {conn_string}", title="[bold green]SSH Connection[/bold green]"))

    console.print("🚀 Connecting to tmate session...")
    os.system(f"ssh {conn_string}")

    console.print("✅ Connection closed")


if __name__ == "__main__":
    main()
