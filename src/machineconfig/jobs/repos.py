

import crocodile.toolbox as tb


tm = tb.Terminal()


def commit_one(path, mess="auto_commit_" + tb.randstr()):
    print(f"Committing {path}".center(80, "-"))
    res = tm.run(f'cd {path}; git add .; git commit -am "{mess}"', shell="powershell")
    res.print()


def push_one(path):
    print(f"Pushing {path}".center(80, "-"))
    remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
    for remote in remotes:
        if remote != "": tm.run(f'cd {path}; git push {remote}', shell="powershell").print()


def pull_one(path):
    print(f"Pulling {path}".center(80, "-"))
    remotes = tm.run(f"cd {path}; git remote", shell="powershell").op.split("\n")
    for remote in remotes:
        if remote != "":
            res = tm.run(f'cd {path}; git pull {remote}', shell="powershell")
            res.print()


def commit_all(): tb.P.home().joinpath("code").search("*").apply(lambda x: commit_one(x), verbose=True)
def push_all(): tb.P.home().joinpath("code").search("*").apply(lambda x: push_one(x), verbose=True)
def pull_all(): tb.P.home().joinpath("code").search("*").apply(lambda x: pull_one(x), verbose=True)


if __name__ == '__main__':
    pass
