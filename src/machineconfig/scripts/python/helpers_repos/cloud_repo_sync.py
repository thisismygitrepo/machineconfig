import git
from rich.console import Console
from rich.panel import Panel
import typer

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.terminal import Response
from machineconfig.utils.source_of_truth import CONFIG_ROOT, DEFAULTS_PATH
from machineconfig.utils.code import get_shell_file_executing_python_script, write_shell_script_to_file

import platform
import subprocess
from typing import Optional, Literal, Annotated


console = Console()


def main(
    cloud: Annotated[Optional[str], typer.Option(..., "--cloud", "-c", help="Cloud storage profile name. If not provided, uses default from config.")] = None,
    repo: Annotated[Optional[str], typer.Option(..., "--repo", "-r", help="Path to the local repository. Defaults to current working directory.")] = None,
    message: Annotated[Optional[str], typer.Option(..., "--message", "-m", help="Commit message for local changes.")] = None,
    on_conflict: Annotated[Literal["ask", "push-local-merge", "overwrite-local", "stop-on-conflict", "remove-rclone-conflict"], typer.Option(..., "--on-conflict", "-oc", help="Action to take on merge conflict. Default is 'ask'.")] = "ask",
    pwd: Annotated[Optional[str], typer.Option(..., "--password", help="Password for encryption/decryption of the remote repository.")] = None,
):
    if cloud is None:
        try:
            from machineconfig.utils.io import read_ini

            cloud_resolved = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  Using default cloud: `{cloud_resolved}` from {DEFAULTS_PATH}", title="Default Cloud", border_style="yellow"))
        except FileNotFoundError:
            console.print(Panel(f"❌ ERROR: No cloud profile found\nLocation: {DEFAULTS_PATH}\nPlease set one up or provide one via the --cloud flag.", title="Error", border_style="red"))
            return ""
    else:
        cloud_resolved = cloud
    repo_local_root = PathExtended.cwd() if repo is None else PathExtended(repo).expanduser().absolute()
    repo_local_obj = git.Repo(repo_local_root, search_parent_directories=True)
    repo_local_root = PathExtended(repo_local_obj.working_dir)  # cwd might have been in a sub directory of repo_root, so its better to redefine it.
    PathExtended(CONFIG_ROOT).joinpath("remote").mkdir(parents=True, exist_ok=True)
    repo_remote_root = PathExtended(CONFIG_ROOT).joinpath("remote", repo_local_root.rel2home())  # .delete(sure=True)

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
        def func2(remote_repo: str, local_repo: str, cloud: str):
            from machineconfig.scripts.python.repos_helpers.sync import delete_remote_repo_copy_and_push_local
            delete_remote_repo_copy_and_push_local(remote_repo=remote_repo, local_repo=local_repo, cloud=cloud)
            return "done"
        from machineconfig.utils.meta import function_to_script
        program_1_py = function_to_script(func=func2, call_with_args=None, call_with_kwargs={"remote_repo": str(repo_remote_root), "local_repo": str(repo_local_root), "cloud": cloud_resolved})
        shell_file_1 = get_shell_file_executing_python_script(python_script=program_1_py, ve_path=None, executable="""uv run --with "machineconfig>=6.36" """)
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
        def func(repo_local_root: str, repo_remote_root: str):
            from machineconfig.scripts.python.repos_helpers.sync import inspect_repos
            inspect_repos(repo_local_root=repo_local_root, repo_remote_root=repo_remote_root)
            return "done"
        program_3_py = function_to_script(func=func, call_with_args=None, call_with_kwargs={"repo_local_root": str(repo_local_root), "repo_remote_root": str(repo_remote_root)})
        shell_file_3 = get_shell_file_executing_python_script(python_script=program_3_py, ve_path=None, executable="""uv run --with "machineconfig>=6.36" """)
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

        print(f"• {option1:75} 👉 {shell_file_1}")
        print(f"• {option2:75} 👉 {shell_file_2}")
        print(f"• {option3:75} 👉 {shell_file_3}")
        print(f"• {option4:75} 👉 {shell_file_4}")
        print("\n\n")

        program_content = None
        match on_conflict:
            case "ask":
                import questionary
                choice = questionary.select("Choose one option:", choices=[option1, option2, option3, option4]).ask()
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
            case "push-local-merge":
                program_content = shell_file_1.read_text(encoding="utf-8")
            case "overwrite-local":
                program_content = program_2
            case "stop-on-conflict":
                program_content = shell_file_3.read_text(encoding="utf-8")
            case "remove-rclone-conflict":
                program_content = program_4
            case _:
                raise ValueError(f"Unknown action: {on_conflict}")
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script=program_content)
    return program_content

