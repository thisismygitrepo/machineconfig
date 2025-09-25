"""utils"""

from pathlib import Path
import git
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.terminal import Terminal
from machineconfig.utils.utils2 import randstr, read_ini

from machineconfig.scripts.python.helpers.repo_sync_helpers import fetch_dotfiles
from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH
from machineconfig.utils.options import choose_one_option
from machineconfig.utils.code import get_shell_file_executing_python_script, write_shell_script_to_file
import platform
import argparse
from typing import Optional, Literal
from rich.console import Console
from rich.panel import Panel

console = Console()

_ = fetch_dotfiles


def main(cloud: Optional[str] = None, path: Optional[str] = None, message: Optional[str] = None, action: Literal["ask", "pushLocalMerge", "overwriteLocal", "InspectRepos", "RemoveLocalRclone"] = "ask", pwd: Optional[str] = None):
    if cloud is None:
        try:
            cloud_resolved = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}", title="Default Cloud", border_style="yellow"))
        except FileNotFoundError:
            console.print(Panel(f"❌ ERROR: No cloud profile found\nLocation: {DEFAULTS_PATH}\nPlease set one up or provide one via the --cloud flag.", title="Error", border_style="red"))
            return ""
    else:
        cloud_resolved = cloud

    # repo_root = PathExtended(args.repo).expanduser().absolute()
    repo_local_root = PathExtended.cwd() if path is None else PathExtended(path).expanduser().absolute()
    repo_local_obj = git.Repo(repo_local_root, search_parent_directories=True)
    repo_local_root = PathExtended(repo_local_obj.working_dir)  # cwd might have been in a sub directory of repo_root, so its better to redefine it.
    PathExtended(CONFIG_PATH).joinpath("remote").mkdir(parents=True, exist_ok=True)
    repo_remote_root = PathExtended(CONFIG_PATH).joinpath("remote", repo_local_root.rel2home())  # .delete(sure=True)

    try:
        console.print(Panel("📥 DOWNLOADING REMOTE REPOSITORY", title_align="left", border_style="blue"))
        remote_path = repo_local_root.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"
        repo_remote_root.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=pwd)
    except AssertionError:
        console.print(Panel("🆕 Remote repository doesn't exist\n📤 Creating new remote and exiting...", title_align="left", border_style="green"))
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
        return ""

    repo_remote_obj = git.Repo(repo_remote_root)
    if repo_remote_obj.is_dirty():
        console.print(Panel(f"⚠️  WARNING: REMOTE REPOSITORY IS DIRTY\nLocation: {repo_remote_root}\nPlease commit or stash changes before proceeding.", title="Warning", border_style="yellow"))

    script = f"""
echo ""
echo 'echo -e "\\033[1;34m═════ COMMITTING LOCAL CHANGES ═════\\033[0m"'
cd {repo_local_root}
git status
git add .
git commit -am "{message}"
echo ""
echo ""
echo 'echo -e "\\033[1;34m═════ PULLING LATEST FROM REMOTE ═════\\033[0m"'
cd {repo_local_root}
echo '-> Trying to removing originEnc remote from local repo if it exists.'
# git remote remove originEnc
git remote remove originEnc 2>/dev/null || true
echo '-> Adding originEnc remote to local repo'
git remote add originEnc {repo_remote_root}
echo '-> Fetching originEnc remote.'
git pull originEnc master

"""

    shell_path = write_shell_script_to_file(shell_script=script)
    res = Terminal().run(f". {shell_path}", shell="powershell").capture().print()

    if res.is_successful(strict_err=True, strict_returcode=True):
        console.print(Panel("✅ Pull succeeded!\n🧹 Removing originEnc remote and local copy\n📤 Pushing merged repository to cloud storage", title="Success", border_style="green"))
        repo_remote_root.delete(sure=True)
        from git.remote import Remote

        Remote.remove(repo_local_obj, "originEnc")
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
        return "success"
    else:
        console.print(Panel(f"⚠️  MERGE FAILED\n💾 Keeping local copy of remote at:\n📂 {repo_remote_root}", title="Merge Failed", border_style="red"))

        # ================================================================================
        option1 = "Delete remote copy and push local:"
        program_1_py = f"""
from machineconfig.scripts.python.helpers.repo_sync_helpers import delete_remote_repo_copy_and_push_local as func
func(remote_repo=r'{str(repo_remote_root)}', local_repo=r'{str(repo_local_root)}', cloud=r'{cloud_resolved}')
"""
        shell_file_1 = get_shell_file_executing_python_script(python_script=program_1_py, ve_path=str(Path.home().joinpath("code", "machineconfig", ".venv")))
        # ================================================================================

        option2 = "Delete local repo and replace it with remote copy:"
        program_2 = f"""
rm -rfd {repo_local_root}
mv {repo_remote_root} {repo_local_root}
"""
        if platform.system() in ["Linux", "Darwin"]:
            program_2 += """
sudo chmod 600 $HOME/.ssh/*
sudo chmod 700 $HOME/.ssh
sudo chmod +x $HOME/dotfiles/scripts/linux -R
"""

        shell_file_2 = write_shell_script_to_file(shell_script=program_2)

        # ================================================================================
        option3 = "Inspect repos:"
        program_3_py = f"""
from machineconfig.scripts.python.helper.repo_sync_helpers import inspect_repos as func
func(repo_local_root=r'{str(repo_local_root)}', repo_remote_root=r'{str(repo_remote_root)}')
"""
        shell_file_3 = get_shell_file_executing_python_script(python_script=program_3_py, ve_path=str(Path.home().joinpath("code", "machineconfig", ".venv")))
        # ================================================================================

        option4 = "Remove problematic rclone file from repo and replace with remote:"
        program_4 = f"""
rm $HOME/dotfiles/creds/rclone/rclone.conf
cp $HOME/.config/machineconfig/remote/dotfiles/creds/rclone/rclone.conf $HOME/dotfiles/creds/rclone
cd $HOME/dotfiles
git commit -am "finished merging"
. {shell_file_1}
"""
        shell_file_4 = write_shell_script_to_file(shell_script=program_4)
        # ================================================================================

        console.print(Panel("🔄 RESOLVE MERGE CONFLICT\nChoose an option to resolve the conflict:", title_align="left", border_style="blue"))

        print(f"• 1️⃣  {option1:75} 👉 {shell_file_1}")
        print(f"• 2️⃣  {option2:75} 👉 {shell_file_2}")
        print(f"• 3️⃣  {option3:75} 👉 {shell_file_3}")
        print(f"• 4️⃣  {option4:75} 👉 {shell_file_4}")

        program_content = None
        match action:
            case "ask":
                choice = choose_one_option(options=[option1, option2, option3, option4], fzf=False)
                if choice == option1:
                    program_content = shell_file_1.read_text(encoding="utf-8")
                elif choice == option2:
                    program_content = program_2
                elif choice == option3:
                    program_content = shell_file_3.read_text(encoding="utf-8")
                elif choice == option4:
                    program_content = program_4
                else:
                    raise NotImplementedError(f"Choice {choice} not implemented.")
            case "pushLocalMerge":
                program_content = shell_file_1.read_text(encoding="utf-8")
            case "overwriteLocal":
                program_content = program_2
            case "InspectRepos":
                program_content = shell_file_3.read_text(encoding="utf-8")
            case "RemoveLocalRclone":
                program_content = program_4
            case _:
                raise ValueError(f"Unknown action: {action}")
        # PROGRAM_PATH.write_text(program_content, encoding="utf-8")
        import subprocess

        subprocess.run(program_content, shell=True, check=True)

    return program_content


def args_parser():
    console.print(Panel("🔄 Repository Synchronization Utility", title_align="left", border_style="blue"))

    parser = argparse.ArgumentParser(description="Secure Repo CLI.")
    # parser.add_argument("cmd", help="command to run", choices=["pull", "push"])
    parser.add_argument("path", nargs="?", type=str, help="Repository path, defaults to cwd.", default=None)
    # parser.add_argument("--share", help="Repository path, defaults to cwd.", action="store_true", default=False)
    parser.add_argument("--cloud", "-c", help="rclone cloud profile name.", default=None)
    parser.add_argument("--message", "-m", help="Commit Message", default=f"new message {randstr()}")
    # parser.add_argument("--skip_confirmation", "-s", help="Skip confirmation.", action="store_true", default=False)
    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)
    # parser.add_argument("--no_push", "-u", help="push to reomte.", action="store_true")  # default is False
    parser.add_argument("--action", "-a", help="Action to take if merge fails.", choices=["ask", "pushLocalMerge", "overwriteLocal", "InspectRepos", "RemoveLocalRclone"], default="ask")
    args = parser.parse_args()
    main(cloud=args.cloud, path=args.path, message=args.message, action=args.action)


if __name__ == "__main__":
    args_parser()
