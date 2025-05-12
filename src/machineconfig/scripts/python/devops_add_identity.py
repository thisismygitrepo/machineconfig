"""ID
"""


# from platform import system
from crocodile.file_management import P
from machineconfig.utils.options import display_options

BOX_WIDTH = 150  # width for box drawing


def main():
    title = "🔑 SSH IDENTITY MANAGEMENT"
    print(f"""{title.center(BOX_WIDTH, "=")}""")
    
    print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔍 Searching for existing SSH keys...{' ' * (BOX_WIDTH - len("🔍 Searching for existing SSH keys..."))}│
╰{'─' * BOX_WIDTH}╯
""")
    
    private_keys = P.home().joinpath(".ssh").search("*.pub").apply(lambda x: x.with_name(x.stem)).filter(lambda x: x.exists())
    
    if private_keys:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ ✅ Found {len(private_keys)} SSH private key(s){' ' * (BOX_WIDTH - len(f"✅ Found {len(private_keys)} SSH private key(s)"))}│
╰{'─' * BOX_WIDTH}╯
""")
    else:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ ⚠️  No SSH private keys found{' ' * (BOX_WIDTH - len("⚠️  No SSH private keys found"))}│
╰{'─' * BOX_WIDTH}╯
""")
        
    choice = display_options(msg="Path to private key to be used when ssh'ing: ", options=private_keys.apply(str).list + ["I have the path to the key file", "I want to paste the key itself"])
    
    if choice == "I have the path to the key file":
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📄 Please enter the path to your private key file{' ' * (BOX_WIDTH - len("📄 Please enter the path to your private key file"))}│
╰{'─' * BOX_WIDTH}╯
""")
        path_to_key = P(input("📋 Input path here: ")).expanduser().absolute()
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📂 Using key from custom path: {path_to_key}{' ' * (BOX_WIDTH - len(f"📂 Using key from custom path: {path_to_key}"))}│
╰{'─' * BOX_WIDTH}╯
""")
        
    elif choice == "I want to paste the key itself":
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📋 Please provide a filename and paste the private key content{' ' * (BOX_WIDTH - len("📋 Please provide a filename and paste the private key content"))}│
╰{'─' * BOX_WIDTH}╯
""")
        key_filename = input("📝 File name (default: my_pasted_key): ") or "my_pasted_key"
        path_to_key = P.home().joinpath(f".ssh/{key_filename}").write_text(input("🔑 Paste the private key here: "))
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 💾 Key saved to: {path_to_key}{' ' * (BOX_WIDTH - len(f"💾 Key saved to: {path_to_key}"))}│
╰{'─' * BOX_WIDTH}╯
""")
        
    elif isinstance(choice, str): 
        path_to_key = P(choice)
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔑 Using selected key: {path_to_key.name}{' ' * (BOX_WIDTH - len(f"🔑 Using selected key: {path_to_key.name}"))}│
╰{'─' * BOX_WIDTH}╯
""")
        
    else: 
        print(f"""
╔{'═' * BOX_WIDTH}╗
║ ❌ ERROR: Invalid choice{' ' * (BOX_WIDTH - len("❌ ERROR: Invalid choice"))}║
║ The selected option is not supported: {choice}{' ' * (BOX_WIDTH - len(f"The selected option is not supported: {choice}"))}║
╚{'═' * BOX_WIDTH}╝
""")
        raise NotImplementedError(f"Choice {choice} not supported")
    
    txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"  # adds this id for all connections, no host specified.
    config_path = P.home().joinpath(".ssh/config")
    
    print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📝 Updating SSH configuration...{' ' * (BOX_WIDTH - len("📝 Updating SSH configuration..."))}│
╰{'─' * BOX_WIDTH}╯
""")
    
    if config_path.exists(): 
        config_path.modify_text(txt_search=txt, txt_alt=txt, replace_line=True, notfound_append=True, prepend=True)  # note that Identity line must come on top of config file otherwise it won't work, hence `prepend=True`
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ ✏️  Updated existing SSH config file{' ' * (BOX_WIDTH - len("✏️  Updated existing SSH config file"))}│
╰{'─' * BOX_WIDTH}╯
""")
    else: 
        config_path.write_text(txt)
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📄 Created new SSH config file{' ' * (BOX_WIDTH - len("📄 Created new SSH config file"))}│
╰{'─' * BOX_WIDTH}╯
""")
    
    program = f"""echo '
╔{'═' * BOX_WIDTH}╗
║ ✅ SSH IDENTITY CONFIGURATION COMPLETE{' ' * (BOX_WIDTH - len("✅ SSH IDENTITY CONFIGURATION COMPLETE"))}║
╠{'═' * BOX_WIDTH}╣
║ Identity added to SSH config file{' ' * (BOX_WIDTH - len("Identity added to SSH config file"))}║
║ Consider reloading the SSH config to apply changes{' ' * (BOX_WIDTH - len("Consider reloading the SSH config to apply changes"))}║
╚{'═' * BOX_WIDTH}╝
'"""
    
    print(f"""
╔{'═' * BOX_WIDTH}╗
║ 🎉 CONFIGURATION SUCCESSFUL{' ' * (BOX_WIDTH - len("🎉 CONFIGURATION SUCCESSFUL"))}║
╠{'═' * BOX_WIDTH}╣
║ Identity added: {path_to_key.name}{' ' * (BOX_WIDTH - len(f"Identity added: {path_to_key.name}"))}║
║ Config file: {config_path}{' ' * (BOX_WIDTH - len(f"Config file: {config_path}"))}║
╚{'═' * BOX_WIDTH}╝
""")
    
    return program


if __name__ == '__main__':
    pass
