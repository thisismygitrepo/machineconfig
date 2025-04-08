"""SSH
"""


from platform import system
from machineconfig.utils.utils import LIBRARY_ROOT, display_options
from crocodile.file_management import P


def get_add_ssh_key_script(path_to_key: P):
    print(f"""
╔{'═' * 70}╗
║ 🔑 SSH KEY CONFIGURATION                                                 ║
╚{'═' * 70}╝
""")
    
    if system() == "Linux": 
        authorized_keys = P.home().joinpath(".ssh/authorized_keys")
        print(f"""
╭{'─' * 70}╮
│ 🐧 Linux SSH configuration                                               │
│ 📄 Authorized keys file: {authorized_keys}                      │
╰{'─' * 70}╯
""")
    elif system() == "Windows": 
        authorized_keys = P("C:/ProgramData/ssh/administrators_authorized_keys")
        print(f"""
╭{'─' * 70}╮
│ 🪟 Windows SSH configuration                                             │
│ 📄 Authorized keys file: {authorized_keys}                │
╰{'─' * 70}╯
""")
    else: 
        print(f"""
╔{'═' * 70}╗
║ ❌ ERROR: Unsupported operating system                                   ║
║ Only Linux and Windows are supported                                     ║
╚{'═' * 70}╝
""")
        raise NotImplementedError

    if authorized_keys.exists():
        split = "\n"
        keys_text = authorized_keys.read_text().split(split)
        key_count = len([k for k in keys_text if k.strip()])
        
        print(f"""
╭{'─' * 70}╮
│ 🔍 Current SSH authorization status                                      │
│ ✅ Found {key_count} authorized key(s)                                        │
╰{'─' * 70}╯
""")
        
        if path_to_key.read_text() in authorized_keys.read_text():
            print(f"""
╔{'═' * 70}╗
║ ⚠️  Key already authorized                                                ║
╠{'═' * 70}╣
║ Key: {path_to_key.name}
║ Status: Already present in authorized_keys file
║ No action required
╚{'═' * 70}╝
""")
            program = ""
        else:
            print(f"""
╭{'─' * 70}╮
│ ➕ Adding new SSH key to authorized keys                                 │
│ 🔑 Key file: {path_to_key.name}                                          │
╰{'─' * 70}╯
""")
            
            if system() == "Linux":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            elif system() == "Windows":
                program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
                program = program_path.expanduser().read_text()
                place_holder = r'$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"'
                assert place_holder in program, f"This section performs string manipulation on the script {program_path} to add the key to the authorized_keys file. The script has changed and the string {place_holder} is not found."
                program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')
                print(f"""
╭{'─' * 70}╮
│ 🔧 Configured PowerShell script for Windows                              │
│ 📝 Replaced placeholder with actual key path                             │
╰{'─' * 70}╯
""")
            else: raise NotImplementedError
    else:
        print(f"""
╭{'─' * 70}╮
│ 📝 Creating new authorized_keys file                                     │
│ 🔑 Using key: {path_to_key.name}                                         │
╰{'─' * 70}╯
""")
        
        if system() == "Linux":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
            program = P(program_path).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')
            print(f"""
╭{'─' * 70}╮
│ 🔧 Configured PowerShell script for Windows                              │
│ 📝 Set key path in script                                                │
╰{'─' * 70}╯
""")

    if system() == "Linux": 
        program += """

sudo chmod 700 ~/.ssh
sudo chmod 644 ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/*.pub
sudo service ssh --full-restart
# from superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder

"""
        print(f"""
╭{'─' * 70}╮
│ 🔒 Setting proper SSH permissions and restarting service                 │
╰{'─' * 70}╯
""")
        
    print(f"""
╔{'═' * 70}╗
║ ✅ SSH KEY CONFIGURATION PREPARED                                        ║
╚{'═' * 70}╝
""")
        
    return program


def main():
    print(f"""
╔{'═' * 70}╗
║ 🔐 SSH PUBLIC KEY AUTHORIZATION TOOL                                     ║
╚{'═' * 70}╝
""")
    
    print(f"""
╭{'─' * 70}╮
│ 🔍 Searching for public keys...                                          │
╰{'─' * 70}╯
""")
    
    pub_keys = P.home().joinpath(".ssh").search("*.pub")
    
    if pub_keys:
        print(f"""
╭{'─' * 70}╮
│ ✅ Found {len(pub_keys)} public key(s)                                           │
╰{'─' * 70}╯
""")
    else:
        print(f"""
╭{'─' * 70}╮
│ ⚠️  No public keys found                                                  │
╰{'─' * 70}╯
""")
    
    all_keys_option = f"all pub keys available ({len(pub_keys)})"
    i_have_path_option = "I have the path to the key file"
    i_paste_option = "I want to paste the key itself"
    
    res = display_options("Which public key to add? ", options=pub_keys.apply(str).list + [all_keys_option, i_have_path_option, i_paste_option])
    assert isinstance(res, str), f"Got {res} of type {type(res)} instead of str."
    
    if res == all_keys_option:
        print(f"""
╭{'─' * 70}╮
│ 🔄 Processing all {len(pub_keys)} public keys...                                  │
╰{'─' * 70}╯
""")
        program = "\n\n\n".join(pub_keys.apply(get_add_ssh_key_script))
    
    elif res == i_have_path_option:
        print(f"""
╭{'─' * 70}╮
│ 📂 Please provide the path to your public key                             │
╰{'─' * 70}╯
""")
        key_path = P(input("📋 Path: ")).expanduser().absolute()
        print(f"""
╭{'─' * 70}╮
│ 📄 Using key from path: {key_path}                        │
╰{'─' * 70}╯
""")
        program = get_add_ssh_key_script(key_path)
    
    elif res == i_paste_option:
        print(f"""
╭{'─' * 70}╮
│ 📋 Please provide a filename and paste the public key content             │
╰{'─' * 70}╯
""")
        key_filename = input("📝 File name (default: my_pasted_key.pub): ") or "my_pasted_key.pub"
        key_path = P.home().joinpath(f".ssh/{key_filename}")
        key_path.write_text(input("🔑 Paste the public key here: "))
        print(f"""
╭{'─' * 70}╮
│ 💾 Key saved to: {key_path}                           │
╰{'─' * 70}╯
""")
        program = get_add_ssh_key_script(key_path)
    
    else:
        print(f"""
╭{'─' * 70}╮
│ 🔑 Using selected key: {P(res).name}                                     │
╰{'─' * 70}╯
""")
        program = get_add_ssh_key_script(P(res))
    
    print(f"""
╔{'═' * 70}╗
║ 🚀 SSH KEY AUTHORIZATION READY                                           ║
║ Run the generated script to apply changes                                ║
╚{'═' * 70}╝
""")
    
    return program


if __name__ == '__main__':
    pass
