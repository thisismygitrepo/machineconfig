

from typing import Optional, Literal, Annotated
import typer

def get_tmp_file():
    from pathlib import Path
    import platform
    from machineconfig.utils.accessories import randstr
    name = randstr(8)
    if platform.system() == "Windows":
        suffix = "ps1"
    else:
        suffix = "sh"
    tmp_file = Path.home().joinpath(f"tmp_results/tmp_files/{name}.{suffix}")
    tmp_file.parent.mkdir(parents=True, exist_ok=True)
    return tmp_file


def main(
    cloud: Annotated[Optional[str], typer.Option(..., "--cloud", "-c", help="Cloud storage profile name. If not provided, uses default from config.")] = None,
    repo: Annotated[Optional[str], typer.Option(..., "--repo", "-r", help="Path to the local repository. Defaults to current working directory.")] = None,
    message: Annotated[Optional[str], typer.Option(..., "--message", "-m", help="Commit message for local changes.")] = None,
    on_conflict: Annotated[Literal["ask", "a",
                                   "push-local-merge", "p",
                                   "overwrite-local", "o",
                                   "stop-on-conflict", "s",
                                   "remove-rclone-conflict", "r"
                                   ], typer.Option(..., "--on-conflict", "-o", help="Action to take on merge conflict. Default is 'ask'.")] = "ask",
    pwd: Annotated[Optional[str], typer.Option(..., "--password", help="Password for encryption/decryption of the remote repository.")] = None,
):
    on_conflict_mapper: dict[str, Literal["ask", "push-local-merge", "overwrite-local", "stop-on-conflict", "remove-rclone-conflict"]] = {
        "a": "ask",
        "ask": "ask",
        "p": "push-local-merge",
        "push-local-merge": "push-local-merge",
        "o": "overwrite-local",
        "overwrite-local": "overwrite-local",
        "s": "stop-on-conflict",
        "stop-on-conflict": "stop-on-conflict",
        "r": "remove-rclone-conflict",
        "remove-rclone-conflict": "remove-rclone-conflict",
    }
    on_conflict = on_conflict_mapper[on_conflict]
    import platform
    import git
    from rich.console import Console
    from rich.panel import Panel

    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.utils.terminal import Response
    from machineconfig.utils.source_of_truth import CONFIG_ROOT, DEFAULTS_PATH
    from machineconfig.utils.code import get_uv_command_executing_python_script
    from pathlib import Path
    import subprocess
    console = Console()

    def _bash_single_quote(val: str) -> str:
        return "'" + val.replace("'", "'\"'\"'") + "'"

    def _ps_single_quote(val: str) -> str:
        return "'" + val.replace("'", "''") + "'"

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
    try:
        repo_local_obj = git.Repo(repo_local_root, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        typer.echo(f"[red]Error:[/] The specified path '{repo_local_root}' is not a valid git repository.")
        typer.Exit(code=1)
        return ""
    repo_local_root = PathExtended(repo_local_obj.working_dir)  # cwd might have been in a sub directory of repo_root, so its better to redefine it.
    local_relative_home = PathExtended(repo_local_root.expanduser().absolute().relative_to(Path.home()))
    PathExtended(CONFIG_ROOT).joinpath("remote").mkdir(parents=True, exist_ok=True)
    repo_remote_root = PathExtended(CONFIG_ROOT).joinpath("remote", local_relative_home)
    repo_remote_root.delete(sure=True)
    try:
        console.print(Panel("📥 DOWNLOADING REMOTE REPOSITORY", title_align="left", border_style="blue"))
        remote_path = repo_local_root.get_remote_path(rel2home=True, os_specific=False, root="myhome") + ".zip.enc"
        res = repo_remote_root.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific=False, pwd=pwd)
        if res is None:
            raise AssertionError("Remote repo does not exist.")
    except AssertionError:
        console.print(Panel("🆕 Remote repository doesn't exist\n📤 Creating new remote and exiting...", title_align="left", border_style="green"))
        repo_local_root.to_cloud(cloud=cloud_resolved, zip=True, encrypt=True, rel2home=True, pwd=pwd, os_specific=False)
        return ""

    repo_remote_obj = git.Repo(repo_remote_root)
    if repo_remote_obj.is_dirty():
        console.print(Panel(f"⚠️  WARNING: REMOTE REPOSITORY IS DIRTY\nLocation: {repo_remote_root}\nPlease commit or stash changes before proceeding.", title="Warning", border_style="yellow"))

    message_resolved = "sync" if message is None or message.strip() == "" else message

    repo_local_root_str = str(repo_local_root)
    repo_remote_root_str = str(repo_remote_root)

    script_bash = f"""
echo ""
echo -e "\\033[1;34m═════ COMMITTING LOCAL CHANGES ═════\\033[0m"
cd {_bash_single_quote(repo_local_root_str)}
git status
git add -A
if git diff --cached --quiet; then
  echo "-> No staged changes to commit."
else
  git commit -m {_bash_single_quote(message_resolved)} || true
fi
echo ""
echo ""
echo -e "\\033[1;34m═════ PULLING LATEST FROM REMOTE ═════\\033[0m"
cd {_bash_single_quote(repo_local_root_str)}
echo "-> Trying to removing originEnc remote from local repo if it exists."
git remote remove originEnc 2>/dev/null || true
echo "-> Adding originEnc remote to local repo"
git remote add originEnc {_bash_single_quote(repo_remote_root_str)}
echo "-> Fetching originEnc remote."
git pull originEnc master

"""

    script_powershell = f"""
Write-Host ""
Write-Host "═════ COMMITTING LOCAL CHANGES ═════" -ForegroundColor Blue
Set-Location -LiteralPath {_ps_single_quote(repo_local_root_str)}
git status
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {{
    Write-Host "-> No staged changes to commit."
}} else {{
    git commit -m {_ps_single_quote(message_resolved)}
    if ($LASTEXITCODE -ne 0) {{
        Write-Host "-> Commit skipped/failed (continuing)."
    }}
}}

Write-Host ""
Write-Host ""
Write-Host "═════ PULLING LATEST FROM REMOTE ═════" -ForegroundColor Blue
Set-Location -LiteralPath {_ps_single_quote(repo_local_root_str)}
Write-Host "-> Trying to remove originEnc remote from local repo if it exists."
git remote remove originEnc 2>$null
Write-Host "-> Adding originEnc remote to local repo"
git remote add originEnc {_ps_single_quote(repo_remote_root_str)}
Write-Host "-> Fetching originEnc remote."
git pull originEnc master
exit $LASTEXITCODE
"""

    script = script_powershell if platform.system() == "Windows" else script_bash

    if Path.home().joinpath("code/machineconfig").exists():
        uv_project_dir = f"""{str(Path.home().joinpath("code/machineconfig"))}"""
        uv_with = None
    else:
        uv_with = ["machineconfig>=8.37"]
        uv_project_dir = None

    shell_path = get_tmp_file()
    shell_path.write_text(script, encoding="utf-8")
    if platform.system() == "Windows":
        completed = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(shell_path)],
            capture_output=True,
            check=False,
            text=True,
        )
    else:
        completed = subprocess.run(
            ["bash", str(shell_path)],
            capture_output=True,
            check=False,
            text=True,
        )
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
        from machineconfig.utils.meta import lambda_to_python_script
        def func2(remote_repo: str, local_repo: str, cloud: str):
            from machineconfig.scripts.python.helpers.helpers_repos.sync import delete_remote_repo_copy_and_push_local
            delete_remote_repo_copy_and_push_local(remote_repo=remote_repo, local_repo=local_repo, cloud=cloud)
        program_1_py = lambda_to_python_script(lambda: func2(remote_repo=str(repo_remote_root), local_repo=str(repo_local_root), cloud=str(cloud_resolved)),
                                                        in_global=True, import_module=False)
        program1, _pyfile1 = get_uv_command_executing_python_script(python_script=program_1_py, uv_with=uv_with, uv_project_dir=uv_project_dir)
        # ================================================================================

        option2 = "Delete local repo and replace it with remote copy:"
        if platform.system() == "Windows":
            program_2 = f"""
Remove-Item -LiteralPath {_ps_single_quote(repo_local_root_str)} -Recurse -Force -ErrorAction SilentlyContinue
Move-Item -LiteralPath {_ps_single_quote(repo_remote_root_str)} -Destination {_ps_single_quote(repo_local_root_str)} -Force
    """
        else:
            program_2 = f"""
rm -rfd {_bash_single_quote(repo_local_root_str)}
mv {_bash_single_quote(repo_remote_root_str)} {_bash_single_quote(repo_local_root_str)}
    """
        if platform.system() in ["Linux", "Darwin"]:
            program_2 += """
sudo chmod 600 $HOME/.ssh/*
sudo chmod 700 $HOME/.ssh
sudo chmod +x $HOME/dotfiles/scripts/linux -R
"""
        shell_file_2 = get_tmp_file()
        shell_file_2.write_text(program_2, encoding="utf-8")

        # ================================================================================
        option3 = "Inspect repos:"
        def func(repo_local_root: str, repo_remote_root: str):
            from machineconfig.scripts.python.helpers.helpers_repos.sync import inspect_repos
            inspect_repos(repo_local_root=repo_local_root, repo_remote_root=repo_remote_root)
        # program_3_py = function_to_script(func=func, call_with_kwargs={"repo_local_root": str(repo_local_root), "repo_remote_root": str(repo_remote_root)})
        # shell_file_3 = get_shell_file_executing_python_script(python_script=program_3_py, ve_path=None, executable=executable)
        program_3_py = lambda_to_python_script(lambda: func(repo_local_root=str(repo_local_root), repo_remote_root=str(repo_remote_root)),
                                                        in_global=True, import_module=False)
        program3, _pyfile3 = get_uv_command_executing_python_script(python_script=program_3_py, uv_with=uv_with, uv_project_dir=uv_project_dir)
        # ================================================================================

        option4 = "Remove problematic rclone file from repo and replace with remote:"
        if platform.system() == "Windows":
            program_4 = f"""
Remove-Item -LiteralPath "$HOME/dotfiles/creds/rclone/rclone.conf" -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "$HOME/dotfiles/creds/rclone" -Force | Out-Null
Copy-Item -LiteralPath "$HOME/.config/machineconfig/remote/dotfiles/creds/rclone/rclone.conf" -Destination "$HOME/dotfiles/creds/rclone/rclone.conf" -Force
Set-Location -LiteralPath "$HOME/dotfiles"
git commit -am "finished merging"
{program1}
    """
        else:
            program_4 = f"""
rm $HOME/dotfiles/creds/rclone/rclone.conf
cp $HOME/.config/machineconfig/remote/dotfiles/creds/rclone/rclone.conf $HOME/dotfiles/creds/rclone
cd $HOME/dotfiles
git commit -am "finished merging"
{program1}
    """
        shell_file_4 = get_tmp_file()
        shell_file_4.write_text(program_4, encoding="utf-8")
        # ================================================================================

        console.print(Panel("🔄 RESOLVE MERGE CONFLICT\nChoose an option to resolve the conflict:", title_align="left", border_style="blue"))

        print(f"• {option1:75} 👉 {program1}")
        print(f"• {option2:75} 👉 {shell_file_2}")
        print(f"• {option3:75} 👉 {program3}")
        print(f"• {option4:75} 👉 {shell_file_4}")
        print("\n\n")

        program_content = None
        match on_conflict:
            case "ask":
                import questionary
                choice = questionary.select("Choose one option:", choices=[option1, option2, option3, option4]).ask()
                if choice == option1:
                    program_content = program1
                elif choice == option2:
                    program_content = program_2
                elif choice == option3:
                    program_content = program3
                elif choice == option4:
                    program_content = program_4
                else:
                    raise NotImplementedError(f"Choice {choice} not implemented.")
            case "push-local-merge":
                program_content = program1
            case "overwrite-local":
                program_content = program_2
            case "stop-on-conflict":
                program_content = program3
            case "remove-rclone-conflict":
                program_content = program_4
            case _:
                raise ValueError(f"Unknown action: {on_conflict}")
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script=program_content)
    return program_content

