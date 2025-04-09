"""Repos

# TODO use gh api user --jq '.login' to get the username and use it to clone the repos.
in the event that username@github.com is not mentioned in the remote url.

"""

from rich import print as pprint
from machineconfig.utils.utils import write_shell_script_to_default_program_path, CONFIG_PATH, DEFAULTS_PATH
from crocodile.file_management import P, Read, Save
from crocodile.core import randstr
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
    remotes: list[str]
    version: dict[str, str]


def git_action(path: P, action: GitAction, mess: Optional[str] = None, r: bool=False) -> str:
    from git.exc import InvalidGitRepositoryError
    from git.repo import Repo
    try:
        repo = Repo(str(path), search_parent_directories=False)
    except InvalidGitRepositoryError:
        pprint(f"⚠️ Skipping {path} because it is not a git repository.")
        if r:
            prgs = [git_action(path=sub_path, action=action, mess=mess, r=r) for sub_path in path.search()]
            return "\n".join(prgs)
        else: return "\necho 'skipped because not a git repo'\n\n"

    program = f'''
🔧 echo '>>>>>>>>> {action}'
cd '{path}'
'''
    if action == GitAction.commit:
        if mess is None: mess = "auto_commit_" + randstr()
        program += f'''
🔄 git add .; git commit -am "{mess}"
'''
    if action == GitAction.push or action == GitAction.pull:
        action_name = "pull" if action == GitAction.pull else "push"
        cmds = [f'echo "🔄 {action_name.capitalize()}ing from {remote.url}" ; git {action_name} {remote.name} {repo.active_branch.name}' for remote in repo.remotes]
        program += '\n' + '\n'.join(cmds) + '\n'
    program = program + '''
✅ echo ""; echo ""
'''
    return program


def main():
    print("\n" + "=" * 50)
    print("📂 Welcome to the Repository Manager")
    print("=" * 50 + "\n")

    parser = argparse.ArgumentParser(description='REPO MANAGER')
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
    # OPTIONAL
    parser.add_argument("--cloud", "-c", help="☁️ Cloud storage option.", default=None)
    args = parser.parse_args()

    if args.directory == "": repos_root = P.home().joinpath("code")  # it is a positional argument, can never be empty.
    else: repos_root = P(args.directory).expanduser().absolute()

    program = ""
    if args.record:
        print("\n📝 Recording repositories...")
        res = record_repos(repos_root=str(repos_root))
        pprint("✅ Recorded repositories:\n", res)
        save_path = CONFIG_PATH.joinpath("repos").joinpath(repos_root.rel2home()).joinpath("repos.json")
        Save.json(obj=res, path=save_path, indent=4)
        pprint(f"📁 Result saved at {P(save_path)}")
        if args.cloud is not None: P(save_path).to_cloud(rel2home=True, cloud=args.cloud)
        program += """\necho '>>>>>>>>> Finished Recording'\n"""
    elif args.clone or args.checkout or args.checkout_to_branch:
        print("\n📥 Cloning or checking out repositories...")
        program += """\necho '>>>>>>>>> Cloning Repos'\n"""
        if not repos_root.exists() or repos_root.stem != 'repos.json':  # user didn't pass absolute path to pickle file, but rather expected it to be in the default save location
            repos_root = CONFIG_PATH.joinpath("repos").joinpath(repos_root.rel2home()).joinpath("repos.json")
            if not repos_root.exists():
                if args.cloud is None:
                    cloud: str=Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
                    print(f"⚠️ Using default cloud: {cloud}")
                else:
                    cloud = args.cloud
                    assert cloud is not None, f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
                repos_root.from_cloud(cloud=cloud, rel2home=True)
        assert (repos_root.exists() and repos_root.name == 'repos.json') or args.cloud is not None, f"Path {repos_root} does not exist and cloud was not passed. You can't clone without one of them."
        program += install_repos(specs_path=str(repos_root), clone=args.clone, checkout_to_recorded_commit=args.checkout, checkout_to_branch=args.checkout_to_branch)
    elif args.all or args.commit or args.pull or args.push:
        print("\n🔄 Performing Git actions on repositories...")
        for a_path in repos_root.search("*"):
            program += f"""echo "{("Handling " + str(a_path)).center(80, "-")}" """
            if args.pull or args.all: program += git_action(path=a_path, action=GitAction.pull, r=args.recursive)
            if args.commit or args.all: program += git_action(a_path, action=GitAction.commit, r=args.recursive)
            if args.push or args.all: program += git_action(a_path, action=GitAction.push, r=args.recursive)
    else: program = "echo '❌ No action specified. Try passing --push, --pull, --commit, or --all.'"
    write_shell_script_to_default_program_path(program=program, desc="Script to update repos", preserve_cwd=True, display=True, execute=False)


