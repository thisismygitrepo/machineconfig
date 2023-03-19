

import crocodile.toolbox as tb
import argparse
from machineconfig.utils.utils import PROGRAM_PATH
from platform import system


tm = tb.Terminal()


def commit_one(path, mess="auto_commit_" + tb.randstr()):
    return f'''
echo "{("Committing " + str(path)).center(80, "-")}"
cd {path}; git add .; git commit -am "{mess}"
echo ""
echo ""
'''


def push_one(path):
    remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
    cmds = []
    join = '\n'
    for remote in remotes:
        if remote != "": cmds.append(f'cd {path}; git push {remote}')
    return f"""
echo "{("Pushing " + str(path)).center(80, "-")}"
{join.join(cmds)}
echo ""
echo ""
"""


def pull_one(path):
    remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
    cmds = []
    join = '\n'
    for remote in remotes:
        if remote != "": cmds.append(f'cd {path}; git pull {remote}')
    return f"""
echo "{("Pulling " + str(path)).center(80, "-")}"
{join.join(cmds)}
echo ""
echo ""
"""


def commit_all(path=None):
    q = path.search("*").apply(lambda x: commit_one(x))  # reduce(lambda x, y: x + "\n\n" + y)[0]
    return "\n\n".join(q)
def push_all(path=None): return "\n\n".join(path.search("*").apply(lambda x: push_one(x)))
def pull_all(path=None): return "\n\n".join(path.search("*").apply(lambda x: pull_one(x)))


def main():
    parser = argparse.ArgumentParser(description='REPO MANAGER')
    # POSITIONAL
    parser.add_argument("directory", help="folder containing repos.", default="")
    # # FLAGS
    parser.add_argument("--push", help=f"push", action="store_true")
    parser.add_argument("--pull", help=f"pull", action="store_true")
    parser.add_argument("--commit", help=f"commit", action="store_true")

    args = parser.parse_args()
    if args.directory == "": path = tb.P.home().joinpath("code")
    else: path = tb.P(args.directory).expanduser().absolute()

    if args.commit: program = commit_all(path)
    elif args.push: program = push_all(path)
    elif args.pull: program = pull_all(path)
    else: program = "echo 'no action specified, try to pass --push, --pull, or --commit'"

    print(f"Executing {PROGRAM_PATH}")
    if system() == 'Windows': PROGRAM_PATH.create(parents_only=True).write_text(program)
    else: PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


if __name__ == '__main__':
    main()
