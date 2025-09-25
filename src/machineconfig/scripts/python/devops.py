"""devops with emojis"""

from machineconfig.utils.options import display_options

from platform import system
from enum import Enum
from typing import Optional
from rich.console import Console
from rich.panel import Panel

console = Console()

BOX_WIDTH = 150  # width for box drawing


class Options(Enum):
    update = "🔄 UPDATE essential repos"
    cli_install = "⚙️ DEVAPPS install"
    sym_path_shell = "🔗 SYMLINKS, SHELL PROFILE, FONT, TERMINAL SETTINGS."
    sym_new = "🆕 SYMLINKS new"
    ssh_add_pubkey = "🔑 SSH add pub key to this machine"
    ssh_add_id = "🗝️ SSH add identity (private key) to this machine"
    ssh_use_pair = "🔐 SSH use key pair to connect two machines"
    ssh_setup = "📡 SSH setup"
    ssh_setup_wsl = "🐧 SSH setup wsl"
    backup = "💾 BACKUP"
    retreive = "📥 RETRIEVE"
    scheduler = "⏰ SCHEDULER"


def args_parser():
    console.print(Panel("🛠️  DevOps Tool Suite", title_align="left", border_style="blue", width=BOX_WIDTH))
    import argparse

    parser = argparse.ArgumentParser()
    new_line = "\n\n"
    parser.add_argument("-w", "--which", help=f"""which option to run\nChoose one of those:\n{new_line.join([f"{item.name}: {item.value}" for item in list(Options)])}""", type=str, default=None)  # , choices=[op.value for op in Options]
    args = parser.parse_args()
    main(which=args.which)


def main(which: Optional[str] = None):
    # PathExtended(_program_PATH).delete(sure=True, verbose=False)
    console.print(Panel("🚀 Initializing DevOps operation...", width=BOX_WIDTH, border_style="blue"))
    options = [op.value for op in Options]
    if which is None:
        try:
            choice_key = display_options(msg="", options=options, header="🛠️ DEVOPS", default=options[0])
        except KeyboardInterrupt:
            console.print(Panel("❌ Operation cancelled by user", title_align="left", border_style="red", width=BOX_WIDTH))
            return
    else:
        choice_key = Options[which].value

    console.print(Panel(f"🔧 SELECTED OPERATION\n{choice_key}", title_align="left", border_style="green", width=BOX_WIDTH))

    if choice_key == Options.update.value:
        console.print(Panel("🔄 Updating essential repositories...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_update_repos as helper

        helper.main()
    elif choice_key == Options.cli_install.value:
        console.print(Panel("⚙️  Installing development applications...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_devapps_install as helper
        helper.main(which=None)

    elif choice_key == Options.sym_new.value:
        console.print(Panel("🔄 Creating new symlinks...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.jobs.python.python_ve_symlink as helper

        helper.main()

    elif choice_key == Options.sym_path_shell.value:
        console.print(Panel("🔗 Setting up symlinks, PATH, and shell profile...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.profile.create as helper

        helper.main()
        "echo '✅ done with symlinks'"

    elif choice_key == Options.ssh_add_pubkey.value:
        console.print(Panel("🔑 Adding public SSH key to this machine...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_add_ssh_key as helper

        helper.main()

    elif choice_key == Options.ssh_use_pair.value:
        console.print(Panel("❌ ERROR: Not Implemented\nSSH key pair connection feature is not yet implemented", title_align="left", border_style="red", width=BOX_WIDTH))
        raise NotImplementedError

    elif choice_key == Options.ssh_add_id.value:  # so that you can SSH directly withuot pointing to identity key.
        console.print(Panel("🗝️  Adding SSH identity (private key) to this machine...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_add_identity as helper

        helper.main()

    elif choice_key == Options.ssh_setup.value:
        console.print(Panel("📡 Setting up SSH...", width=BOX_WIDTH, border_style="blue"))
        _program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        _program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        _program_linux if system() == "Linux" else _program_windows
        import subprocess

        subprocess.run(_program_linux if system() == "Linux" else _program_windows, shell=True, check=True)

    elif choice_key == Options.ssh_setup_wsl.value:
        console.print(Panel("🐧 Setting up SSH for WSL...", width=BOX_WIDTH, border_style="blue"))
        """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == Options.backup.value:
        console.print(Panel("💾 Creating backup...", width=BOX_WIDTH, border_style="blue"))
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve

        main_backup_retrieve(direction="BACKUP")

    elif choice_key == Options.retreive.value:
        console.print(Panel("📥 Retrieving backup...", width=BOX_WIDTH, border_style="blue"))
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve

        main_backup_retrieve(direction="RETRIEVE")

    elif choice_key == Options.scheduler.value:
        console.print(Panel("⏰ Setting up scheduler...", width=BOX_WIDTH, border_style="blue"))
        # from machineconfig.scripts.python.scheduler import main as helper
        # helper()

    else:
        console.print(Panel("❌ ERROR: Invalid choice", title_align="left", border_style="red", width=BOX_WIDTH))
        raise ValueError(f"Unimplemented choice: {choice_key}")


if __name__ == "__main__":
    args_parser()
