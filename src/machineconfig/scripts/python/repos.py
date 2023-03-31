

import crocodile.toolbox as tb
import argparse
from machineconfig.utils.utils import write_shell_script
from rich import print


tm = tb.Terminal()


def commit_one(path, mess="auto_commit_" + tb.randstr()):
    return f'''
cd '{path}'; git add .; git commit -am "{mess}"
echo ""
echo ""
'''


def push_one(path):
    remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
    cmds = []
    join = '\n'
    for remote in remotes:
        if remote != "": cmds.append(f'cd "{path}"; git push {remote}')
    return f"""
{join.join(cmds)}
echo ""; echo ""
"""


def pull_one(path):
    remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
    cmds = []
    join = '\n'
    for remote in remotes:
        if remote != "": cmds.append(f'cd "{path}"; git pull {remote}')
    return f"""
{join.join(cmds)}
echo ""; echo ""
"""


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
    # OPTIONAL
    parser.add_argument("--cloud", "-c", help=f"cloud", default=None)

    args = parser.parse_args()
    if args.directory == "": path = tb.P.home().joinpath("code")
    else: path = tb.P(args.directory).expanduser().absolute()

    program = ""
    if args.record:
        res = record_repos(path=path)
        print(res)
        save_path = tb.Save.pickle(obj=res, path=path.joinpath("repos.pkl"))
        if args.cloud is not None: tb.P(save_path).to_cloud(rel2home=True, cloud=args.cloud)
        program += f"""\necho '>>>>>>>>> Finished Recording'\n"""
    elif args.clone:
        program += f"""\necho '>>>>>>>>> Cloning Repos'\n"""
        program += install_repos(path=path, cloud=args.cloud)
    elif args.all or args.commit or args.pull or args.push:
        for a_path in path.search("*"):
            program += f"""echo "{("Handling " + str(a_path)).center(80, "-")}" """
            if args.pull or args.all: program += f"""\necho '>>>>>>>>> Pulling'\n""" + pull_one(a_path) + "\n"
            if args.commit or args.all: program += f"""\necho '>>>>>>>>> Committing'\n""" + commit_one(a_path) + "\n"
            if args.push or args.all: program += f"""\necho '>>>>>>>>> Pushing'\n""" + push_one(a_path) + "\n"
    else: program = "echo 'no action specified, try to pass --push, --pull, --commit or --all'"
    write_shell_script(program, "Script to update repos")


def record_repos(path) -> list[dict]:
    git = tb.install_n_import("git", "gitpython")
    path = tb.P(path).expanduser().absolute()
    if path.is_file(): return []
    search_res = path.search("*", files=False)
    res = []
    for a_search_res in search_res:
        if a_search_res.joinpath(".git").exists():
            # get list of remotes using git python
            repo = git.Repo(a_search_res)
            remotes = {remote.name: remote.url for remote in repo.remotes}
            res.append({"parent_dir": a_search_res.parent.collapseuser().as_posix(), "remotes": remotes})
        else:
            res += record_repos(a_search_res)
    return res


def install_repos(path=None, cloud=None):
    program = ""
    if cloud is not None:
        path = path.from_cloud(rel2home=True, cloud=cloud)
    else:
        path = tb.P(path).expanduser().absolute()
    repos = tb.Read.pickle(path)
    for repo in repos:
        for idx, (remote_name, remote_url) in enumerate(repo["remotes"].items()):
            parent_dir = tb.P(repo["parent_dir"]).expanduser().absolute().create()
            if idx == 0:
                program += f"\ncd {parent_dir}; git clone {remote_url} --origin {remote_name}\n"
            else:
                program += f"\ncd {parent_dir.as_posix()}/{tb.P(remote_url)[-1].stem}; git remote add {remote_name} {remote_url}\n"
    print(program)
    return program


if __name__ == '__main__':
    main()
