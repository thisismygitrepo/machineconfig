import git
from rich.console import Console
from rich.panel import Panel
import typer

from machineconfig.utils.io import read_ini
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.terminal import Response
from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.code import get_shell_file_executing_python_script, write_shell_script_to_file

import platform
import subprocess
from typing import Optional, Literal
from pathlib import Path
import sys

console = Console()


def main(
    cloud: Optional[str] = typer.Option(None, "--cloud", "-c", help="Cloud storage profile name. If not provided, uses default from config."),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Path to the local repository. Defaults to current working directory."),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Commit message for local changes."),
    on_conflict: Literal["ask", "pushLocalMerge", "overwriteLocal", "InspectRepos", "RemoveLocalRclone"] = typer.Option("ask", "--on-conflict", "-oc", help="Action to take on merge conflict. Default is 'ask'."),
    pwd: Optional[str] = typer.Option(None, "--password", help="Password for encryption/decryption of the remote repository."),
):
    if cloud is None:
        try:
            cloud_resolved = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}", title="Default Cloud", border_style="yellow"))
        except FileNotFoundError:
            console.print(Panel(f"❌ ERROR: No cloud profile found\nLocation: {DEFAULTS_PATH}\nPlease set one up or provide one via the --cloud flag.", title="Error", border_style="red"))
            return ""
    else:
        cloud_resolved = cloud
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
    command = f". {shell_path}"
    if platform.system() == "Windows":
        completed = subprocess.run(["powershell", "-Command", command], capture_output=True, check=False, text=True)
    else:
        completed = subprocess.run(command, shell=True, capture_output=True, check=False, text=True)
    res = Response.from_completed_process(completed).capture().print()

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
        match on_conflict:
            case "ask":
                choice = choose_from_options(multi=False, msg="Choose one option", options=[option1, option2, option3, option4], fzf=False)
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
                raise ValueError(f"Unknown action: {on_conflict}")
        # PROGRAM_PATH.write_text(program_content, encoding="utf-8")
        subprocess.run(program_content, shell=True, check=True)

    return program_content


def args_parser():
    # Check if no arguments provided (excluding the script name)
    if len(sys.argv) == 1:
        app = typer.Typer(add_completion=False, help="Sync a local git repository with a remote encrypted cloud copy.")
        app.command()(main)
        app(["--help"])
        return

    app = typer.Typer(add_completion=False, no_args_is_help=True, help="Sync a local git repository with a remote encrypted cloud copy.")
    app.command()(main)
    app()


if __name__ == "__main__":
    args_parser()
