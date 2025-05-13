"""BR: Backup and Retrieve
"""

# import subprocess
from crocodile.file_management import Read, P
from machineconfig.utils.utils import LIBRARY_ROOT, DEFAULTS_PATH, print_code, choose_cloud_interactively, choose_multiple_options
from machineconfig.scripts.python.helpers.helpers2 import ES
from platform import system
from typing import Any, Literal, Optional


OPTIONS = Literal["BACKUP", "RETRIEVE"]


def main_backup_retrieve(direction: OPTIONS, which: Optional[str] = None):
    try:
        cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        print(f"""
╔{'═' * 150}╗
║ ⚠️  DEFAULT CLOUD CONFIGURATION{' ' * (78 - len('║ ⚠️  DEFAULT CLOUD CONFIGURATION'))}║
╠{'═' * 150}╣
║ 🌥️  Using default cloud: {cloud}{' ' * (78 - len(f'║ 🌥️  Using default cloud: {cloud}'))}║
╚{'═' * 150}╝
""")
    except (FileNotFoundError, KeyError, IndexError):
        print(f"""
╔{'═' * 150}╗
║ 🔍 DEFAULT CLOUD NOT FOUND{' ' * (78 - len('║ 🔍 DEFAULT CLOUD NOT FOUND'))}║
║ 🔄 Please select a cloud configuration from the options below{' ' * (78 - len('║ 🔄 Please select a cloud configuration from the options below'))}║
╚{'═' * 150}╝
""")
        cloud = choose_cloud_interactively()

    bu_file: dict[str, Any] = Read.toml(LIBRARY_ROOT.joinpath("profile/backup.toml"))
    
    print(f"""
╔{'═' * 150}╗
║ 🧰 LOADING BACKUP CONFIGURATION                                         ║
║ 📄 File: {LIBRARY_ROOT.joinpath("profile/backup.toml")}      ║
╚{'═' * 150}╝
""")
    
    if system() == "Linux": 
        bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
        print(f"""
╔{'═' * 150}╗
║ 🐧 LINUX ENVIRONMENT DETECTED                                           ║
║ 🔍 Filtering out Windows-specific entries                               ║
║ ✅ Found {len(bu_file)} applicable backup configuration entries               ╚{'═' * 150}╝
""")
    elif system() == "Windows": 
        bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}
        print(f"""
╔{'═' * 150}╗
║ 🪟 WINDOWS ENVIRONMENT DETECTED                                         ║
║ 🔍 Filtering out Linux-specific entries                                 ║
║ ✅ Found {len(bu_file)} applicable backup configuration entries               ╚{'═' * 150}╝
""")

    if which is None:
        print(f"""
╔{'═' * 150}╗
║ 🔍 SELECT {direction} ITEMS                                             ║
║ 📋 Choose which configuration entries to process                         ║
╚{'═' * 150}╝
""")
        choices = choose_multiple_options(msg=f"WHICH FILE of the following do you want to {direction}?", options=['all'] + list(bu_file.keys()))
    else:
        choices = which.split(",") if isinstance(which, str) else which
        print(f"""
╔{'═' * 150}╗
║ 🔖 PRE-SELECTED ITEMS{' ' * (78 - len('║ 🔖 PRE-SELECTED ITEMS'))}║
║ 📝 Using: {', '.join(choices)}{' ' * (78 - len(f'║ 📝 Using: {", ".join(choices)}'))}║
╚{'═' * 150}╝
""")

    if "all" in choices:
        items = bu_file
        print(f"""
╔{'═' * 150}╗
║ 📋 PROCESSING ALL ENTRIES{' ' * (78 - len('║ 📋 PROCESSING ALL ENTRIES'))}║
║ 🔢 Total entries to process: {len(bu_file)}{' ' * (78 - len(f'║ 🔢 Total entries to process: {len(bu_file)}'))}║
╚{'═' * 150}╝
""")
    else:
        items = {key: val for key, val in bu_file.items() if key in choices}
        print(f"""
╔{'═' * 150}╗
║ 📋 PROCESSING SELECTED ENTRIES                                          ║
║ 🔢 Total entries to process: {len(items):<39} ║
╚{'═' * 150}╝
""")

    program = f"""$cloud = "{cloud}:{ES}" \n """ if system() == "Windows" else f"""cloud="{cloud}:{ES}" \n """
    
    print(f"""
╔{'═' * 150}╗
║ 🚀 GENERATING {direction} SCRIPT                                        ║
╠{'═' * 150}╣
║ 🌥️  Cloud: {cloud:<58} ║
║ 🗂️  Items: {len(items):<58} ║
╚{'═' * 150}╝
""")
    
    for item_name, item in items.items():
        flags = ''
        flags += 'z' if item['zip'] == 'True' else ''
        flags += 'e' if item['encrypt'] == 'True' else ''
        flags += 'r' if item['rel2home'] == 'True' else ''
        flags += 'o' if system().lower() in item_name else ''
        
        print(f"""
╔{'─' * 150}╗
║ 📦 PROCESSING: {item_name:<53} ║
╠{'─' * 150}╣
║ 📂 Path: {P(item['path']).as_posix():<55} ║
║ 🏳️  Flags: {flags or 'None':<56} ║
╚{'─' * 150}╝
""")
        
        if flags: flags = "-" + flags
        if direction == "BACKUP": 
            program += f"""\ncloud_copy "{P(item['path']).as_posix()}" $cloud {flags}\n"""
        elif direction == "RETRIEVE": 
            program += f"""\ncloud_copy $cloud "{P(item['path']).as_posix()}" {flags}\n"""
        else:
            print(f"""
╔{'═' * 150}╗
║ ❌ ERROR: INVALID DIRECTION                                            ║
║ ⚠️  Direction must be either "BACKUP" or "RETRIEVE"                     ║
╚{'═' * 150}╝
""")
            raise RuntimeError(f"Unknown direction: {direction}")
            
        if item_name == "dotfiles" and system() == "Linux": 
            program += """\nchmod 700 ~/.ssh/*\n"""
            print(f"""
╔{'─' * 150}╗
║ 🔒 SPECIAL HANDLING: SSH PERMISSIONS                                    ║
║ 🛠️  Setting secure permissions for SSH files                            ║
║ 📝 Command: chmod 700 ~/.ssh/*                                          ║
╚{'─' * 150}╝
""")
            
    print_code(program, lexer="shell", desc=f"{direction} script")
    
    print(f"""
╔{'═' * 150}╗
║ ✅ {direction} SCRIPT GENERATION COMPLETE                               ║
║ 🚀 Ready to execute the operations                                      ║
╚{'═' * 150}╝
""")
    
    return program


def main(direction: OPTIONS, which: Optional[str] = None):
    print(f"""
╔{'═' * 150}╗
║ 🔄 {direction} OPERATION STARTED                                        ║
║ ⏱️  {'-' * 58} ║
╚{'═' * 150}╝
""")
    
    code = main_backup_retrieve(direction=direction, which=which)
    from machineconfig.utils.utils import write_shell_script_to_default_program_path
    
    print(f"""
╔{'═' * 150}╗
║ 💾 GENERATING SHELL SCRIPT                                             ║
║ 📄 Filename: backup_retrieve.sh                                         ║
╚{'═' * 150}╝
""")
    
    write_shell_script_to_default_program_path(program=code, desc="backup_retrieve.sh")


if __name__ == "__main__":
    pass
