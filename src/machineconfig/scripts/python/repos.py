"""Repos

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""

from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.utils2 import randstr, read_ini
from machineconfig.scripts.python.repos_helper_update import update_repository
from machineconfig.scripts.python.repos_helper_record import main as record_repos

import argparse
from enum import Enum
from typing import Optional

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
        save_path = record_repos(repos_root=repos_root)
        if args.cloud is not None:
            PathExtended(save_path).to_cloud(rel2home=True, cloud=args.cloud)

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


if __name__ == "__main__":
    main()
