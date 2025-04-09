"""devops with emojis
"""

from machineconfig.utils.utils import display_options, PROGRAM_PATH, write_shell_script_to_default_program_path
from platform import system
from enum import Enum
from typing import Optional


class Options(Enum):
    update         = '🔄 UPDATE essential repos'
    cli_install    = '⚙️ DEVAPPS install'
    ve             = '🐍 VE install'
    sym_path_shell = '🔗 SYMLINKS, PATH & SHELL PROFILE'
    sym_new        = '🆕 SYMLINKS new'
    ssh_add_pubkey = '🔑 SSH add pub key to this machine'
    ssh_add_id     = '🗝️ SSH add identity (private key) to this machine'
    ssh_use_pair   = '🔐 SSH use key pair to connect two machines'
    ssh_setup      = '📡 SSH setup'
    ssh_setup_wsl  = '🐧 SSH setup wsl'
    dot_files_sync = '🔗 DOTFILES sync'
    backup         = '💾 BACKUP'
    retreive       = '📥 RETRIEVE'
    scheduler      = '⏰ SCHEDULER'


def args_parser():
    print(f"""
╔{'═' * 70}╗
║ 🛠️  DevOps Tool Suite                                                    ║
╚{'═' * 70}╝
""")
    
    import argparse
    parser = argparse.ArgumentParser()
    new_line = "\n\n"
    parser.add_argument("-w", "--which", help=f"""which option to run\nChoose one of those:\n{new_line.join([f"{item.name}: {item.value}" for item in list(Options)])}""", type=str, default=None)  # , choices=[op.value for op in Options]
    args = parser.parse_args()
    main(which=args.which)


def main(which: Optional[str] = None):
    PROGRAM_PATH.delete(sure=True, verbose=False)
    print(f"""
╭{'─' * 70}╮
│ 🚀 Initializing DevOps operation...                                      │
╰{'─' * 70}╯
""")
    
    options = [op.value for op in Options]
    if which is None:
        try:
            choice_key = display_options(msg="", options=options, header="🛠️ DEVOPS", default=options[0])
        except KeyboardInterrupt:
            print(f"""
╔{'═' * 70}╗
║ ❌ Operation cancelled by user                                           ║
╚{'═' * 70}╝
""")
            return
    else: choice_key = Options[which].value

    print(f"""
╔{'═' * 70}╗
║ 🔧 SELECTED OPERATION                                                    ║
╠{'═' * 70}╣
║ {choice_key.center(68)} ║
╚{'═' * 70}╝
""")

    if choice_key == Options.update.value:
        print(f"""
╭{'─' * 70}╮
│ 🔄 Updating essential repositories...                                    │
╰{'─' * 70}╯
""")
        import machineconfig.scripts.python.devops_update_repos as helper
        program = helper.main()

    elif choice_key == Options.ve.value:
        print(f"""
╭{'─' * 70}╮
│ 🐍 Setting up virtual environment...                                     │
╰{'─' * 70}╯
""")
        from machineconfig.utils.ve import get_ve_install_script
        program = get_ve_install_script()

    elif choice_key == Options.cli_install.value:
        print(f"""
╭{'─' * 70}╮
│ ⚙️  Installing development applications...                                │
╰{'─' * 70}╯
""")
        import machineconfig.scripts.python.devops_devapps_install as helper
        program = helper.main()

    elif choice_key == Options.sym_new.value:
        print(f"""
╭{'─' * 70}╮
│ 🔄 Creating new symlinks...                                              │
╰{'─' * 70}╯
""")
        import machineconfig.jobs.python.python_ve_symlink as helper
        program = helper.main()

    elif choice_key == Options.sym_path_shell.value:
        print(f"""
╭{'─' * 70}╮
│ 🔗 Setting up symlinks, PATH, and shell profile...                       │
╰{'─' * 70}╯
""")
        import machineconfig.profile.create as helper
        helper.main()
        program = "echo '✅ done with symlinks'"

    elif choice_key == Options.ssh_add_pubkey.value:
        print(f"""
╭{'─' * 70}╮
│ 🔑 Adding public SSH key to this machine...                              │
╰{'─' * 70}╯
""")
        import machineconfig.scripts.python.devops_add_ssh_key as helper
        program = helper.main()

    elif choice_key == Options.ssh_use_pair.value:
        print(f"""
╔{'═' * 70}╗
║ ❌ ERROR: Not Implemented                                                ║
║ SSH key pair connection feature is not yet implemented                   ║
╚{'═' * 70}╝
""")
        raise NotImplementedError

    elif choice_key == Options.ssh_add_id.value:  # so that you can SSH directly withuot pointing to identity key.
        print(f"""
╭{'─' * 70}╮
│ 🗝️  Adding SSH identity (private key) to this machine...                  │
╰{'─' * 70}╯
""")
        import machineconfig.scripts.python.devops_add_identity as helper
        program = helper.main()

    elif choice_key == Options.ssh_setup.value:
        print(f"""
╭{'─' * 70}╮
│ 📡 Setting up SSH...                                                     │
╰{'─' * 70}╯
""")
        program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == Options.ssh_setup_wsl.value:
        print(f"""
╭{'─' * 70}╮
│ 🐧 Setting up SSH for WSL...                                             │
╰{'─' * 70}╯
""")
        program = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == Options.backup.value:
        print(f"""
╭{'─' * 70}╮
│ 💾 Creating backup...                                                    │
╰{'─' * 70}╯
""")
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve as helper
        program = helper(direction="BACKUP")
        
    elif choice_key == Options.retreive.value:
        print(f"""
╭{'─' * 70}╮
│ 📥 Retrieving backup...                                                  │
╰{'─' * 70}╯
""")
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve as helper
        program = helper(direction="RETRIEVE")

    elif choice_key == Options.scheduler.value:
        print(f"""
╭{'─' * 70}╮
│ ⏰ Setting up scheduler...                                               │
╰{'─' * 70}╯
""")
        from machineconfig.scripts.python.scheduler import main as helper
        program = helper()

    elif choice_key == Options.dot_files_sync.value:
        print(f"""
╭{'─' * 70}╮
│ 🔗 Synchronizing dotfiles...                                             │
╰{'─' * 70}╯
""")
        from machineconfig.scripts.python.cloud_repo_sync import main as helper, P
        program = helper(cloud=None, path=str(P.home() / "dotfiles"), pwd=None, action="ask")

    else: 
        print(f"""
╔{'═' * 70}╗
║ ❌ ERROR: Invalid choice                                                 ║
║ The selected operation is not implemented: {choice_key}                  
╚{'═' * 70}╝
""")
        raise ValueError(f"Unimplemented choice: {choice_key}")
        
    if program:
        print(f"""
╭{'─' * 70}╮
│ 📜 Preparing shell script...                                             │
╰{'─' * 70}╯
""")
        write_shell_script_to_default_program_path(program=program, display=True, preserve_cwd=True, desc="🔧 Shell script prepared by Python.", execute=True if which is not None else False)
    else: 
        write_shell_script_to_default_program_path(program="echo '✨ Done.'", display=False, desc="🔧 Shell script prepared by Python.", preserve_cwd=True, execute=False)



if __name__ == "__main__":
    args_parser()
