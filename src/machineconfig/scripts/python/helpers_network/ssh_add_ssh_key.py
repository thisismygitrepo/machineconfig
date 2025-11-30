"""SSH"""

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box
from typing import Optional, Annotated
import typer


console = Console()


def get_add_ssh_key_script(path_to_key: Path, verbose: bool = True) -> tuple[str, str]:
    """Returns (program_script, status_message) tuple."""
    os_name = system()
    if os_name == "Linux" or os_name == "Darwin":
        authorized_keys = Path.home().joinpath(".ssh/authorized_keys")
        os_icon, os_label = "🐧", "Linux/macOS"
    elif os_name == "Windows":
        authorized_keys = Path("C:/ProgramData/ssh/administrators_authorized_keys")
        os_icon, os_label = "🪟", "Windows"
    else:
        raise NotImplementedError("Only Linux, macOS and Windows are supported")

    status_lines: list[str] = [f"{os_icon} {os_label} │ Auth file: {authorized_keys}"]

    if authorized_keys.exists():
        keys_text = authorized_keys.read_text(encoding="utf-8").split("\n")
        key_count = len([k for k in keys_text if k.strip()])
        status_lines.append(f"🔑 Existing keys: {key_count}")
        if path_to_key.read_text(encoding="utf-8") in authorized_keys.read_text(encoding="utf-8"):
            status_lines.append(f"⚠️  Key [yellow]{path_to_key.name}[/yellow] already authorized, skipping")
            program = ""
        else:
            status_lines.append(f"➕ Adding: [green]{path_to_key.name}[/green]")
            if os_name == "Linux" or os_name == "Darwin":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            elif os_name == "Windows":
                from machineconfig.setup_windows import SSH_ADD_KEY
                program = Path(SSH_ADD_KEY).expanduser().read_text(encoding="utf-8")
                place_holder = r'$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"'
                assert place_holder in program, f"Script {SSH_ADD_KEY} changed, placeholder not found: {place_holder}"
                program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')
            else:
                raise NotImplementedError
    else:
        status_lines.append(f"📝 Creating auth file with: [green]{path_to_key.name}[/green]")
        if os_name == "Linux" or os_name == "Darwin":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            from machineconfig.setup_windows import SSH_ADD_KEY
            program = Path(SSH_ADD_KEY).expanduser().read_text(encoding="utf-8")
            place_holder = r'$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"'
            assert place_holder in program, f"Script {SSH_ADD_KEY} changed, placeholder not found: {place_holder}"
            program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')

    if os_name == "Linux" or os_name == "Darwin":
        program += """
sudo chmod 700 ~/.ssh
sudo chmod 644 ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/*.pub
sudo service ssh --full-restart
# from superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder
"""
    return program, "\n".join(status_lines)


"""
Common pitfalls: 
🚫 Wrong line endings (LF/CRLF) in config files
🌐 Network port conflicts (try 2222 -> 2223) between WSL and Windows
sudo service ssh restart
sudo service ssh status
sudo nano /etc/ssh/sshd_config
"""


def main(pub_path: Annotated[Optional[str], typer.Argument(help="Path to the public key file")] = None,
         pub_choose: Annotated[bool, typer.Option("--choose", "-c", help="Choose from available public keys in ~/.ssh")] = False,
         pub_val: Annotated[bool, typer.Option("--paste", "-p", help="Paste the public key content manually")] = False,
         from_github: Annotated[Optional[str], typer.Option("--from-github", "-g", help="Fetch public keys from a GitHub username")] = None
         ) -> None:
    info_lines: list[str] = []
    program = ""
    status_msg = ""

    if pub_path:
        key_path = Path(pub_path).expanduser().absolute()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        if not key_path.exists():
            console.print(Panel(f"❌ Key path does not exist: {key_path}", title="[bold red]Error[/bold red]", border_style="red"))
            raise FileNotFoundError(f"Provided key path does not exist: {key_path}")
        info_lines.append(f"📄 Source: Local file │ {key_path}")
        program, status_msg = get_add_ssh_key_script(key_path)

    elif pub_choose:
        pub_keys = list(Path.home().joinpath(".ssh").glob("*.pub"))
        if not pub_keys:
            console.print(Panel("⚠️  No public keys found in ~/.ssh", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            return
        info_lines.append(f"📄 Source: Local ~/.ssh │ Found {len(pub_keys)} key(s)")
        programs: list[str] = []
        statuses: list[str] = []
        for key in pub_keys:
            p, s = get_add_ssh_key_script(key)
            programs.append(p)
            statuses.append(s)
        program = "\n\n\n".join(programs)
        status_msg = "\n".join(statuses)

    elif pub_val:
        key_filename = input("📝 File name (default: my_pasted_key.pub): ") or "my_pasted_key.pub"
        key_path = Path.home().joinpath(f".ssh/{key_filename}")
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(input("🔑 Paste the public key here: "), encoding="utf-8")
        info_lines.append(f"📄 Source: Pasted │ Saved to {key_path}")
        program, status_msg = get_add_ssh_key_script(key_path)

    elif from_github:
        import requests
        response = requests.get(f"https://api.github.com/users/{from_github}/keys")
        if response.status_code != 200:
            console.print(Panel(f"❌ GitHub API error for user '{from_github}' │ Status: {response.status_code}", title="[bold red]Error[/bold red]", border_style="red"))
            raise RuntimeError(f"Failed to fetch keys from GitHub user {from_github}: Status Code {response.status_code}")
        keys = response.json()
        if not keys:
            console.print(Panel(f"⚠️  No public keys found for GitHub user: {from_github}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            return
        key_path = Path.home().joinpath(f".ssh/{from_github}_github_keys.pub")
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text("\n".join([key["key"] for key in keys]), encoding="utf-8")
        info_lines.append(f"📄 Source: GitHub @{from_github} │ {len(keys)} key(s) → {key_path}")
        program, status_msg = get_add_ssh_key_script(key_path)

    else:
        console.print(Panel("❌ No key source specified. Use --help for options.", title="[bold red]Error[/bold red]", border_style="red"))
        raise ValueError("No method provided to add SSH key. Use --help for options.")

    combined_info = "\n".join(info_lines + [""] + status_msg.split("\n"))
    console.print(Panel(combined_info, title="[bold blue]🔑 SSH Key Authorization[/bold blue]", border_style="blue"))

    if program.strip():
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script=program)

    import machineconfig.scripts.python.helpers_network.address as helper
    res = helper.select_lan_ipv4(prefer_vpn=False)
    if res is None:
        console.print(Panel("❌ Could not determine local LAN IPv4 address", title="[bold red]Error[/bold red]", border_style="red"))
        raise typer.Exit(code=1)

    console.print(Panel(f"✅ Complete │ This machine accessible at: [green]{res}[/green]", title="[bold green]SSH Key Authorization[/bold green]", border_style="green", box=box.DOUBLE_EDGE))


if __name__ == "__main__":
    pass
