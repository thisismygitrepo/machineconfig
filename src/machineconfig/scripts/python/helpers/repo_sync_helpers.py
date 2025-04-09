
from crocodile.file_management import P, Read
from crocodile.meta import Terminal
from machineconfig.scripts.python.get_zellij_cmd import get_zellij_cmd
from machineconfig.utils.utils import CONFIG_PATH, DEFAULTS_PATH, get_shell_script, write_shell_script
import platform


def delete_remote_repo_copy_and_push_local(remote_repo: str, local_repo: str, cloud: str):
    print(f"""
╔{'═' * 70}╗
║ 🗑️  Deleting remote repo copy and pushing local copy                       ║
╚{'═' * 70}╝
""")
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
╭{'─' * 70}╮
│ 📤 Uploading local repository to cloud...                                │
╰{'─' * 70}╯
""")

    repo_root_path.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, os_specific=False)

    print(f"""
╔{'═' * 70}╗
║ ✅ Repository successfully pushed to cloud                                ║
╚{'═' * 70}╝
""")


# import sys
# import subprocess


def get_wt_cmd(wd1: P, wd2: P) -> str:
    lines = [
        f"""wt --window 0 new-tab --profile pwsh --title "gitdiff" --tabColor `#3b04d1 --startingDirectory {wd1} ` --colorScheme "Solarized Dark" """,
        f"""split-pane --horizontal --profile pwsh --startingDirectory {wd2} --size 0.5 --colorScheme "Tango Dark" -- pwsh -Interactive """
    ]
    return " `; ".join(lines)


def inspect_repos(repo_local_root: str, repo_remote_root: str):
    print(f"""
╔{'═' * 70}╗
║ 🔍 Inspecting Repositories                                                ║
╠{'═' * 70}╣
║ 📂 Local:  {repo_local_root}                      
║ 📂 Remote: {repo_remote_root}                    
╚{'═' * 70}╝
""")

    if platform.system() == "Windows":
        program = get_wt_cmd(wd1=P(repo_local_root), wd2=P(repo_local_root))
        write_shell_script(program=program, execute=True, desc="Inspecting repos ...", preserve_cwd=True, display=True)
        return None
    elif platform.system() == "Linux":
        program = get_zellij_cmd(wd1=P(repo_local_root), wd2=P(repo_remote_root))
        write_shell_script(program=program, execute=True, desc="Inspecting repos ...", preserve_cwd=True, display=True)
        return None
    else: raise NotImplementedError(f"Platform {platform.system()} not implemented.")


def fetch_dotfiles():
    print(f"""
╔{'═' * 70}╗
║ 📁 Fetching Dotfiles                                                      ║
╚{'═' * 70}╝
""")

    cloud_resolved = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
    print(f"""
╭{'─' * 70}╮
│ ⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}     │
╰{'─' * 70}╯
""")

    dotfiles_local = P.home().joinpath("dotfiles")
    CONFIG_PATH.joinpath("remote").create()
    dotfiles_remote = CONFIG_PATH.joinpath("remote", dotfiles_local.rel2home())
    remote_path = dotfiles_local.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"

    print(f"""
╭{'─' * 70}╮
│ 📥 Downloading dotfiles from cloud...                                    │
╰{'─' * 70}╯
""")

    dotfiles_remote.from_cloud(remotepath=remote_path, cloud=cloud_resolved,
        unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=None)

    print(f"""
╭{'─' * 70}╮
│ 🗑️  Removing old dotfiles and replacing with cloud version...            │
╰{'─' * 70}╯
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
    shell_path = get_shell_script(shell_script=script)
    Terminal().run(f". {shell_path}", shell="bash").capture().print()

    print(f"""
╔{'═' * 70}╗
║ ✅ Dotfiles successfully fetched and installed                            ║
╚{'═' * 70}╝
""")

