
"""Repos
"""

import crocodile.toolbox as tb
import argparse
from machineconfig.utils.utils import write_shell_script, CONFIG_PATH
from rich import print as pprint
# from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any
# tm = tb.Terminal()


class GitAction(Enum):
    commit = "commit"
    push = "push"
    pull = "pull"


def git_action(path: tb.P, action: GitAction, mess: Optional[str] = None, r: bool = False) -> str:
    from git.exc import InvalidGitRepositoryError
    from git.repo import Repo
    try:
        repo = Repo(str(path), search_parent_directories=False)
    except InvalidGitRepositoryError:
        pprint(f"Skipping {path} because it is not a git repository.")
        if r:
            prgs = [git_action(path=sub_path, action=action, mess=mess, r=r) for sub_path in path.search()]
            return "\n".join(prgs)
        else: return "\necho 'skipped because not a git repo'\n\n"

    program = f'''
echo '>>>>>>>>> {action}'
cd '{path}'
'''
    if action == GitAction.commit:
        if mess is None: mess = "auto_commit_" + tb.randstr()
        program += f'''
git add .; git commit -am "{mess}"
'''
    if action == GitAction.push or action == GitAction.pull:
        # remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
        action_name = "pull" if action == GitAction.pull else "push"
        cmds = [f'echo "pulling from {remote.url}" ; git {action_name} {remote.name} {repo.active_branch.name}' for remote in repo.remotes]
        program += '\n' + '\n'.join(cmds) + '\n'
    program = program + f'''
echo ""; echo ""
'''
    return program


def main():
    parser = argparse.ArgumentParser(description='REPO MANAGER')
    # POSITIONAL
    parser.add_argument("directory", help="folder containing repos.", default="")
    # FLAGS
    parser.add_argument("--push", help=f"push", action="store_true")
    parser.add_argument("--pull", help=f"pull", action="store_true")
    parser.add_argument("--commit", help=f"commit", action="store_true")
    parser.add_argument("--all", help=f"pull, commit and push", action="store_true")
    parser.add_argument("--record", help=f"record respos", action="store_true")
    parser.add_argument("--clone", help=f"clone repos from record", action="store_true")
    parser.add_argument("--version", help=f"After cloning, checkout to the specific commits as per records (instead of latest commits)", action="store_true")
    parser.add_argument("--recursive", "-r", help=f"recursive flag", action="store_true")
    # OPTIONAL
    parser.add_argument("--cloud", "-c", help=f"cloud", default=None)
    args = parser.parse_args()

    if args.directory == "": path = tb.P.home().joinpath("code")  # it is a positional argument, can never be empty.
    else: path = tb.P(args.directory).expanduser().absolute()
    _ = tb.install_n_import("git", "gitpython")

    program = ""
    if args.record:
        res = record_repos(path=str(path))
        pprint(f"Recorded repositories:\n", res)
        save_path = CONFIG_PATH.joinpath("repos").joinpath(path.rel2home()).joinpath("repos.pkl")
        tb.Save.pickle(obj=res, path=save_path)
        pprint(f"Result pickled at {tb.P(save_path)}")
        if args.cloud is not None: tb.P(save_path).to_cloud(rel2home=True, cloud=args.cloud)
        program += f"""\necho '>>>>>>>>> Finished Recording'\n"""
    elif args.clone:
        program += f"""\necho '>>>>>>>>> Cloning Repos'\n"""
        if not path.exists() or path.stem != 'repos.pkl':  # user didn't pass absolute path to pickle file, but rather expected it to be in the default save location
            path = CONFIG_PATH.joinpath("repos").joinpath(path.rel2home()).joinpath("repos.pkl")
            if not path.exists(): path.from_cloud(cloud=args.cloud, rel2home=True)
        assert (path.exists() and path.stem == 'repos.pkl') or args.cloud is not None, f"Path {path} does not exist and cloud was not passed. You can't clone without one of them."
        program += install_repos(path=str(path), checkout_to_recorded_commit=args.version)
    elif args.all or args.commit or args.pull or args.push:
        for a_path in path.search("*"):
            program += f"""echo "{("Handling " + str(a_path)).center(80, "-")}" """
            if args.pull or args.all: program += git_action(path=a_path, action=GitAction.pull, r=args.recursive)
            if args.commit or args.all: program += git_action(a_path, action=GitAction.commit, r=args.recursive)
            if args.push or args.all: program += git_action(a_path, action=GitAction.push, r=args.recursive)
    else: program = "echo 'no action specified, try to pass --push, --pull, --commit or --all'"
    # pprint(program)
    write_shell_script(program, "Script to update repos")


def record_repos(path: str, r: bool = True) -> list[dict[str, Any]]:
    from git.repo import Repo
    path_obj = tb.P(path).expanduser().absolute()
    if path_obj.is_file(): return []
    search_res = path_obj.search("*", files=False)
    res = []
    for a_search_res in search_res:
        if a_search_res.joinpath(".git").exists():
            repo = Repo(a_search_res)  # get list of remotes using git python
            remotes = {remote.name: remote.url for remote in repo.remotes}
            try: commit = repo.head.commit.hexsha
            except ValueError:  # look at https://github.com/gitpython-developers/GitPython/issues/1016
                print(f"Failed to get latest commit of {repo}")
                # cmd = "git config --global -add safe.directory"
                commit = None
            res.append({"parent_dir": a_search_res.parent.collapseuser().as_posix(), "remotes": remotes, "version": {"branch": repo.head.reference.name, "commit": commit}})
        else:
            if r: res += record_repos(str(a_search_res), r=r)
    return res


def install_repos(path: str, checkout_to_recorded_commit: bool = False):
    program = ""
    path_obj = tb.P(path).expanduser().absolute()
    repos: list[dict[str, Any]] = tb.Read.pickle(path_obj)
    for repo in repos:
        parent_dir = tb.P(repo["parent_dir"]).expanduser().absolute().create()
        for idx, (remote_name, remote_url) in enumerate(repo["remotes"].items()):
            if idx == 0:  # clone
                program += f"\ncd {parent_dir.as_posix()}; git clone {remote_url} --origin {remote_name}\n"
                program += f"\ncd {parent_dir.as_posix()}/{tb.P(remote_url)[-1].stem}; git remote set-url {remote_name} {remote_url}\n"
                # the new url-setting to ensure that account name before `@` was not lost (git clone ignores it): https://thisismygitrepo@github.com/thisismygitrepo/crocodile.git
            program += f"\ncd {parent_dir.as_posix()}/{tb.P(remote_url)[-1].stem}; git remote add {remote_name} {remote_url}\n"
            if checkout_to_recorded_commit:
                commit = repo['version']['commit']
                if isinstance(commit, str): program += f"\n git checkout {commit}"
    pprint(program)
    return program


if __name__ == '__main__':
    main()
