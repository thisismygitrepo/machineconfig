from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.schemas.repos.repos_types import GitVersionInfo, RepoRecordDict, RepoRemote

from machineconfig.utils.schemas.repos.repos_types import RepoRecordFile
from machineconfig.utils.source_of_truth import CONFIG_PATH
from machineconfig.utils.io_save import save_json

from typing import Optional

from rich import print as pprint
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn


def build_tree_structure(repos: list[RepoRecordDict], repos_root: PathExtended) -> str:
    """Build a tree structure representation of all repositories."""
    if not repos:
        return "No repositories found."

    # Group repos by their parent directories relative to repos_root
    tree_dict: dict[str, list[RepoRecordDict]] = {}
    repos_root_abs = repos_root.expanduser().absolute()

    for repo in repos:
        parent_path = PathExtended(repo["parentDir"]).expanduser().absolute()
        try:
            relative_path = parent_path.relative_to(repos_root_abs)
            relative_str = str(relative_path) if str(relative_path) != "." else ""
        except ValueError:
            # If the path is not relative to repos_root, use the full path
            relative_str = str(parent_path)

        if relative_str not in tree_dict:
            tree_dict[relative_str] = []
        tree_dict[relative_str].append(repo)

    # Sort directories for consistent output
    sorted_dirs = sorted(tree_dict.keys())

    tree_lines: list[str] = []
    tree_lines.append(f"📂 {repos_root.name}/ ({repos_root_abs})")

    for i, dir_path in enumerate(sorted_dirs):
        is_last_dir = i == len(sorted_dirs) - 1
        dir_prefix = "└── " if is_last_dir else "├── "

        if dir_path:
            tree_lines.append(f"│   {dir_prefix}📁 {dir_path}/")
            repo_prefix_base = "│   │   " if not is_last_dir else "    "
        else:
            repo_prefix_base = "│   "

        repos_in_dir = tree_dict[dir_path]
        # Sort repos by name
        repos_in_dir.sort(key=lambda x: x["name"])

        for j, repo in enumerate(repos_in_dir):
            is_last_repo = j == len(repos_in_dir) - 1
            repo_prefix = f"{repo_prefix_base}└── " if is_last_repo else f"{repo_prefix_base}├── "

            # Create status indicators
            status_indicators = []
            if repo["isDirty"]:
                status_indicators.append("🔶 DIRTY")
            if not repo["remotes"]:
                status_indicators.append("⚠️ NO_REMOTE")
            if repo["currentBranch"] == "DETACHED":
                status_indicators.append("🔀 DETACHED")

            status_str = f"[{' | '.join(status_indicators)}]" if status_indicators else "[✅ CLEAN]"
            branch_info = f" ({repo['currentBranch']})" if repo["currentBranch"] != "DETACHED" else ""

            # Build the base string without status
            base_str = f"{repo_prefix}📦 {repo['name']}{branch_info}"

            # Calculate padding to align status at 75 characters
            target_width = 45
            current_length = len(base_str)
            padding = max(1, target_width - current_length)  # At least 1 space

            tree_lines.append(f"{base_str}{' ' * padding}{status_str}")

    return "\n".join(tree_lines)


def record_a_repo(path: PathExtended, search_parent_directories: bool, preferred_remote: Optional[str]) -> RepoRecordDict:
    from git.repo import Repo

    repo = Repo(path, search_parent_directories=search_parent_directories)  # get list of remotes using git python
    repo_root = PathExtended(repo.working_dir).absolute()
    # remotes: = {remote.name: remote.url for remote in repo.remotes}
    remotes: list[RepoRemote] = [{"name": remote.name, "url": remote.url} for remote in repo.remotes]
    if preferred_remote is not None:
        if preferred_remote in [remote["name"] for remote in remotes]:
            remotes = [remote for remote in remotes if remote["name"] == preferred_remote]
        else:
            print(f"⚠️ `{preferred_remote=}` not found in {remotes}.")
            preferred_remote = None
    try:
        commit = repo.head.commit.hexsha
    except ValueError:  # look at https://github.com/gitpython-developers/GitPython/issues/1016
        print(f"⚠️ Failed to get latest commit of {repo}")
        commit = "UNKNOWN"
    try:
        current_branch = repo.head.reference.name  # same as repo.active_branch.name
    except TypeError:
        print(f"⁉️ Failed to get current branch of {repo}. It is probably in a detached state.")
        # current_branch = None
        current_branch = "DETACHED"

    # Check if repo is dirty (has uncommitted changes)
    is_dirty = repo.is_dirty(untracked_files=True)

    version_info: GitVersionInfo = {"branch": current_branch, "commit": commit}

    res: RepoRecordDict = {"name": repo_root.name, "parentDir": repo_root.parent.collapseuser().as_posix(), "currentBranch": current_branch, "remotes": remotes, "version": version_info, "isDirty": is_dirty}
    return res


