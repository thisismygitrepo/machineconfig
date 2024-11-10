
"""utils"""

import git
from crocodile.file_management import P, Read
from crocodile.core import randstr
from crocodile.meta import Terminal

from machineconfig.utils.utils import CONFIG_PATH, DEFAULTS_PATH, PROGRAM_PATH, write_shell_script, get_shell_file_executing_python_script, get_shell_script, choose_one_option
import argparse
import platform
from typing import Optional, Literal
# import sys
# import subprocess


def get_wt_cmd(wd1: P, wd2: P) -> str:
    lines = [
        f"""wt --window 0 new-tab --profile pwsh --title "gitdiff" --tabColor `#3b04d1 --startingDirectory {wd1} ` --colorScheme "Solarized Dark" """,
        f"""split-pane --horizontal --profile pwsh --startingDirectory {wd2} --size 0.5 --colorScheme "Tango Dark" -- pwsh -Interactive """
    ]
    return " `; ".join(lines)


def get_zellij_cmd(wd1: P, wd2: P) -> str:
    _ = wd1, wd2
    lines = [""" zellij action new-tab --name gitdiff""",
             """zellij action new-pane --direction down --name local --cwd ./data """,
             """zellij action write-chars "cd '{wd1}'; git status" """,
             """zellij action move-focus up; zellij action close-pane """,
             """zellij action new-pane --direction down --name remote --cwd code """,
             """zellij action write-chars "cd '{wd2}' """,
             """git status" """
    ]
    return "; ".join(lines)


def args_parser():
    parser = argparse.ArgumentParser(description="Secure Repo CLI.")

    # parser.add_argument("cmd", help="command to run", choices=["pull", "push"])
    parser.add_argument("path", nargs='?', type=str, help="Repository path, defaults to cwd.", default=None)

    # parser.add_argument("--share", help="Repository path, defaults to cwd.", action="store_true", default=False)

    parser.add_argument("--cloud", "-c", help="rclone cloud profile name.", default=None)
    parser.add_argument("--message", "-m", help="Commit Message", default=f"new message {randstr()}")
    # parser.add_argument("--skip_confirmation", "-s", help="Skip confirmation.", action="store_true", default=False)
    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)
    # parser.add_argument("--no_push", "-u", help="push to reomte.", action="store_true")  # default is False
    parser.add_argument("--action", "-a", help="Action to take if merge fails.", choices=["ask", "pushLocalMerge", "overwriteLocal", "InspectRepos", "RemoveLocalRclone"], default="ask")
    args = parser.parse_args()

    # if args.share:
    #     from machineconfig.scripts.cloud.dotfiles import put
    #     put()
    #     return None
    main(cloud=args.cloud, path=args.path, message=args.message, action=args.action)


