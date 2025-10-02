from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.code import write_shell_script_to_file
import platform
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def get_zellij_cmd(wd1: Path, wd2: Path) -> str:
    _ = wd1, wd2
    lines = [
        """ zellij action new-tab --name gitdiff""",
        """zellij action new-pane --direction down --name local --cwd ./data """,
        """zellij action write-chars "cd '{wd1}'; git status" """,
        """zellij action move-focus up; zellij action close-pane """,
        """zellij action new-pane --direction down --name remote --cwd code """,
        """zellij action write-chars "cd '{wd2}' """,
        """git status" """,
    ]
    return "; ".join(lines)

def delete_remote_repo_copy_and_push_local(remote_repo: str, local_repo: str, cloud: str):
    console.print(Panel("🗑️  Deleting remote repo copy and pushing local copy", title="[bold blue]Repo Sync[/bold blue]", border_style="blue"))
    repo_sync_root = PathExtended(remote_repo).expanduser().absolute()
    repo_root_path = PathExtended(local_repo).expanduser().absolute()
    repo_sync_root.delete(sure=True)
    print("🧹 Removed temporary remote copy")
    from git.remote import Remote
    from git.repo import Repo

    try:
        Remote.remove(Repo(repo_root_path), "originEnc")
        console.print(Panel("🔗 Removed originEnc remote reference", border_style="blue"))
    except Exception:
        pass  # type: ignore
    console.print(Panel("📈 Deleting remote repository copy and pushing local changes", width=150, border_style="blue"))

    repo_root_path.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, os_specific=False)

    console.print(Panel("✅ Repository successfully pushed to cloud", title="[bold green]Repo Sync[/bold green]", border_style="green"))



def get_wt_cmd(wd1: PathExtended, wd2: PathExtended) -> str:
    lines = [
        f"""wt --window 0 new-tab --profile pwsh --title "gitdiff" --tabColor `#3b04d1 --startingDirectory {wd1} ` --colorScheme "Solarized Dark" """,
        f"""split-pane --horizontal --profile pwsh --startingDirectory {wd2} --size 0.5 --colorScheme "Tango Dark" -- pwsh -Interactive """,
    ]
    return " `; ".join(lines)


def inspect_repos(repo_local_root: str, repo_remote_root: str):
    console.print(Panel(f"📂 Local:  {repo_local_root}\n📂 Remote: {repo_remote_root}", title="[bold blue]🔍 Inspecting Repositories[/bold blue]", border_style="blue"))

    if platform.system() == "Windows":
        program = get_wt_cmd(wd1=PathExtended(repo_local_root), wd2=PathExtended(repo_local_root))
        write_shell_script_to_file(shell_script=program)
        return None
    elif platform.system() in ["Linux", "Darwin"]:
        program = get_zellij_cmd(wd1=PathExtended(repo_local_root), wd2=PathExtended(repo_remote_root))
        write_shell_script_to_file(shell_script=program)
        return None
    else:
        raise NotImplementedError(f"Platform {platform.system()} not implemented.")


def check_dotfiles_version_is_beyond(commit_dtm: str, update: bool) -> bool:
    dotfiles_path = str(PathExtended.home().joinpath("dotfiles"))
    from git import Repo

    repo = Repo(path=dotfiles_path)
    last_commit = repo.head.commit
    dtm = last_commit.committed_datetime
    from datetime import datetime  # make it tz unaware

    dtm = datetime(dtm.year, dtm.month, dtm.day, dtm.hour, dtm.minute, dtm.second)
    res = dtm > datetime.fromisoformat(commit_dtm)
    if res is False and update is True:
        console = Console()
        console.print(Panel(f"🔄 UPDATE REQUIRED | Updating dotfiles because {dtm} < {datetime.fromisoformat(commit_dtm)}", border_style="bold blue", expand=False))
        from machineconfig.scripts.python.cloud_repo_sync import main

        main(cloud=None, path=dotfiles_path)
    return res