def count_git_repositories(repos_root: str, r: bool) -> int:
    """Count total git repositories for accurate progress tracking."""
    path_obj = PathExtended(repos_root).expanduser().absolute()
    if path_obj.is_file():
        return 0

    search_res = path_obj.search("*", files=False, folders=True)
    count = 0

    for a_search_res in search_res:
        if a_search_res.joinpath(".git").exists():
            count += 1
        elif r:
            count += count_git_repositories(str(a_search_res), r=r)

    return count


def count_total_directories(repos_root: str, r: bool) -> int:
    """Count total directories to scan for accurate progress tracking."""
    path_obj = PathExtended(repos_root).expanduser().absolute()
    if path_obj.is_file():
        return 0

    search_res = path_obj.search("*", files=False, folders=True)
    count = len(search_res)

    if r:
        for a_search_res in search_res:
            if not a_search_res.joinpath(".git").exists():
                count += count_total_directories(str(a_search_res), r=r)

    return count


def record_repos_recursively(repos_root: str, r: bool, progress: Progress | None, scan_task_id: TaskID | None, process_task_id: TaskID | None) -> list[RepoRecordDict]:
    path_obj = PathExtended(repos_root).expanduser().absolute()
    if path_obj.is_file():
        return []

    search_res = path_obj.search("*", files=False, folders=True)
    res: list[RepoRecordDict] = []

    for a_search_res in search_res:
        if progress and scan_task_id:
            progress.update(scan_task_id, description=f"Scanning: {a_search_res.name}")

        if a_search_res.joinpath(".git").exists():
            try:
                if progress and process_task_id:
                    progress.update(process_task_id, description=f"Recording: {a_search_res.name}")

                repo_record = record_a_repo(a_search_res, search_parent_directories=False, preferred_remote=None)
                res.append(repo_record)

                if progress and process_task_id:
                    progress.update(process_task_id, advance=1, description=f"Recorded: {repo_record['name']}")
            except Exception as e:
                print(f"⚠️ Failed to record {a_search_res}: {e}")
        else:
            if r:
                res += record_repos_recursively(str(a_search_res), r=r, progress=progress, scan_task_id=scan_task_id, process_task_id=process_task_id)

        if progress and scan_task_id:
            progress.update(scan_task_id, advance=1)

    return res


def main(repos_root: PathExtended):
    print("\n📝 Recording repositories...")

    # Count total directories and repositories for accurate progress tracking
    print("🔍 Analyzing directory structure...")
    total_dirs = count_total_directories(str(repos_root), r=True)
    total_repos = count_git_repositories(str(repos_root), r=True)
    print(f"📊 Found {total_dirs} directories to scan and {total_repos} git repositories to record")

    # Setup progress bars
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as progress:
        scan_task = progress.add_task("Scanning directories...", total=total_dirs)
        process_task = progress.add_task("Recording repositories...", total=total_repos)

        repo_records = record_repos_recursively(repos_root=str(repos_root), r=True, progress=progress, scan_task_id=scan_task, process_task_id=process_task)

    res: RepoRecordFile = {"version": "0.1", "repos": repo_records}

    # Summary with warnings
    total_repos = len(repo_records)
    repos_with_no_remotes = [repo for repo in repo_records if len(repo["remotes"]) == 0]
    repos_with_remotes = [repo for repo in repo_records if len(repo["remotes"]) > 0]
    dirty_repos = [repo for repo in repo_records if repo["isDirty"]]
    clean_repos = [repo for repo in repo_records if not repo["isDirty"]]

    print("\n📊 Repository Summary:")
    print(f"   Total repositories found: {total_repos}")
    print(f"   Repositories with remotes: {len(repos_with_remotes)}")
    print(f"   Repositories without remotes: {len(repos_with_no_remotes)}")
    print(f"   Clean repositories: {len(clean_repos)}")
    print(f"   Dirty repositories: {len(dirty_repos)}")

    if repos_with_no_remotes:
        print(f"\n⚠️  WARNING: {len(repos_with_no_remotes)} repositories have no remotes configured:")
        for repo in repos_with_no_remotes:
            repo_path = PathExtended(repo["parentDir"]).joinpath(repo["name"])
            print(f"   • {repo['name']} ({repo_path})")
        print("   These repositories may be local-only or have configuration issues.")
    else:
        print("\n✅ All repositories have remote configurations.")

    if dirty_repos:
        print(f"\n⚠️  WARNING: {len(dirty_repos)} repositories have uncommitted changes:")
        for repo in dirty_repos:
            repo_path = PathExtended(repo["parentDir"]).joinpath(repo["name"])
            print(f"   • {repo['name']} ({repo_path}) [branch: {repo['currentBranch']}]")
        print("   These repositories have uncommitted changes that may need attention.")
    else:
        print("\n✅ All repositories are clean (no uncommitted changes).")

    # Display repository tree structure
    print("\n🌳 Repository Tree Structure:")
    tree_structure = build_tree_structure(repo_records, repos_root)
    print(tree_structure)

    save_path = CONFIG_PATH.joinpath("repos").joinpath(repos_root.rel2home()).joinpath("repos.json")
    save_json(obj=res, path=save_path, indent=4)
    pprint(f"📁 Result saved at {PathExtended(save_path)}")
    print(">>>>>>>>> Finished Recording")
    return save_path
