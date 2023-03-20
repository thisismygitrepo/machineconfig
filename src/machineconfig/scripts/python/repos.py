

import crocodile.toolbox as tb
import argparse
from machineconfig.utils.utils import PROGRAM_PATH
from platform import system


tm = tb.Terminal()


def commit_one(path, mess="auto_commit_" + tb.randstr()):
    return f'''
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
{join.join(cmds)}
echo ""
echo ""
"""


def main():
    parser = argparse.ArgumentParser(description='REPO MANAGER')
    # POSITIONAL
    parser.add_argument("directory", help="folder containing repos.", default="")
    # FLAGS
    parser.add_argument("--push", help=f"push", action="store_true")
    parser.add_argument("--pull", help=f"pull", action="store_true")
    parser.add_argument("--commit", help=f"commit", action="store_true")
    parser.add_argument("--all", help=f"all", action="store_true")

    args = parser.parse_args()
    if args.directory == "": path = tb.P.home().joinpath("code")
    else: path = tb.P(args.directory).expanduser().absolute()

    program = ""
    for a_path in path.search("*"):
        program += f"""echo "{("Handling " + str(a_path)).center(80, "-")}" """
        if args.pull or args.all: program += f"""\necho '>>>>>>>>> Pulling'\n""" + pull_one(a_path) + "\n"
        if args.commit or args.all: program += f"""\necho '>>>>>>>>> Committing'\n""" + commit_one(a_path) + "\n"
        if args.push or args.all: program += f"""\necho '>>>>>>>>> Pushing'\n""" + push_one(a_path) + "\n"
        if not args.all and not args.commit and not args.pull and not args.push:
            program = "echo 'no action specified, try to pass --push, --pull, --commit or --all'"
            break

    program = "$orig_path = $pwd\n" + program + "\ncd $orig_path"
    print(f"Executing {PROGRAM_PATH}")
    if system() == 'Windows': PROGRAM_PATH.create(parents_only=True).write_text(program)
    else: PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


if __name__ == '__main__':
    main()
