
from pathlib import Path
from typing import Literal, Optional, cast

from git import Repo as GitRepo
from git.exc import GitCommandError
from rich import print as pprint
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from machineconfig.utils.schemas.repos.repos_types import RepoRecordDict, RepoRecordFile, RepoRemote
from machineconfig.utils.io import read_json


CloneStatus = Literal["cloned", "skipped", "failed"]


def choose_remote(remotes: list[RepoRemote], preferred_remote: Optional[str]) -> Optional[RepoRemote]:
    if preferred_remote is not None:
        for remote in remotes:
            if remote["name"] == preferred_remote:
                return remote
    for remote in remotes:
        if remote["name"] == "origin":
            return remote
    return remotes[0] if len(remotes) > 0 else None


def ensure_destination(parent_dir: str, name: str) -> Path:
    parent_path = Path(parent_dir).expanduser().absolute()
    parent_path.mkdir(parents=True, exist_ok=True)
    return parent_path.joinpath(name)


def checkout_branch(repo: GitRepo, branch: str) -> bool:
    if branch == "DETACHED":
        return False
    current_branch = repo.active_branch.name if not repo.head.is_detached else None
    if current_branch == branch:
        return False
    repo.git.checkout(branch)
    return True


def checkout_commit(repo: GitRepo, commit: str) -> bool:
    if commit in {"", "UNKNOWN"}:
        return False
    current_commit = repo.head.commit.hexsha
    if current_commit == commit:
        return False
    repo.git.checkout(commit)
    return True


def clone_single_repo(repo_spec: RepoRecordDict, preferred_remote: Optional[str], checkout_branch_flag: bool, checkout_commit_flag: bool) -> tuple[CloneStatus, str]:
    destination = ensure_destination(parent_dir=repo_spec["parentDir"], name=repo_spec["name"])
    repo_path = destination.joinpath(".git")
    remotes = repo_spec["remotes"]
    if len(remotes) == 0:
        return ("failed", f"No remotes configured for {destination}")
    remote = choose_remote(remotes=remotes, preferred_remote=preferred_remote)
    if remote is None:
        return ("failed", f"No usable remote for {destination}")
    repo = None
    status: CloneStatus
    message: str
    if destination.exists() and repo_path.exists():
        status = "skipped"
        repo = GitRepo(str(destination))
        message = f"Skipped cloning for {destination}; existing repository reused"
    elif destination.exists() and not repo_path.exists():
        return ("failed", f"Destination exists but is not a git repository: {destination}")
    else:
        try:
            pprint(f"📥 Cloning {repo_spec['name']} from {remote['url']}")
            repo = GitRepo.clone_from(url=remote["url"], to_path=str(destination))
            status = "cloned"
            message = f"Cloned {destination}"
        except Exception as err:  # noqa: BLE001
            return ("failed", f"Clone failed for {destination}: {err}")
    assert repo is not None
    checkout_summary: list[str] = []
    try:
        if checkout_branch_flag:
            if checkout_branch(repo=repo, branch=repo_spec["version"]["branch"]):
                checkout_summary.append(f"branch {repo_spec['version']['branch']}")
        if checkout_commit_flag:
            if checkout_commit(repo=repo, commit=repo_spec["version"]["commit"]):
                checkout_summary.append(f"commit {repo_spec['version']['commit'][:8]}")
    except GitCommandError as err:
        return ("failed", f"Checkout failed for {destination}: {err}")
    if len(checkout_summary) > 0:
        message = f"{message} | Checked out {' & '.join(checkout_summary)}"
    return (status, message)


def clone_repos(spec_path: Path, preferred_remote: Optional[str], checkout_branch_flag: bool, checkout_commit_flag: bool) -> list[tuple[CloneStatus, str]]:
    spec_file = cast(RepoRecordFile, read_json(path=spec_path))
    repos = spec_file["repos"]
    results: list[tuple[CloneStatus, str]] = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as progress:
        task_id = progress.add_task("Processing repositories...", total=len(repos))
        for repo_spec in repos:
            progress.update(task_id, description=f"Processing {repo_spec['name']}")
            try:
                result = clone_single_repo(repo_spec=repo_spec, preferred_remote=preferred_remote, checkout_branch_flag=checkout_branch_flag, checkout_commit_flag=checkout_commit_flag)
            except Exception as err:  # noqa: BLE001
                result = ("failed", f"Unexpected error for {repo_spec['name']}: {err}")
            results.append(result)
            if result[0] == "failed":
                pprint(f"❌ {result[1]}")
            elif result[0] == "cloned":
                pprint(f"✅ {result[1]}")
            else:
                pprint(f"⏭️ {result[1]}")
            progress.update(task_id, advance=1)
    success_count = len([status for status, _ in results if status == "cloned"])
    skip_count = len([status for status, _ in results if status == "skipped"])
    fail_count = len([status for status, _ in results if status == "failed"])
    pprint(f"✅ Cloned: {success_count} | ⏭️ Skipped: {skip_count} | ❌ Failed: {fail_count}")
    return results
