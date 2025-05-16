from crocodile.file_management import P, Read
from crocodile.meta import Terminal
from machineconfig.scripts.python.get_zellij_cmd import get_zellij_cmd
from machineconfig.utils.utils import CONFIG_PATH, DEFAULTS_PATH
from machineconfig.utils.code import write_shell_script_to_file
import platform
from rich.console import Console
from rich.panel import Panel

console = Console()


def delete_remote_repo_copy_and_push_local(remote_repo: str, local_repo: str, cloud: str):
    console.print(Panel("🗑️  Deleting remote repo copy and pushing local copy", title="[bold blue]Repo Sync[/bold blue]", border_style="blue"))
    repo_sync_root = P(remote_repo).expanduser().absolute()
    repo_root_path = P(local_repo).expanduser().absolute()
    repo_sync_root.delete(sure=True)
    print("🧹 Removed temporary remote copy")
    from git.remote import Remote
    from git.repo import Repo
    try:
        Remote.remove(Repo(repo_root_path), "originEnc")
        print("🔗 Removed originEnc remote reference")
    except Exception: pass  # type: ignore
    print(f"""
╭{'─' * 150}╮
│ 📤 Uploading local repository to cloud...                                │
╰{'─' * 150}╯
""")

    repo_root_path.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, os_specific=False)

    console.print(Panel("✅ Repository successfully pushed to cloud", title="[bold green]Repo Sync[/bold green]", border_style="green"))


# import sys
# import subprocess


def get_wt_cmd(wd1: P, wd2: P) -> str:
    lines = [
        f"""wt --window 0 new-tab --profile pwsh --title "gitdiff" --tabColor `#3b04d1 --startingDirectory {wd1} ` --colorScheme "Solarized Dark" """,
        f"""split-pane --horizontal --profile pwsh --startingDirectory {wd2} --size 0.5 --colorScheme "Tango Dark" -- pwsh -Interactive """
    ]
    return " `; ".join(lines)


def inspect_repos(repo_local_root: str, repo_remote_root: str):
    console.print(Panel(f"📂 Local:  {repo_local_root}\\n📂 Remote: {repo_remote_root}", title="[bold blue]🔍 Inspecting Repositories[/bold blue]", border_style="blue"))

    if platform.system() == "Windows":
        program = get_wt_cmd(wd1=P(repo_local_root), wd2=P(repo_local_root))
        write_shell_script_to_file(program=program, execute=True, desc="Inspecting repos ...", preserve_cwd=True, display=True)
        return None
    elif platform.system() == "Linux":
        program = get_zellij_cmd(wd1=P(repo_local_root), wd2=P(repo_remote_root))
        write_shell_script_to_file(program=program, execute=True, desc="Inspecting repos ...", preserve_cwd=True, display=True)
        return None
    else: raise NotImplementedError(f"Platform {platform.system()} not implemented.")


def fetch_dotfiles():
    console.print(Panel("📁 Fetching Dotfiles", title="[bold blue]Dotfiles[/bold blue]", border_style="blue"))

    cloud_resolved = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
    print(f"""
╭{'─' * 150}╮
│ ⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}{' ' * (78 - len(f'│ ⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}'))}│
╰{'─' * 150}╯
""")

    dotfiles_local = P.home().joinpath("dotfiles")
    CONFIG_PATH.joinpath("remote").create()
    dotfiles_remote = CONFIG_PATH.joinpath("remote", dotfiles_local.rel2home())
    remote_path = dotfiles_local.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"

    print(f"""
╭{'─' * 150}╮
│ 📥 Downloading dotfiles from cloud...                                    │
╰{'─' * 150}╯
""")

    dotfiles_remote.from_cloud(remotepath=remote_path, cloud=cloud_resolved,
        unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=None)

    print(f"""
╭{'─' * 150}╮
│ 🗑️  Removing old dotfiles and replacing with cloud version...            │
╰{'─' * 150}╯
""")

    dotfiles_local.delete(sure=True)
    dotfiles_remote.move(folder=P.home())
    script = f"""
# rm -rf {dotfiles_local}
# mv {dotfiles_remote} {dotfiles_local}
"""
    if platform.system() == "Linux": script += """
sudo chmod 600 $HOME/.ssh/*
sudo chmod 700 $HOME/.ssh
sudo chmod +x $HOME/dotfiles/scripts/linux -R
"""
    shell_path = write_shell_script_to_file(shell_script=script)
    Terminal().run(f". {shell_path}", shell="bash").capture().print()

    console.print(Panel("✅ Dotfiles successfully fetched and installed", title="[bold green]Dotfiles[/bold green]", border_style="green"))

