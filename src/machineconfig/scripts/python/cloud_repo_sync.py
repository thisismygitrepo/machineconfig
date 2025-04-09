"""utils"""

import git
from crocodile.file_management import P, Read
from crocodile.meta import Terminal
from crocodile.core import randstr

from machineconfig.scripts.python.helpers.repo_sync_helpers import fetch_dotfiles
from machineconfig.utils.utils import CONFIG_PATH, DEFAULTS_PATH, PROGRAM_PATH, get_shell_file_executing_python_script, write_shell_script_to_file, choose_one_option
import platform
import argparse
from typing import Optional, Literal

_ = fetch_dotfiles


def main(cloud: Optional[str] = None, path: Optional[str] = None, message: Optional[str] = None,
         action: Literal["ask", "pushLocalMerge", "overwriteLocal", "InspectRepos", "RemoveLocalRclone"] = "ask",
         pwd: Optional[str] = None):
    if cloud is None:
        try:
            cloud_resolved = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"""
╭{'─' * 70}╮
│ ⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}     │
╰{'─' * 70}╯
""")
        except FileNotFoundError:
            print(f"""
╔{'═' * 70}╗
║ ❌ ERROR: No cloud profile found                                          ║
╠{'═' * 70}╣
║ Location: {DEFAULTS_PATH}                        
║ Please set one up or provide one via the --cloud flag.                   ║
╚{'═' * 70}╝
""")
            return ""
    else: cloud_resolved = cloud
    
    # repo_root = P(args.repo).expanduser().absolute()
    repo_local_root = P.cwd() if path is None else P(path).expanduser().absolute()
    repo_local_obj = git.Repo(repo_local_root, search_parent_directories=True)
    repo_local_root = P(repo_local_obj.working_dir)  # cwd might have been in a sub directory of repo_root, so its better to redefine it.
    CONFIG_PATH.joinpath("remote").create()
    repo_remote_root = CONFIG_PATH.joinpath("remote", repo_local_root.rel2home())  # .delete(sure=True)
    
    try:
        print(f"""
╔{'═' * 70}╗
║ 📥 DOWNLOADING REMOTE REPOSITORY                                          ║
╚{'═' * 70}╝
""")
        remote_path = repo_local_root.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"
        repo_remote_root.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=pwd)
    except AssertionError:
        print(f"""
╔{'═' * 70}╗
║ 🆕 Remote repository doesn't exist                                        ║
║ 📤 Creating new remote and exiting...                                     ║
╚{'═' * 70}╝
""")
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
        return ""
        
    repo_remote_obj = git.Repo(repo_remote_root)
    if repo_remote_obj.is_dirty():
        print(f"""
╔{'═' * 70}╗
║ ⚠️  WARNING: REMOTE REPOSITORY IS DIRTY                                    ║
╠{'═' * 70}╣
║ Location: {repo_remote_root}               
║ Please commit or stash changes before proceeding.                        ║
╚{'═' * 70}╝
""")

    script = f"""
echo ""
echo "╔{'═' * 70}╗"
echo "║ 💾 COMMITTING LOCAL CHANGES                                               ║"
echo "╚{'═' * 70}╝"
cd {repo_local_root}
git status
git add .
git commit -am "{message}"
echo ""
echo ""
echo "╔{'═' * 70}╗"
echo "║ 🔄 PULLING LATEST FROM REMOTE                                             ║"
echo "╚{'═' * 70}╝"
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
        print(f"""
╔{'═' * 70}╗
║ ✅ Pull succeeded!                                                        ║
╠{'═' * 70}╣
║ 🧹 Removing originEnc remote and local copy                               ║
║ 📤 Pushing merged repository to cloud storage                             ║
╚{'═' * 70}╝
""")
        repo_remote_root.delete(sure=True)
        from git.remote import Remote
        Remote.remove(repo_local_obj, "originEnc")
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
    else:
        print(f"""
╔{'═' * 70}╗
║ ⚠️  MERGE FAILED                                                          ║
╠{'═' * 70}╣
║ 💾 Keeping local copy of remote at:                                       ║
║ 📂 {repo_remote_root}                    
╚{'═' * 70}╝
""")

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
"""
        if platform.system() == "Linux": program_2 += """
sudo chmod 600 $HOME/.ssh/*
sudo chmod 700 $HOME/.ssh
sudo chmod +x $HOME/dotfiles/scripts/linux -R
"""

        shell_file_2 = write_shell_script_to_file(shell_script=program_2)

        # ================================================================================
        option3 = 'Inspect repos:'
        program_3_py = f"""
from machineconfig.scripts.python.cloud_repo_sync import inspect_repos as func
func(repo_local_root=r'{repo_local_root.to_str()}', repo_remote_root=r'{repo_remote_root.to_str()}')
"""
        shell_file_3 = get_shell_file_executing_python_script(python_script=program_3_py, ve_name="ve")
        # ================================================================================

        option4 = 'Remove problematic rclone file from repo and replace with remote:'
        program_4 = f"""
rm $HOME/dotfiles/creds/rclone/rclone.conf
cp $HOME/.config/machineconfig/remote/dotfiles/creds/rclone/rclone.conf $HOME/dotfiles/creds/rclone
cd $HOME/dotfiles
git commit -am "finished merging"
. {shell_file_1}
"""
        shell_file_4 = write_shell_script_to_file(shell_script=program_4)
        # ================================================================================

        print(f"""
╔{'═' * 70}╗
║ 🔄 RESOLVE MERGE CONFLICT                                                 ║
╠{'═' * 70}╣
║ Choose an option to resolve the conflict:                                ║
╚{'═' * 70}╝
""")
        
        print(f"• 1️⃣  {option1:75} 👉 {shell_file_1}")
        print(f"• 2️⃣  {option2:75} 👉 {shell_file_2}")
        print(f"• 3️⃣  {option3:75} 👉 {shell_file_3}")
        print(f"• 4️⃣  {option4:75} 👉 {shell_file_4}")

        program_content = None
        match action:
            case "ask":
                choice = choose_one_option(options=[option1, option2, option3, option4], fzf=False)
                if choice == option1: program_content = shell_file_1.read_text()
                elif choice == option2: program_content = program_2
                elif choice == option3: program_content = shell_file_3.read_text()
                elif choice == option4: program_content = program_4
                else: raise NotImplementedError(f"Choice {choice} not implemented.")
            case "pushLocalMerge": program_content = shell_file_1.read_text()
            case "overwriteLocal": program_content = program_2
            case "InspectRepos": program_content = shell_file_3.read_text()
            case "RemoveLocalRclone": program_content = program_4
        PROGRAM_PATH.write_text(program_content)
    return program_content

def args_parser():
    print(f"""
╔{'═' * 70}╗
║ 🔄 Repository Synchronization Utility                                     ║
╚{'═' * 70}╝
""")

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
    main(cloud=args.cloud, path=args.path, message=args.message, action=args.action)

if __name__ == "__main__":
    args_parser()
