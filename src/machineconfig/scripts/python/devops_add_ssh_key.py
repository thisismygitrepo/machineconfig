"""SSH
"""


from platform import system
from machineconfig.utils.utils import LIBRARY_ROOT, display_options
from crocodile.file_management import P
from rich.console import Console
from rich.panel import Panel


console = Console()


def get_add_ssh_key_script(path_to_key: P):
    console.print(Panel("🔑 SSH KEY CONFIGURATION", title="[bold blue]SSH Setup[/bold blue]"))

    if system() == "Linux":
        authorized_keys = P.home().joinpath(".ssh/authorized_keys")
        console.print(Panel(f"🐧 Linux SSH configuration\n📄 Authorized keys file: {authorized_keys}", title="[bold blue]System Info[/bold blue]"))
    elif system() == "Windows":
        authorized_keys = P("C:/ProgramData/ssh/administrators_authorized_keys")
        console.print(Panel(f"🪟 Windows SSH configuration\n📄 Authorized keys file: {authorized_keys}", title="[bold blue]System Info[/bold blue]"))
    else:
        console.print(Panel("❌ ERROR: Unsupported operating system\nOnly Linux and Windows are supported", title="[bold red]Error[/bold red]"))
        raise NotImplementedError

    if authorized_keys.exists():
        split = "\n"
        keys_text = authorized_keys.read_text().split(split)
        key_count = len([k for k in keys_text if k.strip()])
        console.print(Panel(f"🔍 Current SSH authorization status\n✅ Found {key_count} authorized key(s)", title="[bold blue]Status[/bold blue]"))

        if path_to_key.read_text() in authorized_keys.read_text():
            console.print(Panel(f"⚠️  Key already authorized\nKey: {path_to_key.name}\nStatus: Already present in authorized_keys file\nNo action required", title="[bold yellow]Warning[/bold yellow]"))
            program = ""
        else:
            console.print(Panel(f"➕ Adding new SSH key to authorized keys\n🔑 Key file: {path_to_key.name}", title="[bold blue]Action[/bold blue]"))
            if system() == "Linux":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            elif system() == "Windows":
                program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
                program = program_path.expanduser().read_text()
                place_holder = r'$sshfile = "$env:USERPROFILE\\.ssh\\pubkey.pub"'
                assert place_holder in program, f"This section performs string manipulation on the script {program_path} to add the key to the authorized_keys file. The script has changed and the string {place_holder} is not found."
                program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')
                console.print(Panel("🔧 Configured PowerShell script for Windows\n📝 Replaced placeholder with actual key path", title="[bold blue]Configuration[/bold blue]"))
            else: raise NotImplementedError
    else:
        console.print(Panel(f"📝 Creating new authorized_keys file\n🔑 Using key: {path_to_key.name}", title="[bold blue]Action[/bold blue]"))
        if system() == "Linux":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
            program = P(program_path).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')
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


def main():
    print(f"""
╔{'═' * 150}╗
║ 🔐 SSH PUBLIC KEY AUTHORIZATION TOOL                                     ║
╚{'═' * 150}╝
""")
    
    print(f"""
╭{'─' * 150}╮
│ 🔍 Searching for public keys...                                          │
╰{'─' * 150}╯
""")
    
    pub_keys = P.home().joinpath(".ssh").search("*.pub")
    
    if pub_keys:
        print(f"""
╭{'─' * 150}╮
│ ✅ Found {len(pub_keys)} public key(s)                                           │
╰{'─' * 150}╯
""")
    else:
        print(f"""
╭{'─' * 150}╮
│ ⚠️  No public keys found                                                  │
╰{'─' * 150}╯
""")
    
    all_keys_option = f"all pub keys available ({len(pub_keys)})"
    i_have_path_option = "I have the path to the key file"
    i_paste_option = "I want to paste the key itself"
    
    res = display_options("Which public key to add? ", options=pub_keys.apply(str).list + [all_keys_option, i_have_path_option, i_paste_option])
    assert isinstance(res, str), f"Got {res} of type {type(res)} instead of str."
    
    if res == all_keys_option:
        print(f"""
╭{'─' * 150}╮
│ 🔄 Processing all {len(pub_keys)} public keys...                                  │
╰{'─' * 150}╯
""")
        program = "\n\n\n".join(pub_keys.apply(get_add_ssh_key_script))
    
    elif res == i_have_path_option:
        print(f"""
╭{'─' * 150}╮
│ 📂 Please provide the path to your public key                             │
╰{'─' * 150}╯
""")
        key_path = P(input("📋 Path: ")).expanduser().absolute()
        print(f"""
╭{'─' * 150}╮
│ 📄 Using key from path: {key_path}                        │
╰{'─' * 150}╯
""")
        program = get_add_ssh_key_script(key_path)
    
    elif res == i_paste_option:
        print(f"""
╭{'─' * 150}╮
│ 📋 Please provide a filename and paste the public key content             │
╰{'─' * 150}╯
""")
        key_filename = input("📝 File name (default: my_pasted_key.pub): ") or "my_pasted_key.pub"
        key_path = P.home().joinpath(f".ssh/{key_filename}")
        key_path.write_text(input("🔑 Paste the public key here: "))
        print(f"""
╭{'─' * 150}╮
│ 💾 Key saved to: {key_path}                           │
╰{'─' * 150}╯
""")
        program = get_add_ssh_key_script(key_path)
    
    else:
        print(f"""
╭{'─' * 150}╮
│ 🔑 Using selected key: {P(res).name}                                     │
╰{'─' * 150}╯
""")
        program = get_add_ssh_key_script(P(res))
    
    print(f"""
╔{'═' * 150}╗
║ 🚀 SSH KEY AUTHORIZATION READY                                           ║
║ Run the generated script to apply changes                                ║
╚{'═' * 150}╝
""")
    
    return program


if __name__ == '__main__':
    pass
