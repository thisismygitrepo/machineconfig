"""Repos

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""

from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH
from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.utils.accessories import randstr
from machineconfig.scripts.python.repos_helper_update import update_repository
from machineconfig.scripts.python.repos_helper_record import main as record_repos
from machineconfig.scripts.python.repos_helper_clone import clone_repos

import typer
from enum import Enum
from typing import Annotated, Optional

from rich import print as pprint


class GitAction(Enum):
    commit = "commit"
    push = "push"
    pull = "pull"


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
            update_repository(repo, auto_sync=auto_sync, allow_password_prompt=False)
            print("✅ Pull completed")
            return True

    except Exception as e:
        print(f"❌ Error performing {action} on {path}: {e}")
        return False

    return True


def main(
    directory: Annotated[str, typer.Argument(help="📁 Folder containing repos to record or a specs JSON file to follow.")] = "",
    push: Annotated[bool, typer.Option("--push", help="🚀 Push changes.")] = False,
    pull: Annotated[bool, typer.Option("--pull", help="⬇️ Pull changes.")] = False,
    commit: Annotated[bool, typer.Option("--commit", help="💾 Commit changes.")] = False,
    all: Annotated[bool, typer.Option("--all", help="🔄 Pull, commit, and push changes.")] = False,
    record: Annotated[bool, typer.Option("--record", help="📝 Record repositories.")] = False,
    clone: Annotated[bool, typer.Option("--clone", help="📥 Clone repositories from record.")] = False,
    checkout: Annotated[bool, typer.Option("--checkout", help="🔀 Check out to versions provided in a JSON file.")] = False,
    checkout_to_branch: Annotated[bool, typer.Option("--checkout-to-branch", help="🔀 Check out to the main branch.")] = False,
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="🔍 Recursive flag.")] = False,
    no_sync: Annotated[bool, typer.Option("--no-sync", help="🚫 Disable automatic uv sync after pulls.")] = False,
    cloud: Annotated[Optional[str], typer.Option("--cloud", "-c", help="☁️ Cloud storage option.")] = None,
) -> None:
    print("\n" + "=" * 50)
    print("📂 Welcome to the Repository Manager")
    print("=" * 50 + "\n")

    if directory == "":
        repos_root = PathExtended.home().joinpath("code")  # it is a positional argument, can never be empty.
    else:
        repos_root = PathExtended(directory).expanduser().absolute()

    auto_sync = not no_sync  # Enable auto sync by default, disable with --no-sync

    if record:
        save_path = record_repos(repos_root=repos_root)
        if cloud is not None:
            PathExtended(save_path).to_cloud(rel2home=True, cloud=cloud)

    elif clone or checkout or checkout_to_branch:
        print("\n📥 Cloning or checking out repositories...")
        print(">>>>>>>>> Cloning Repos")
        if not repos_root.exists() or repos_root.name != "repos.json":
            repos_root = PathExtended(CONFIG_PATH).joinpath("repos").joinpath(repos_root.rel2home()).joinpath("repos.json")
            if not repos_root.exists():
                if cloud is None:
                    cloud_name: str = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
                    print(f"⚠️ Using default cloud: {cloud_name}")
                else:
                    cloud_name = cloud
                    assert cloud_name is not None, f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
                repos_root.from_cloud(cloud=cloud_name, rel2home=True)
        assert (repos_root.exists() and repos_root.name == "repos.json") or cloud is not None, f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
        clone_repos(spec_path=repos_root, preferred_remote=None, checkout_branch_flag=checkout_to_branch, checkout_commit_flag=checkout)

    elif all or commit or pull or push:
        print(f"\n🔄 Performing Git actions on repositories @ `{repos_root}`...")
        overall_success = True
        for a_path in repos_root.search("*"):
            print(f"{('Handling ' + str(a_path)).center(80, '-')}")
            path_success = True
            if pull or all:
                path_success = git_action(path=a_path, action=GitAction.pull, r=recursive, auto_sync=auto_sync) and path_success
            if commit or all:
                path_success = git_action(a_path, action=GitAction.commit, r=recursive, auto_sync=auto_sync) and path_success
            if push or all:
                path_success = git_action(a_path, action=GitAction.push, r=recursive, auto_sync=auto_sync) and path_success
            overall_success = overall_success and path_success

        if overall_success:
            print("✅ All git operations completed successfully")
        else:
            print("⚠️ Some git operations encountered issues")
    else:
        print("❌ No action specified. Try passing --push, --pull, --commit, or --all.")


def main_from_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    main_from_parser()
