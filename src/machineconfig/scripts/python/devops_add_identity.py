"""ID
"""


# from platform import system
from crocodile.file_management import P
from machineconfig.utils.utils_options import display_options


def main():
    print(f"""
╔{'═' * 70}╗
║ 🔑 SSH IDENTITY MANAGEMENT                                               ║
╚{'═' * 70}╝
""")
    
    print(f"""
╭{'─' * 70}╮
│ 🔍 Searching for existing SSH keys...                                    │
╰{'─' * 70}╯
""")
    
    private_keys = P.home().joinpath(".ssh").search("*.pub").apply(lambda x: x.with_name(x.stem)).filter(lambda x: x.exists())
    
    if private_keys:
        print(f"""
╭{'─' * 70}╮
│ ✅ Found {len(private_keys)} SSH private key(s)                                    │
╰{'─' * 70}╯
""")
    else:
        print(f"""
╭{'─' * 70}╮
│ ⚠️  No SSH private keys found                                             │
╰{'─' * 70}╯
""")
        
    choice = display_options(msg="Path to private key to be used when ssh'ing: ", options=private_keys.apply(str).list + ["I have the path to the key file", "I want to paste the key itself"])
    
    if choice == "I have the path to the key file":
        print(f"""
╭{'─' * 70}╮
│ 📄 Please enter the path to your private key file                         │
╰{'─' * 70}╯
""")
        path_to_key = P(input("📋 Input path here: ")).expanduser().absolute()
        print(f"""
╭{'─' * 70}╮
│ 📂 Using key from custom path: {path_to_key}              │
╰{'─' * 70}╯
""")
        
    elif choice == "I want to paste the key itself":
        print(f"""
╭{'─' * 70}╮
│ 📋 Please provide a filename and paste the private key content            │
╰{'─' * 70}╯
""")
        key_filename = input("📝 File name (default: my_pasted_key): ") or "my_pasted_key"
        path_to_key = P.home().joinpath(f".ssh/{key_filename}").write_text(input("🔑 Paste the private key here: "))
        print(f"""
╭{'─' * 70}╮
│ 💾 Key saved to: {path_to_key}                           │
╰{'─' * 70}╯
""")
        
    elif isinstance(choice, str): 
        path_to_key = P(choice)
        print(f"""
╭{'─' * 70}╮
│ 🔑 Using selected key: {path_to_key.name}                                 │
╰{'─' * 70}╯
""")
        
    else: 
        print(f"""
╔{'═' * 70}╗
║ ❌ ERROR: Invalid choice                                                 ║
║ The selected option is not supported: {choice}                           ║
╚{'═' * 70}╝
""")
        raise NotImplementedError(f"Choice {choice} not supported")
    
    txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"  # adds this id for all connections, no host specified.
    config_path = P.home().joinpath(".ssh/config")
    
    print(f"""
╭{'─' * 70}╮
│ 📝 Updating SSH configuration...                                          │
╰{'─' * 70}╯
""")
    
    if config_path.exists(): 
        config_path.modify_text(txt_search=txt, txt_alt=txt, replace_line=True, notfound_append=True, prepend=True)  # note that Identity line must come on top of config file otherwise it won't work, hence `prepend=True`
        print(f"""
╭{'─' * 70}╮
│ ✏️  Updated existing SSH config file                                       │
╰{'─' * 70}╯
""")
    else: 
        config_path.write_text(txt)
        print(f"""
╭{'─' * 70}╮
│ 📄 Created new SSH config file                                            │
╰{'─' * 70}╯
""")
    
    program = f"""echo '
╔{'═' * 70}╗
║ ✅ SSH IDENTITY CONFIGURATION COMPLETE                                   ║
╠{'═' * 70}╣
║ Identity added to SSH config file                                        ║
║ Consider reloading the SSH config to apply changes                       ║
╚{'═' * 70}╝
'"""
    
    print(f"""
╔{'═' * 70}╗
║ 🎉 CONFIGURATION SUCCESSFUL                                              ║
╠{'═' * 70}╣
║ Identity added: {path_to_key.name}                                       
║ Config file: {config_path}                                
╚{'═' * 70}╝
""")
    
    return program


if __name__ == '__main__':
    pass
