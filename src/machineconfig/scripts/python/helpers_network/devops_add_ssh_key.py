"""SSH"""

from platform import system
from machineconfig.utils.source_of_truth import LIBRARY_ROOT
from machineconfig.utils.path_extended import PathExtended
from rich.console import Console
from rich.panel import Panel
from rich import box
from typing import Optional, Annotated
import typer


console = Console()


def get_add_ssh_key_script(path_to_key: PathExtended) -> str:
    console.print(Panel("🔑 SSH KEY CONFIGURATION", title="[bold blue]SSH Setup[/bold blue]"))
    if system() == "Linux" or system() == "Darwin":
        authorized_keys = PathExtended.home().joinpath(".ssh/authorized_keys")
        console.print(Panel(f"🐧 Linux SSH configuration\n📄 Authorized keys file: {authorized_keys}", title="[bold blue]System Info[/bold blue]"))
    elif system() == "Windows":
        authorized_keys = PathExtended("C:/ProgramData/ssh/administrators_authorized_keys")
        console.print(Panel(f"🪟 Windows SSH configuration\n📄 Authorized keys file: {authorized_keys}", title="[bold blue]System Info[/bold blue]"))
    else:
        console.print(Panel("❌ ERROR: Unsupported operating system\nOnly Linux and Windows are supported", title="[bold red]Error[/bold red]"))
        raise NotImplementedError

    if authorized_keys.exists():
        split = "\n"
        keys_text = authorized_keys.read_text(encoding="utf-8").split(split)
        key_count = len([k for k in keys_text if k.strip()])
        console.print(Panel(f"🔍 Current SSH authorization status\n✅ Found {key_count} authorized key(s)", title="[bold blue]Status[/bold blue]"))
        if path_to_key.read_text(encoding="utf-8") in authorized_keys.read_text(encoding="utf-8"):
            console.print(Panel(f"⚠️  Key already authorized\nKey: {path_to_key.name}\nStatus: Already present in authorized_keys file\nNo action required", title="[bold yellow]Warning[/bold yellow]"))
            program = ""
        else:
            console.print(Panel(f"➕ Adding new SSH key to authorized keys\n🔑 Key file: {path_to_key.name}", title="[bold blue]Action[/bold blue]"))
            if system() == "Linux" or system() == "Darwin":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            elif system() == "Windows":
                program_path = LIBRARY_ROOT.joinpath("setup_windows/add-sshkey.ps1")
                program = program_path.expanduser().read_text(encoding="utf-8")
                place_holder = r'$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"'
                assert place_holder in program, f"This section performs string manipulation on the script {program_path} to add the key to the authorized_keys file. The script has changed and the string {place_holder} is not found."
                program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')
                console.print(Panel("🔧 Configured PowerShell script for Windows\n📝 Replaced placeholder with actual key path", title="[bold blue]Configuration[/bold blue]"))
            else:
                raise NotImplementedError
    else:
        console.print(Panel(f"📝 Creating new authorized_keys file\n🔑 Using key: {path_to_key.name}", title="[bold blue]Action[/bold blue]"))
        if system() == "Linux" or system() == "Darwin":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
            program = PathExtended(program_path).expanduser().read_text(encoding="utf-8").replace('$sshfile=""', f'$sshfile="{path_to_key}"')
            console.print(Panel("🔧 Configured PowerShell script for Windows\n📝 Set key path in script", title="[bold blue]Configuration[/bold blue]"))

    if system() == "Linux" or system() == "Darwin":
        program += """
sudo chmod 700 ~/.ssh
sudo chmod 644 ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/*.pub
sudo service ssh --full-restart
# from superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder
"""
    return program


"""
Common pitfalls: 
🚫 Wrong line endings (LF/CRLF) in config files
🌐 Network port conflicts (try 2222 -> 2223) between WSL and Windows
sudo service ssh restart
sudo service ssh status
sudo nano /etc/ssh/sshd_config
"""


