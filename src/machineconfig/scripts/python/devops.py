"""devops with emojis
"""

from machineconfig.utils.utils import display_options, PROGRAM_PATH, write_shell_script_to_default_program_path
from platform import system
from enum import Enum
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich import box # Import box

console = Console()

BOX_WIDTH = 150  # width for box drawing


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
╔{'═' * BOX_WIDTH}╗
║ 🛠️  DevOps Tool Suite{' ' * (BOX_WIDTH - len('🛠️  DevOps Tool Suite'))}║
╚{'═' * BOX_WIDTH}╝
""")
    
    import argparse
    parser = argparse.ArgumentParser()
    new_line = "\n\n"
    parser.add_argument("-w", "--which", help=f"""which option to run\nChoose one of those:\n{new_line.join([f"{item.name}: {item.value}" for item in list(Options)])}""", type=str, default=None)  # , choices=[op.value for op in Options]
    args = parser.parse_args()
    main(which=args.which)


def display_title(title):
    console.print(Panel(title, box=box.DOUBLE_EDGE, title_align="left")) # Replace print with Panel

def display_task_title(title):
    console.print(Panel(title, box=box.ROUNDED, title_align="left")) # Replace print with Panel

def display_task_status(status):
    console.print(Panel(status, box=box.ROUNDED, title_align="left")) # Replace print with Panel

def display_task_result(result):
    console.print(Panel(result, box=box.ROUNDED, title_align="left")) # Replace print with Panel

def display_task_error(error):
    console.print(Panel(error, box=box.ROUNDED, border_style="red", title_align="left")) # Replace print with Panel

def display_task_warning(warning):
    console.print(Panel(warning, box=box.ROUNDED, border_style="yellow", title_align="left")) # Replace print with Panel

def display_task_success(success):
    console.print(Panel(success, box=box.ROUNDED, border_style="green", title_align="left")) # Replace print with Panel


def main(which: Optional[str] = None):
    PROGRAM_PATH.delete(sure=True, verbose=False)
    print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🚀 Initializing DevOps operation...{' ' * (BOX_WIDTH - len('│ 🚀 Initializing DevOps operation...'))}│
╰{'─' * BOX_WIDTH}╯
""")
    
    options = [op.value for op in Options]
    if which is None:
        try:
            choice_key = display_options(msg="", options=options, header="🛠️ DEVOPS", default=options[0])
        except KeyboardInterrupt:
            print(f"""
╔{'═' * BOX_WIDTH}╗
║ ❌ Operation cancelled by user{' ' * (BOX_WIDTH - len('║ ❌ Operation cancelled by user'))}║
╚{'═' * BOX_WIDTH}╝
""")
            return
    else: choice_key = Options[which].value

    print(f"""
╔{'═' * BOX_WIDTH}╗
║ 🔧 SELECTED OPERATION{' ' * (BOX_WIDTH - len('║ 🔧 SELECTED OPERATION'))}║
╠{'═' * BOX_WIDTH}╣
║ {choice_key.center(BOX_WIDTH-4)} ║
╚{'═' * BOX_WIDTH}╝
""")

    if choice_key == Options.update.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔄 Updating essential repositories...{' ' * (BOX_WIDTH - len('│ 🔄 Updating essential repositories...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        import machineconfig.scripts.python.devops_update_repos as helper
        program = helper.main()

    elif choice_key == Options.ve.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🐍 Setting up virtual environment...{' ' * (BOX_WIDTH - len('│ 🐍 Setting up virtual environment...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        from machineconfig.utils.ve import get_ve_install_script
        program = get_ve_install_script()

    elif choice_key == Options.cli_install.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ ⚙️  Installing development applications...{' ' * (BOX_WIDTH - len('│ ⚙️  Installing development applications...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        import machineconfig.scripts.python.devops_devapps_install as helper
        program = helper.main()

    elif choice_key == Options.sym_new.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔄 Creating new symlinks...{' ' * (BOX_WIDTH - len('│ 🔄 Creating new symlinks...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        import machineconfig.jobs.python.python_ve_symlink as helper
        program = helper.main()

    elif choice_key == Options.sym_path_shell.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔗 Setting up symlinks, PATH, and shell profile...{' ' * (BOX_WIDTH - len('│ 🔗 Setting up symlinks, PATH, and shell profile...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        import machineconfig.profile.create as helper
        helper.main()
        program = "echo '✅ done with symlinks'"

    elif choice_key == Options.ssh_add_pubkey.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔑 Adding public SSH key to this machine...{' ' * (BOX_WIDTH - len('│ 🔑 Adding public SSH key to this machine...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        import machineconfig.scripts.python.devops_add_ssh_key as helper
        program = helper.main()

    elif choice_key == Options.ssh_use_pair.value:
        print(f"""
╔{'═' * BOX_WIDTH}╗
║ ❌ ERROR: Not Implemented{' ' * (BOX_WIDTH - len('║ ❌ ERROR: Not Implemented'))}║
║ SSH key pair connection feature is not yet implemented{' ' * (BOX_WIDTH - len('║ SSH key pair connection feature is not yet implemented'))}║
╚{'═' * BOX_WIDTH}╝
""")
        raise NotImplementedError

    elif choice_key == Options.ssh_add_id.value:  # so that you can SSH directly withuot pointing to identity key.
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🗝️  Adding SSH identity (private key) to this machine...{' ' * (BOX_WIDTH - len('│ 🗝️  Adding SSH identity (private key) to this machine...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        import machineconfig.scripts.python.devops_add_identity as helper
        program = helper.main()

    elif choice_key == Options.ssh_setup.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📡 Setting up SSH...{' ' * (BOX_WIDTH - len('│ 📡 Setting up SSH...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == Options.ssh_setup_wsl.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🐧 Setting up SSH for WSL...{' ' * (BOX_WIDTH - len('│ 🐧 Setting up SSH for WSL...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        program = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == Options.backup.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 💾 Creating backup...{' ' * (BOX_WIDTH - len('│ 💾 Creating backup...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve as helper
        program = helper(direction="BACKUP")
        
    elif choice_key == Options.retreive.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📥 Retrieving backup...{' ' * (BOX_WIDTH - len('│ 📥 Retrieving backup...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve as helper
        program = helper(direction="RETRIEVE")

    elif choice_key == Options.scheduler.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ ⏰ Setting up scheduler...{' ' * (BOX_WIDTH - len('│ ⏰ Setting up scheduler...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        from machineconfig.scripts.python.scheduler import main as helper
        program = helper()

    elif choice_key == Options.dot_files_sync.value:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 🔗 Synchronizing dotfiles...{' ' * (BOX_WIDTH - len('│ 🔗 Synchronizing dotfiles...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        from machineconfig.scripts.python.cloud_repo_sync import main as helper, P
        program = helper(cloud=None, path=str(P.home() / "dotfiles"), pwd=None, action="ask")

    else: 
        print(f"""
╔{'═' * BOX_WIDTH}╗
║ ❌ ERROR: Invalid choice{' ' * (BOX_WIDTH - len('║ ❌ ERROR: Invalid choice'))}║
║ The selected operation is not implemented: {choice_key}{' ' * (BOX_WIDTH - len(f'║ The selected operation is not implemented: {choice_key}'))}║
╚{'═' * BOX_WIDTH}╝
""")
        raise ValueError(f"Unimplemented choice: {choice_key}")
        
    if program:
        print(f"""
╭{'─' * BOX_WIDTH}╮
│ 📜 Preparing shell script...{' ' * (BOX_WIDTH - len('│ 📜 Preparing shell script...'))}│
╰{'─' * BOX_WIDTH}╯
""")
        write_shell_script_to_default_program_path(program=program, display=True, preserve_cwd=True, desc="🔧 Shell script prepared by Python.", execute=True if which is not None else False)
    else: 
        write_shell_script_to_default_program_path(program="echo '✨ Done.'", display=False, desc="🔧 Shell script prepared by Python.", preserve_cwd=True, execute=False)



if __name__ == "__main__":
    args_parser()
