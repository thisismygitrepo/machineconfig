

import crocodile.toolbox as tb
tm = tb.Terminal()


def commit_one(path, mess="auto_commit_" + tb.randstr()):
    return f'''
echo "{("Committing " + str(path)).center(80, "-")}"
cd {path}; git add .; git commit -am "{mess}"'
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


def commit_all():
    q = tb.P.home().joinpath("code").search("*").apply(lambda x: commit_one(x))  # reduce(lambda x, y: x + "\n\n" + y)[0]
    return "\n\n".join(q)

def push_all(): return "\n\n".join(tb.P.home().joinpath("code").search("*").apply(lambda x: push_one(x)))
def pull_all(): return "\n\n".join(tb.P.home().joinpath("code").search("*").apply(lambda x: pull_one(x)))


if __name__ == '__main__':
    pass
