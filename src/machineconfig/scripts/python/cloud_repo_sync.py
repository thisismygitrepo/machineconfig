
"""utils"""


from machineconfig.utils.utils import CONFIG_PATH, DEFAULTS_PATH, write_shell_script, get_shell_file_executing_python_script
from crocodile.file_management import P, Read, install_n_import
from crocodile.core import randstr
from crocodile.meta import Terminal
import argparse
import platform
from typing import Optional
# import sys
# import subprocess


def get_wt_cmd(wd1: P, wd2: P) -> str:
    lines = [
        f"""wt --window 0 new-tab --profile pwsh --title "gitdiff" --tabColor `#3b04d1 --startingDirectory {wd1} ` --colorScheme "Solarized Dark" """,
        f"""split-pane --horizontal --profile pwsh --startingDirectory {wd2} --size 0.5 --colorScheme "Tango Dark" -- pwsh -Interactive """
    ]
    return " `; ".join(lines)

def get_zellij_cmd(wd1: P, wd2: P) -> str:
    lines = [f""" zellij action new-tab --name gitdiff""",
             f"""zellij action new-pane --direction down --name local --cwd ./data """,
             f"""zellij action write-chars "cd '{wd1}'; git status" """,
             f"""zellij action move-focus up; zellij action close-pane """,
             f"""zellij action new-pane --direction down --name remote --cwd code """,
             f"""zellij action write-chars "cd '{wd2}' """,
             f"""git status" """
    ]
    return "; ".join(lines)


def args_parser():
    parser = argparse.ArgumentParser(description="Secure Repo CLI.")

    # parser.add_argument("cmd", help="command to run", choices=["pull", "push"])
    parser.add_argument("path", nargs='?', type=str, help="Repository path, defaults to cwd.", default=None)

    # parser.add_argument("--share", help="Repository path, defaults to cwd.", action="store_true", default=False)

    parser.add_argument("--cloud", "-c", help="rclone cloud profile name.", default=None)
    parser.add_argument("--message", "-m", help="Commit Message", default=f"new message {randstr()}")
    parser.add_argument("--skip_confirmation", "-s", help="Skip confirmation.", action="store_true", default=False)
    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)
    parser.add_argument("--no_push", "-u", help="push to reomte.", action="store_true")  # default is False
    args = parser.parse_args()

    # if args.share:
    #     from machineconfig.scripts.cloud.dotfiles import put
    #     put()
    #     return None
    main(cloud=args.cloud, path=args.path, message=args.message, skip_confirmation=args.skip_confirmation, pwd=args.pwd, push=not args.no_push)


def main(cloud: Optional[str] = None, path: Optional[str] = None, message: Optional[str] = None, skip_confirmation: bool = False, pwd: Optional[str] = None, push: bool = True):
    if cloud is None:
        try:
            cloud_resolved = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH} ⚠️")
        except FileNotFoundError:
            print(f"No cloud profile found @ {DEFAULTS_PATH}, please set one up or provide one via the --cloud flag.")
            return ""
    else: cloud_resolved = cloud
    # repo_root = P(args.repo).expanduser().absolute()
    repo_root = P.cwd() if path is None else P(path).expanduser().absolute()
    repo_obj = install_n_import("git", "gitpython").Repo(repo_root, search_parent_directories=True)
    repo_root = P(repo_obj.working_dir)  # cwd might have been in a sub directory of repo_root, so its better to redefine it.
    CONFIG_PATH.joinpath("remote").create()
    repo_sync_root = CONFIG_PATH.joinpath("remote", repo_root.rel2home())  # .delete(sure=True)
    try:
        print("\n", "=============================== Downloading Remote Repo ====================================")
        remote_path = repo_root.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"
        repo_sync_root.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=pwd)
    except AssertionError:
        print("Remote does not exist, creating it and exiting ... ")
        repo_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
        return ""
    repo_sync_obj = install_n_import("git", "gitpython").Repo(repo_sync_root)
    if repo_sync_obj.is_dirty():
        print("=" * 50, '\n', f"WRANING: the remote `{repo_sync_root}` is dirty, please commit or stash changes before proceeding.", '\n', "=" * 50)

    script = f"""
echo ""
echo "=============================== Committing Local Changes ==================================="
cd {repo_root}
git status
git add .
git commit -am "{message}"
echo ""
echo ""
echo "=============================== Pulling Latest From Remote ================================"
cd {repo_root}
echo '-> Trying to removing originEnc remote from local repo if it exists.'
git remote remove originEnc
echo '-> Adding originEnc remote to local repo'
git remote add originEnc {repo_sync_root}
echo '-> Fetching originEnc remote.'
git pull originEnc master

"""
    suffix = '.ps1' if platform.system() == 'Windows' else '.sh'
    res = Terminal().run(f". {P.tmpfile(suffix=suffix).write_text(script)}", shell="powershell").capture().print()

    if res.is_successful(strict_err=True, strict_returcode=True):
        print("\n", "Pull succeeded, removing originEnc, the local copy of remote & pushing merged repo_root to remote ... ")
        repo_sync_root.delete(sure=True)
        from git.remote import Remote
        Remote.remove(repo_obj, "originEnc")
        if push:
            repo_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
    else:
        print(f"Failed to pull, keeping local copy of remote at {repo_sync_root} ... ")

        if push:
            if skip_confirmation: resp = "y"
            else: resp = input(f"Would you like to proceed syncing `{repo_root}` to `{cloud_resolved}` by pushing local changes to remote and deleting local copy of remote? y/[n] ") or "n"
        else: resp = "n"

        if resp.lower() == "y":
            delete_remote_repo_copy_and_push_local(remote_repo=repo_sync_root.str, local_repo=repo_root.str, cloud=cloud_resolved)
        else:
            program = f"""
from machineconfig.scripts.python.cloud_repo_sync import delete_remote_repo_copy_and_push_local as func
func(remote_repo=r'{repo_sync_root.str}', local_repo=r'{repo_root.str}', cloud=r'{cloud_resolved}')
"""
            shell_file = get_shell_file_executing_python_script(python_script=program)
            print(f"When ready, use this snippet: \n. {shell_file}")
            if platform.system() == "Windows":
                program = get_wt_cmd(wd1=repo_root, wd2=repo_sync_root)
                write_shell_script(program=program, execute=True)
                return None
            elif platform.system() == "Linux":
                program = get_zellij_cmd(wd1=repo_root, wd2=repo_sync_root)
                write_shell_script(program=program, execute=True)
                return None
            else: raise NotImplementedError(f"Platform {platform.system()} not implemented.")


def delete_remote_repo_copy_and_push_local(remote_repo: str, local_repo: str, cloud: str):
    repo_sync_root = P(remote_repo).expanduser().absolute()
    repo_root_path = P(local_repo).expanduser().absolute()
    repo_sync_root.delete(sure=True)
    from git.remote import Remote
    from git.repo import Repo
    try: Remote.remove(Repo(repo_root_path), "originEnc")
    except Exception: pass  # type: ignore
    repo_root_path.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, os_specific=False)


if __name__ == "__main__":
    args_parser()