def main(cloud: Optional[str] = None, path: Optional[str] = None, message: Optional[str] = None,
         action: Literal["ask", "pushLocalMerge", "overwriteLocal", "InspectRepos", "RemoveLocalRclone"] = "ask",
         pwd: Optional[str] = None):
    if cloud is None:
        try:
            cloud_resolved = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH} ⚠️")
        except FileNotFoundError:
            print(f"No cloud profile found @ {DEFAULTS_PATH}, please set one up or provide one via the --cloud flag.")
            return ""
    else: cloud_resolved = cloud
    # repo_root = P(args.repo).expanduser().absolute()
    repo_local_root = P.cwd() if path is None else P(path).expanduser().absolute()
    repo_local_obj = git.Repo(repo_local_root, search_parent_directories=True)
    repo_local_root = P(repo_local_obj.working_dir)  # cwd might have been in a sub directory of repo_root, so its better to redefine it.
    CONFIG_PATH.joinpath("remote").create()
    repo_remote_root = CONFIG_PATH.joinpath("remote", repo_local_root.rel2home())  # .delete(sure=True)
    try:
        print("\n", "=============================== Downloading Remote Repo ====================================")
        remote_path = repo_local_root.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"
        repo_remote_root.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=pwd)
    except AssertionError:
        print("Remote does not exist, creating it and exiting ... ")
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
        return ""
    repo_remote_obj = git.Repo(repo_remote_root)
    if repo_remote_obj.is_dirty():
        print("=" * 50, '\n', f"WRANING: the remote `{repo_remote_root}` is dirty, please commit or stash changes before proceeding.", '\n', "=" * 50)

    script = f"""
echo ""
echo "=============================== Committing Local Changes ==================================="
cd {repo_local_root}
git status
git add .
git commit -am "{message}"
echo ""
echo ""
echo "=============================== Pulling Latest From Remote ================================"
cd {repo_local_root}
echo '-> Trying to removing originEnc remote from local repo if it exists.'
git remote remove originEnc
echo '-> Adding originEnc remote to local repo'
git remote add originEnc {repo_remote_root}
echo '-> Fetching originEnc remote.'
git pull originEnc master

"""

    shell_path = get_shell_script(shell_script=script)
    res = Terminal().run(f". {shell_path}", shell="powershell").capture().print()

    if res.is_successful(strict_err=True, strict_returcode=True):
        print("\n", "Pull succeeded, removing originEnc, the local copy of remote & pushing merged repo_root to remote ... ")
        repo_remote_root.delete(sure=True)
        from git.remote import Remote
        Remote.remove(repo_local_obj, "originEnc")
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
    else:
        print(f"Failed to merge with no errors, keeping local copy of remote at {repo_remote_root} ... ")

        # ================================================================================
        option1 = 'Delete remote copy and push local:'
        program_1_py = f"""
from machineconfig.scripts.python.cloud_repo_sync import delete_remote_repo_copy_and_push_local as func
func(remote_repo=r'{repo_remote_root.to_str()}', local_repo=r'{repo_local_root.to_str()}', cloud=r'{cloud_resolved}')
"""
        shell_file_1 = get_shell_file_executing_python_script(python_script=program_1_py, ve_name="ve")
        # ================================================================================

        option2 = 'Delete local repo and replace it with remote copy:'
        program_2 = f"""
rm -rfd {repo_local_root}
mv {repo_remote_root} {repo_local_root}
sudo chmod 600 ~/.ssh/*
sudo chmod 700 ~/.ssh
"""

        shell_file_2 = get_shell_script(shell_script=program_2)

        # ================================================================================
        option3 = 'Inspect repos:'
        program_3_py = f"""
from machineconfig.scripts.python.cloud_repo_sync import inspect_repos as func
func(repo_local_root=r'{repo_local_root.to_str()}', repo_remote_root=r'{repo_remote_root.to_str()}')
"""
        shell_file_3 = get_shell_file_executing_python_script(python_script=program_3_py, ve_name="ve")
        # ================================================================================

        option4 = 'Remove problematic rclone file from repo and replace with remote:'
        program_4 = """
rm ~/dotfiles/creds/rclone/rclone.conf
cp ~/.config/machineconfig/remote/dotfiles/creds/rclone/rclone.conf ~/dotfiles/creds/rclone
"""
        shell_file_4 = get_shell_script(shell_script=program_4)
        # ================================================================================

        print(f"• {option1:75} 👉 {shell_file_1}")
        print(f"• {option2:75} 👉 {shell_file_2}")
        print(f"• {option3:75} 👉 {shell_file_3}")
        print(f"• {option4:75} 👉 {shell_file_4}")

        match action:
            case "ask":
                choice = choose_one_option(options=[option1, option2, option3, option4])
                if choice == option1: PROGRAM_PATH.write_text(shell_file_1.read_text())
                elif choice == option2: PROGRAM_PATH.write_text(program_2)
                elif choice == option3: PROGRAM_PATH.write_text(shell_file_3.read_text())
                elif choice == option4: PROGRAM_PATH.write_text(program_4)
                else: raise NotImplementedError(f"Choice {choice} not implemented.")
            case "pushLocalMerge":
                PROGRAM_PATH.write_text(shell_file_1.read_text())
            case "overwriteLocal":
                PROGRAM_PATH.write_text(program_2)
            case "InspectRepos":
                PROGRAM_PATH.write_text(shell_file_3.read_text())
            case "RemoveLocalRclone":
                PROGRAM_PATH.write_text(program_4)


def delete_remote_repo_copy_and_push_local(remote_repo: str, local_repo: str, cloud: str):
    repo_sync_root = P(remote_repo).expanduser().absolute()
    repo_root_path = P(local_repo).expanduser().absolute()
    repo_sync_root.delete(sure=True)
    from git.remote import Remote
    from git.repo import Repo
    try: Remote.remove(Repo(repo_root_path), "originEnc")
    except Exception: pass  # type: ignore
    repo_root_path.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, os_specific=False)


def inspect_repos(repo_local_root: str, repo_remote_root: str):
    if platform.system() == "Windows":
        program = get_wt_cmd(wd1=P(repo_local_root), wd2=P(repo_local_root))
        write_shell_script(program=program, execute=True)
        return None
    elif platform.system() == "Linux":
        program = get_zellij_cmd(wd1=P(repo_local_root), wd2=P(repo_remote_root))
        write_shell_script(program=program, execute=True)
        return None
    else: raise NotImplementedError(f"Platform {platform.system()} not implemented.")



if __name__ == "__main__":
    args_parser()
