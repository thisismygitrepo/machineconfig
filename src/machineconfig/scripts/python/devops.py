"""devops with emojis"""

from machineconfig.utils.options import choose_from_options

from platform import system
from typing import Optional, Literal, TypeAlias
from rich.console import Console
from rich.panel import Panel

console = Console()

BOX_WIDTH = 150  # width for box drawing


Options: TypeAlias = Literal["🔄 UPDATE essential repos", "⚙️ DEVAPPS install", "🔗 SYMLINKS, SHELL PROFILE, FONT, TERMINAL SETTINGS.", "🆕 SYMLINKS new", "🔑 SSH add pub key to this machine", "🗝️ SSH add identity (private key) to this machine", "🔐 SSH use key pair to connect two machines", "📡 SSH setup", "🐧 SSH setup wsl", "💾 BACKUP", "📥 RETRIEVE", "⏰ SCHEDULER"]

options_list = list(Options.__args__)


def args_parser():
    import typer
    typer.run(main)


def main(which: Optional[Options] = None):
    # PathExtended(_program_PATH).delete(sure=True, verbose=False)
    console.print(Panel("🚀 Initializing DevOps operation...", width=BOX_WIDTH, border_style="blue"))
    options = options_list
    if which is None:
        try:
            choice_key = choose_from_options(msg="", options=options, header="🛠️ DEVOPS", default=options[0], multi=False, fzf=False)
        except KeyboardInterrupt:
            console.print(Panel("❌ Operation cancelled by user", title_align="left", border_style="red", width=BOX_WIDTH))
            return
    else:
        choice_key = which

    console.print(Panel(f"🔧 SELECTED OPERATION\n{choice_key}", title_align="left", border_style="green", width=BOX_WIDTH))

    if choice_key == "🔄 UPDATE essential repos":
        console.print(Panel("🔄 Updating essential repositories...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_update_repos as helper

        helper.main()
    elif choice_key == "⚙️ DEVAPPS install":
        console.print(Panel("⚙️  Installing development applications...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_devapps_install as helper

        helper.main(which=None)

    elif choice_key == "🆕 SYMLINKS new":
        console.print(Panel("🔄 Creating new symlinks...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.jobs.python.python_ve_symlink as helper

        helper.main()

    elif choice_key == "🔗 SYMLINKS, SHELL PROFILE, FONT, TERMINAL SETTINGS.":
        console.print(Panel("🔗 Setting up symlinks, PATH, and shell profile...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.profile.create as helper

        helper.main()
        "echo '✅ done with symlinks'"

    elif choice_key == "🔑 SSH add pub key to this machine":
        console.print(Panel("🔑 Adding public SSH key to this machine...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_add_ssh_key as helper

        helper.main()

    elif choice_key == "🔐 SSH use key pair to connect two machines":
        console.print(Panel("❌ ERROR: Not Implemented\nSSH key pair connection feature is not yet implemented", title_align="left", border_style="red", width=BOX_WIDTH))
        raise NotImplementedError

    elif choice_key == "🗝️ SSH add identity (private key) to this machine":  # so that you can SSH directly withuot pointing to identity key.
        console.print(Panel("🗝️  Adding SSH identity (private key) to this machine...", width=BOX_WIDTH, border_style="blue"))
        import machineconfig.scripts.python.devops_add_identity as helper

        helper.main()

    elif choice_key == "📡 SSH setup":
        console.print(Panel("📡 Setting up SSH...", width=BOX_WIDTH, border_style="blue"))
        _program_windows = """Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        _program_linux = """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        _program_linux if system() == "Linux" else _program_windows
        import subprocess

        subprocess.run(_program_linux if system() == "Linux" else _program_windows, shell=True, check=True)

    elif choice_key == "🐧 SSH setup wsl":
        console.print(Panel("🐧 Setting up SSH for WSL...", width=BOX_WIDTH, border_style="blue"))
        """curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == "💾 BACKUP":
        console.print(Panel("💾 Creating backup...", width=BOX_WIDTH, border_style="blue"))
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve

        main_backup_retrieve(direction="BACKUP")

    elif choice_key == "📥 RETRIEVE":
        console.print(Panel("📥 Retrieving backup...", width=BOX_WIDTH, border_style="blue"))
        from machineconfig.scripts.python.devops_backup_retrieve import main_backup_retrieve

        main_backup_retrieve(direction="RETRIEVE")

    elif choice_key == "⏰ SCHEDULER":
        console.print(Panel("⏰ Setting up scheduler...", width=BOX_WIDTH, border_style="blue"))
        # from machineconfig.scripts.python.scheduler import main as helper
        # helper()

    else:
        console.print(Panel("❌ ERROR: Invalid choice", title_align="left", border_style="red", width=BOX_WIDTH))
        raise ValueError(f"Unimplemented choice: {choice_key}")


if __name__ == "__main__":
    args_parser()
