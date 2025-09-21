"""Repos

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""

import subprocess
from rich import print as pprint
from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.io_save import save_json
from machineconfig.utils.utils2 import randstr, read_json, read_ini
from machineconfig.scripts.python.devops_update_repos import run_uv_sync, update_repository
import argparse
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any


class GitAction(Enum):
    commit = "commit"
    push = "push"
    pull = "pull"


@dataclass
class RepoRecord:
    name: str
    parent_dir: str
    remotes: dict[str, str]  # Fixed: should be dict mapping remote name to URL
    version: dict[str, str]


def git_action(path: PathExtended, action: GitAction, mess: Optional[str] = None, r: bool = False, auto_sync: bool = True) -> bool:
    """Perform git actions using Python instead of shell scripts. Returns True if successful."""
    from git.exc import InvalidGitRepositoryError
    from git.repo import Repo

    try:
        repo = Repo(str(path), search_parent_directories=False)
    except InvalidGitRepositoryError:
        pprint(f"⚠️ Skipping {path} because it is not a git repository.")
        if r:
            results = [git_action(path=sub_path, action=action, mess=mess, r=r, auto_sync=auto_sync) for sub_path in path.search()]
            return all(results)  # Return True only if all recursive operations succeeded
        else:
            return False

    print(f">>>>>>>>> 🔧{action} - {path}")

    try:
        if action == GitAction.commit:
            if mess is None:
                mess = "auto_commit_" + randstr()

            # Check if there are changes to commit
            if repo.is_dirty() or repo.untracked_files:
                repo.git.add(A=True)  # Stage all changes
                repo.index.commit(mess)
                print(f"✅ Committed changes with message: {mess}")
                return True
            else:
                print("ℹ️  No changes to commit")
                return True

        elif action == GitAction.push:
            success = True
            for remote in repo.remotes:
                try:
                    print(f"🚀 Pushing to {remote.url}")
                    remote.push(repo.active_branch.name)
                    print(f"✅ Pushed to {remote.name}")
                except Exception as e:
                    print(f"❌ Failed to push to {remote.name}: {e}")
                    success = False
            return success

        elif action == GitAction.pull:
            # Use the enhanced update function with uv sync support
            update_repository(repo, auto_sync=auto_sync)
            print("✅ Pull completed")
            return True

    except Exception as e:
        print(f"❌ Error performing {action} on {path}: {e}")
        return False

    return True


def main():
    print("\n" + "=" * 50)
    print("📂 Welcome to the Repository Manager")
    print("=" * 50 + "\n")

    parser = argparse.ArgumentParser(description="REPO MANAGER")
    # POSITIONAL
    parser.add_argument("directory", help="📁 Folder containing repos to record or a specs JSON file to follow.", default="")
    # FLAGS
    parser.add_argument("--push", help="🚀 Push changes.", action="store_true")
    parser.add_argument("--pull", help="⬇️ Pull changes.", action="store_true")
    parser.add_argument("--commit", help="💾 Commit changes.", action="store_true")
    parser.add_argument("--all", help="🔄 Pull, commit, and push changes.", action="store_true")
    parser.add_argument("--record", help="📝 Record repositories.", action="store_true")
    parser.add_argument("--clone", help="📥 Clone repositories from record.", action="store_true")
    parser.add_argument("--checkout", help="🔀 Check out to versions provided in a JSON file.", action="store_true")
    parser.add_argument("--checkout_to_branch", help="🔀 Check out to the main branch.", action="store_true")
    parser.add_argument("--recursive", "-r", help="🔍 Recursive flag.", action="store_true")
    parser.add_argument("--no-sync", help="🚫 Disable automatic uv sync after pulls.", action="store_true")
    # OPTIONAL
    parser.add_argument("--cloud", "-c", help="☁️ Cloud storage option.", default=None)
    args = parser.parse_args()

    if args.directory == "":
        repos_root = PathExtended.home().joinpath("code")  # it is a positional argument, can never be empty.
    else:
        repos_root = PathExtended(args.directory).expanduser().absolute()

    auto_sync = not args.no_sync  # Enable auto sync by default, disable with --no-sync

    if args.record:
        print("\n📝 Recording repositories...")
        res = record_repos(repos_root=str(repos_root))
        pprint("✅ Recorded repositories:\n", res)
        save_path = CONFIG_PATH.joinpath("repos").joinpath(repos_root.rel2home()).joinpath("repos.json")
        save_json(obj=res, path=save_path, indent=4)
        pprint(f"📁 Result saved at {PathExtended(save_path)}")
        if args.cloud is not None:
            PathExtended(save_path).to_cloud(rel2home=True, cloud=args.cloud)
        print(">>>>>>>>> Finished Recording")

    elif args.clone or args.checkout or args.checkout_to_branch:
        print("\n📥 Cloning or checking out repositories...")
        print(">>>>>>>>> Cloning Repos")
        if not repos_root.exists() or repos_root.name != "repos.json":  # Fixed: use name instead of stem
            repos_root = PathExtended(CONFIG_PATH).joinpath("repos").joinpath(repos_root.rel2home()).joinpath("repos.json")
            if not repos_root.exists():
                if args.cloud is None:
                    cloud: str = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
                    print(f"⚠️ Using default cloud: {cloud}")
                else:
                    cloud = args.cloud
                    assert cloud is not None, f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
                repos_root.from_cloud(cloud=cloud, rel2home=True)
        assert (repos_root.exists() and repos_root.name == "repos.json") or args.cloud is not None, f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
        success = install_repos_python(specs_path=str(repos_root), clone=args.clone, checkout_to_recorded_commit=args.checkout, checkout_to_branch=args.checkout_to_branch, auto_sync=auto_sync)
        if success:
            print("✅ Repository operations completed successfully")
        else:
            print("⚠️ Some repository operations encountered issues")

    elif args.all or args.commit or args.pull or args.push:
        print(f"\n🔄 Performing Git actions on repositories @ `{repos_root}`...")
        overall_success = True
        for a_path in repos_root.search("*"):
            print(f"{('Handling ' + str(a_path)).center(80, '-')}")
            path_success = True
            if args.pull or args.all:
                path_success = git_action(path=a_path, action=GitAction.pull, r=args.recursive, auto_sync=auto_sync) and path_success
            if args.commit or args.all:
                path_success = git_action(a_path, action=GitAction.commit, r=args.recursive, auto_sync=auto_sync) and path_success
            if args.push or args.all:
                path_success = git_action(a_path, action=GitAction.push, r=args.recursive, auto_sync=auto_sync) and path_success
            overall_success = overall_success and path_success

        if overall_success:
            print("✅ All git operations completed successfully")
        else:
            print("⚠️ Some git operations encountered issues")
    else:
        print("❌ No action specified. Try passing --push, --pull, --commit, or --all.")


def record_repos(repos_root: str, r: bool = True) -> list[dict[str, Any]]:
    path_obj = PathExtended(repos_root).expanduser().absolute()
    if path_obj.is_file():
        return []
    search_res = path_obj.search("*", files=False)
    res: list[dict[str, Any]] = []
    for a_search_res in search_res:
        if a_search_res.joinpath(".git").exists():
            try:
                res.append(record_a_repo(a_search_res))
            except Exception as e:
                print(f"⚠️ Failed to record {a_search_res}: {e}")
        else:
            if r:
                res += record_repos(str(a_search_res), r=r)
    return res


def record_a_repo(path: PathExtended, search_parent_directories: bool = False, preferred_remote: Optional[str] = None):
    from git.repo import Repo

    repo = Repo(path, search_parent_directories=search_parent_directories)  # get list of remotes using git python
    repo_root = PathExtended(repo.working_dir).absolute()
    remotes = {remote.name: remote.url for remote in repo.remotes}
    if preferred_remote is not None:
        if preferred_remote in remotes:
            remotes = {preferred_remote: remotes[preferred_remote]}
        else:
            print(f"⚠️ `{preferred_remote=}` not found in {remotes}.")
            preferred_remote = None
    try:
        commit = repo.head.commit.hexsha
    except ValueError:  # look at https://github.com/gitpython-developers/GitPython/issues/1016
        print(f"⚠️ Failed to get latest commit of {repo}")
        commit = None
    try:
        current_branch = repo.head.reference.name  # same as repo.active_branch.name
    except TypeError:
        print(f"⁉️ Failed to get current branch of {repo}. It is probably in a detached state.")
        current_branch = None
    res: dict[str, Any] = {"name": repo_root.name, "parent_dir": repo_root.parent.collapseuser().as_posix(), "current_branch": current_branch, "remotes": remotes, "version": {"branch": current_branch, "commit": commit}}
    return res


def install_repos_python(specs_path: str, clone: bool = True, checkout_to_recorded_commit: bool = False, checkout_to_branch: bool = False, editable_install: bool = False, preferred_remote: Optional[str] = None, auto_sync: bool = True) -> bool:
    """Python-based repository installation with uv sync support. Returns True if all operations succeeded."""
    from git.repo import Repo
    from git.exc import GitCommandError

    path_obj = PathExtended(specs_path).expanduser().absolute()
    repos: list[dict[str, Any]] = read_json(path_obj)
    overall_success = True

    for repo in repos:
        repo_success = True
        parent_dir = PathExtended(repo["parent_dir"]).expanduser().absolute()
        parent_dir.mkdir(parents=True, exist_ok=True)
        repo_path = parent_dir / repo["name"]

        print(f"\n{'Processing ' + repo['name']:.^80}")

        # Handle cloning and remote setup
        if clone:
            # Select the remote to use for cloning
            if len(repo["remotes"]) == 0:
                print(f"⚠️ No remotes found for {repo['name']}. Skipping clone.")
                repo_success = False
                continue

            remote_name, remote_url = next(iter(repo["remotes"].items()))  # Get first remote by default
            if preferred_remote is not None and preferred_remote in repo["remotes"]:
                remote_name = preferred_remote
                remote_url = repo["remotes"][preferred_remote]
            elif preferred_remote is not None:
                print(f"⚠️ `{preferred_remote=}` not found in {repo['remotes']}.")

            try:
                # Clone with the selected remote
                print(f"📥 Cloning {remote_url} to {repo_path}")
                cloned_repo = Repo.clone_from(remote_url, repo_path, origin=remote_name, depth=2)
                print(f"✅ Successfully cloned {repo['name']}")

                # Add any additional remotes
                for other_remote_name, other_remote_url in repo["remotes"].items():
                    if other_remote_name != remote_name:
                        try:
                            cloned_repo.create_remote(other_remote_name, other_remote_url)
                            print(f"✅ Added remote {other_remote_name}")
                        except Exception as e:
                            print(f"⚠️ Failed to add remote {other_remote_name}: {e}")

            except GitCommandError as e:
                print(f"❌ Failed to clone {repo['name']}: {e}")
                repo_success = False
                continue
            except Exception as e:
                print(f"❌ Unexpected error cloning {repo['name']}: {e}")
                repo_success = False
                continue

        # Handle checkout operations (after cloning/if repo exists)
        if repo_path.exists():
            try:
                existing_repo = Repo(repo_path)

                if checkout_to_recorded_commit:
                    commit = repo["version"]["commit"]
                    if isinstance(commit, str):
                        print(f"🔀 Checking out to commit {commit[:8]}...")
                        existing_repo.git.checkout(commit)
                        print("✅ Checked out to recorded commit")
                    else:
                        print(f"⚠️ Skipping {repo['name']} because it doesn't have a commit recorded. Found {commit}")

                elif checkout_to_branch:
                    if repo.get("current_branch"):
                        print(f"🔀 Checking out to branch {repo['current_branch']}...")
                        existing_repo.git.checkout(repo["current_branch"])
                        print("✅ Checked out to recorded branch")
                    else:
                        print(f"⚠️ No current branch recorded for {repo['name']}")

                # Handle editable install
                if editable_install:
                    pyproject_path = repo_path / "pyproject.toml"
                    if pyproject_path.exists():
                        print(f"📦 Installing {repo['name']} in editable mode...")
                        result = subprocess.run(["uv", "pip", "install", "-e", "."], cwd=repo_path, capture_output=True, text=True)
                        if result.returncode == 0:
                            print("✅ Editable install completed")
                        else:
                            print(f"❌ Editable install failed: {result.stderr}")
                            repo_success = False
                    else:
                        print(f"⚠️ No pyproject.toml found in {repo['name']}, skipping editable install")

                # Run uv sync if auto_sync is enabled and pyproject.toml exists
                if auto_sync and (repo_path / "pyproject.toml").exists():
                    sync_success = run_uv_sync(repo_path)
                    if not sync_success:
                        repo_success = False

            except Exception as e:
                print(f"❌ Error processing existing repository {repo['name']}: {e}")
                repo_success = False

        overall_success = overall_success and repo_success

    return overall_success


def install_repos(specs_path: str, clone: bool = True, checkout_to_recorded_commit: bool = False, checkout_to_branch: bool = False, editable_install: bool = False, preferred_remote: Optional[str] = None):
    program = ""
    path_obj = PathExtended(specs_path).expanduser().absolute()
    repos: list[dict[str, Any]] = read_json(path_obj)
    for repo in repos:
        parent_dir = PathExtended(repo["parent_dir"]).expanduser().absolute()
        parent_dir.mkdir(parents=True, exist_ok=True)

        # Handle cloning and remote setup
        if clone:
            # Select the remote to use for cloning
            if len(repo["remotes"]) == 0:
                print(f"⚠️ No remotes found for {repo['name']}. Skipping clone.")
                continue
            remote_name, remote_url = next(iter(repo["remotes"].items()))  # Get first remote by default
            if preferred_remote is not None and preferred_remote in repo["remotes"]:
                remote_name = preferred_remote
                remote_url = repo["remotes"][preferred_remote]
            elif preferred_remote is not None:
                print(f"⚠️ `{preferred_remote=}` not found in {repo['remotes']}.")

            # Clone with the selected remote
            program += f"\ncd {parent_dir.collapseuser().as_posix()}; git clone {remote_url} --origin {remote_name} --depth 2"
            program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git remote set-url {remote_name} {remote_url}"

            # Add any additional remotes
            for other_remote_name, other_remote_url in repo["remotes"].items():
                if other_remote_name != remote_name:
                    program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git remote add {other_remote_name} {other_remote_url}"

        # Handle checkout operations (after all remotes are set up)
        if checkout_to_recorded_commit:
            commit = repo["version"]["commit"]
            if isinstance(commit, str):
                program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git checkout {commit}"
            else:
                print(f"Skipping {repo['parent_dir']} because it doesn't have a commit recorded. Found {commit}")
        elif checkout_to_branch:
            program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git checkout {repo['current_branch']}"

        # Handle editable install
        if editable_install:
            program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; uv pip install -e ."

        program += "\n"
    pprint(program)
    return program


if __name__ == "__main__":
    main()