def main(pub_path: Annotated[Optional[str], typer.Argument(..., help="Path to the public key file")] = None,
         pub_choose: Annotated[bool, typer.Option(..., "--choose", "-c", help="Choose from available public keys in ~/.ssh")] = False,
         pub_val: Annotated[bool, typer.Option(..., "--paste", "-p", help="Paste the public key content manually")] = False,
         from_github: Annotated[Optional[str], typer.Option(..., "--from-github", "-g", help="Fetch public keys from a GitHub username")] = None
         ) -> None:
    
    if pub_path:
        key_path = PathExtended(pub_path).expanduser().absolute()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        if not key_path.exists():
            console.print(Panel(f"❌ ERROR: Provided key path does not exist\nPath: {key_path}", title="[bold red]Error[/bold red]"))
            raise FileNotFoundError(f"Provided key path does not exist: {key_path}")
        console.print(Panel(f"📄 Using provided public key file: {key_path}", title="[bold blue]Info[/bold blue]"))
        program = get_add_ssh_key_script(key_path)
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script=program)
        console.print(Panel("✅ SSH KEY AUTHORIZATION COMPLETED", box=box.DOUBLE_EDGE, title_align="left"))
        return
    elif pub_choose:
        console.print(Panel("🔐 SSH PUBLIC KEY AUTHORIZATION TOOL", box=box.DOUBLE_EDGE, title_align="left"))
        console.print(Panel("🔍 Searching for public keys...", title="[bold blue]SSH Setup[/bold blue]", border_style="blue"))
        pub_keys = PathExtended.home().joinpath(".ssh").search("*.pub")
        if pub_keys:
            console.print(Panel(f"✅ Found {len(pub_keys)} public key(s)", title="[bold green]Status[/bold green]", border_style="green"))
        else:
            console.print(Panel("⚠️  No public keys found", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            return
        console.print(Panel(f"🔄 Processing all {len(pub_keys)} public keys...", title="[bold blue]Processing[/bold blue]", border_style="blue"))
        program = "\n\n\n".join([get_add_ssh_key_script(key) for key in pub_keys])

    elif pub_val:
        console.print(Panel("📋 Please provide a filename and paste the public key content", title="[bold blue]Input Required[/bold blue]", border_style="blue"))
        key_filename = input("📝 File name (default: my_pasted_key.pub): ") or "my_pasted_key.pub"
        key_path = PathExtended.home().joinpath(f".ssh/{key_filename}")
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(input("🔑 Paste the public key here: "), encoding="utf-8")
        console.print(Panel(f"💾 Key saved to: {key_path}", title="[bold green]Success[/bold green]", border_style="green"))
        program = get_add_ssh_key_script(key_path)
    elif from_github:
        console.print(Panel(f"🌐 Fetching public keys from GitHub user: {from_github}", title="[bold blue]GitHub Fetch[/bold blue]", border_style="blue"))
        import requests
        response = requests.get(f"https://api.github.com/users/{from_github}/keys")
        if response.status_code != 200:
            console.print(Panel(f"❌ ERROR: Failed to fetch keys from GitHub user {from_github}\nStatus Code: {response.status_code}", title="[bold red]Error[/bold red]", border_style="red"))
            raise RuntimeError(f"Failed to fetch keys from GitHub user {from_github}: Status Code {response.status_code}")
        keys = response.json()
        if not keys:
            console.print(Panel(f"⚠️  No public keys found for GitHub user: {from_github}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            return
        console.print(Panel(f"✅ Found {len(keys)} public key(s) for user: {from_github}", title="[bold green]Success[/bold green]", border_style="green"))
        key_path = PathExtended.home().joinpath(f".ssh/{from_github}_github_keys.pub")
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text("\n".join([key["key"] for key in keys]), encoding="utf-8")
        console.print(Panel(f"💾 Keys saved to: {key_path}", title="[bold green]Success[/bold green]", border_style="green"))
        program = get_add_ssh_key_script(key_path)
    else:
        console.print(Panel("❌ ERROR: No method provided to add SSH key\nUse --help for options", title="[bold red]Error[/bold red]", border_style="red"))
        raise ValueError("No method provided to add SSH key. Use --help for options.")
    console.print(Panel("🚀 SSH KEY AUTHORIZATION READY\nRun the generated script to apply changes", box=box.DOUBLE_EDGE, title_align="left"))
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=program)

    import machineconfig.scripts.python.helpers_network.address as helper
    res = helper.select_lan_ipv4(prefer_vpn=False)
    if res is None:
        console.print(Panel("❌ ERROR: Could not determine local LAN IPv4 address", title="[bold red]Error[/bold red]", border_style="red"))
        raise typer.Exit(code=1)
    local_ip_v4 = res

    console.print(Panel(f"🌐 This computer is accessible at: {local_ip_v4}", title="[bold green]Network Info[/bold green]", border_style="green"))
    console.print(Panel("✅ SSH KEY AUTHORIZATION COMPLETED", box=box.DOUBLE_EDGE, title_align="left"))


if __name__ == "__main__":
    pass
