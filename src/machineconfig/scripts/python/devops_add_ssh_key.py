"""SSH"""

from platform import system
from machineconfig.utils.source_of_truth import LIBRARY_ROOT
from machineconfig.utils.options import display_options
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from rich.console import Console
from rich.panel import Panel
from rich import box  # Import box


console = Console()


def get_add_ssh_key_script(path_to_key: PathExtended):
    console.print(Panel("🔑 SSH KEY CONFIGURATION", title="[bold blue]SSH Setup[/bold blue]"))

    if system() == "Linux":
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
            if system() == "Linux":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            elif system() == "Windows":
                program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
                program = program_path.expanduser().read_text(encoding="utf-8")
                place_holder = r'$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"'
                assert place_holder in program, f"This section performs string manipulation on the script {program_path} to add the key to the authorized_keys file. The script has changed and the string {place_holder} is not found."
                program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')
                console.print(Panel("🔧 Configured PowerShell script for Windows\n📝 Replaced placeholder with actual key path", title="[bold blue]Configuration[/bold blue]"))
            else:
                raise NotImplementedError
    else:
        console.print(Panel(f"📝 Creating new authorized_keys file\n🔑 Using key: {path_to_key.name}", title="[bold blue]Action[/bold blue]"))
        if system() == "Linux":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
            program = PathExtended(program_path).expanduser().read_text(encoding="utf-8").replace('$sshfile=""', f'$sshfile="{path_to_key}"')
            console.print(Panel("🔧 Configured PowerShell script for Windows\n📝 Set key path in script", title="[bold blue]Configuration[/bold blue]"))

    if system() == "Linux":
        program += """

sudo chmod 700 ~/.ssh
sudo chmod 644 ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/*.pub
sudo service ssh --full-restart
# from superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder
"""
    return program


def main() -> None:
    console.print(Panel("🔐 SSH PUBLIC KEY AUTHORIZATION TOOL", box=box.DOUBLE_EDGE, title_align="left"))

    console.print(Panel("🔍 Searching for public keys...", title="[bold blue]SSH Setup[/bold blue]", border_style="blue"))

    pub_keys = PathExtended.home().joinpath(".ssh").search("*.pub")

    if pub_keys:
        console.print(Panel(f"✅ Found {len(pub_keys)} public key(s)", title="[bold green]Status[/bold green]", border_style="green"))
    else:
        console.print(Panel("⚠️  No public keys found", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))

    all_keys_option = f"all pub keys available ({len(pub_keys)})"
    i_have_path_option = "I have the path to the key file"
    i_paste_option = "I want to paste the key itself"

    res = display_options("Which public key to add? ", options=[str(x) for x in pub_keys] + [all_keys_option, i_have_path_option, i_paste_option])
    assert isinstance(res, str), f"Got {res} of type {type(res)} instead of str."

    if res == all_keys_option:
        console.print(Panel(f"🔄 Processing all {len(pub_keys)} public keys...", title="[bold blue]Processing[/bold blue]", border_style="blue"))
        program = "\n\n\n".join([get_add_ssh_key_script(key) for key in pub_keys])

    elif res == i_have_path_option:
        console.print(Panel("📂 Please provide the path to your public key", title="[bold blue]Input Required[/bold blue]", border_style="blue"))
        key_path = PathExtended(input("📋 Path: ")).expanduser().absolute()
        console.print(Panel(f"📄 Using key from path: {key_path}", title="[bold blue]Info[/bold blue]", border_style="blue"))
        program = get_add_ssh_key_script(key_path)

    elif res == i_paste_option:
        console.print(Panel("📋 Please provide a filename and paste the public key content", title="[bold blue]Input Required[/bold blue]", border_style="blue"))
        key_filename = input("📝 File name (default: my_pasted_key.pub): ") or "my_pasted_key.pub"
        key_path = PathExtended.home().joinpath(f".ssh/{key_filename}")
        key_path.write_text(input("🔑 Paste the public key here: "), encoding="utf-8")
        console.print(Panel(f"💾 Key saved to: {key_path}", title="[bold green]Success[/bold green]", border_style="green"))
        program = get_add_ssh_key_script(key_path)

    else:
        console.print(Panel(f"🔑 Using selected key: {PathExtended(res).name}", title="[bold blue]Info[/bold blue]", border_style="blue"))
        program = get_add_ssh_key_script(PathExtended(res))

    console.print(Panel("🚀 SSH KEY AUTHORIZATION READY\nRun the generated script to apply changes", box=box.DOUBLE_EDGE, title_align="left"))

    # return program
    import subprocess

    subprocess.run(program, shell=True, check=True)
    console.print(Panel("✅ SSH KEY AUTHORIZATION COMPLETED", box=box.DOUBLE_EDGE, title_align="left"))


if __name__ == "__main__":
    pass