def record_repos(repos_root: str, r: bool=True) -> list[dict[str, Any]]:
    path_obj = P(repos_root).expanduser().absolute()
    if path_obj.is_file(): return []
    search_res = path_obj.search("*", files=False)
    res: list[dict[str, Any]] = []
    for a_search_res in search_res:
        if a_search_res.joinpath(".git").exists():
            res.append(record_a_repo(a_search_res))
        else:
            if r: res += record_repos(str(a_search_res), r=r)
    return res


def record_a_repo(path: P, search_parent_directories: bool=False, preferred_remote: Optional[str] = None):
    from git.repo import Repo
    repo = Repo(path, search_parent_directories=search_parent_directories)  # get list of remotes using git python
    repo_root = P(repo.working_dir).absolute()
    remotes = {remote.name: remote.url for remote in repo.remotes}
    if preferred_remote is not None:
        if preferred_remote in remotes: remotes = {preferred_remote: remotes[preferred_remote]}
        else:
            print(f"⚠️ `{preferred_remote=}` not found in {remotes}.")
            preferred_remote = None
    try: commit = repo.head.commit.hexsha
    except ValueError:  # look at https://github.com/gitpython-developers/GitPython/issues/1016
        print(f"⚠️ Failed to get latest commit of {repo}")
        commit = None
    try: current_branch = repo.head.reference.name  # same as repo.active_branch.name
    except TypeError:
        print(f"⁉️ Failed to get current branch of {repo}. It is probably in a detached state.")
        current_branch = None
    res: dict[str, Any] = {"name": repo_root.name, "parent_dir": repo_root.parent.collapseuser().as_posix(),
                            "current_branch": current_branch,
                            "remotes": remotes, "version": {"branch": current_branch, "commit": commit}}
    return res


def install_repos(specs_path: str, clone: bool=True, checkout_to_recorded_commit: bool=False, checkout_to_branch: bool=False, editable_install: bool=False, preferred_remote: Optional[str] = None):
    program = ""
    path_obj = P(specs_path).expanduser().absolute()
    repos: list[dict[str, Any]] = Read.json(path_obj)
    for repo in repos:
        parent_dir = P(repo["parent_dir"]).expanduser().absolute().create()
        for idx, (remote_name, remote_url) in enumerate(repo["remotes"].items()):
            if clone:
                if idx == 0:  # clone
                    if preferred_remote is not None:
                        if preferred_remote in repo["remotes"]:
                            remote_name = preferred_remote
                            remote_url = repo["remotes"][preferred_remote]
                        else:
                            print(f"⚠️ `{preferred_remote=}` not found in {repo['remotes']}.")
                    program += f"\ncd {parent_dir.collapseuser().as_posix()}; git clone {remote_url} --origin {remote_name}"
                    program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git remote set-url {remote_name} {remote_url}"
                program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git remote add {remote_name} {remote_url}"
            if checkout_to_recorded_commit:
                commit = repo['version']['commit']
                if isinstance(commit, str): program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git checkout {commit}"
                else: print(f"Skipping {repo['parent_dir']} because it doesn't have a commit recorded. Found {commit}")
                break
            if checkout_to_branch:
                program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; git checkout {repo['current_branch']}"
                break
            if editable_install and idx == 0:
                program += f"\ncd {parent_dir.collapseuser().as_posix()}/{repo['name']}; uv pip install -e ."
        program += "\n"
    pprint(program)
    return program


if __name__ == '__main__':
    main()
