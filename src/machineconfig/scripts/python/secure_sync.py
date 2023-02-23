
import crocodile.toolbox as tb
import argparse
# import sys
# import subprocess


def args_parser():
    parser = argparse.ArgumentParser(description="Secure Repo CLI.")

    parser.add_argument("--repo_root", "-r", help="repo root", default=None)
    parser.add_argument("--cloud", "-c", help="rclone cloud profile name.", default=None)
    parser.add_argument("--message", "-m", help="Commit Message", default=f"new message {tb.randstr()}")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)
    parser.add_argument("--push", "-u", help="Zip before sending.", action="store_true")  # default is False

    args = parser.parse_args()

    if args.cloud is None:
        cloud = tb.P.home().joinpath("dotfiles/config/setup/rclone_remote").read_text().replace("\n", "")
    else: cloud = args.cloud

    if args.repo_root is None:
        repo_root = tb.P(".").absolute()
    else:
        repo_root = tb.P(args.repo_root).expanduser().absolute()

    repo = tb.install_n_import("git", "gitpython").Repo(repo_root)
    tb.P.home().joinpath(".machineconfig/remote").create()
    repo_sync = tb.P.home().joinpath(".machineconfig/remote", repo_root.rel2home())

    try:
        print("\n", "=============================== Downloading Remote Repo ====================================")
        repo_root.from_cloud(cloud=cloud, localpath=repo_sync, unzip=True, decrypt=True, rel2home=True, key=args.key, pwd=args.pwd, os_specific=False)
    except AssertionError:
        print("Remote does not exist, creating it and exiting ... ")
        repo_root.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, key=args.key, pwd=args.pwd, os_specific=False)
        return ""

    script = f"""
echo ""
echo "=============================== Committing Local Changes ==================================="
cd {repo_root}
git status
git add .
git commit -am "{args.message}"
echo ""
echo ""
echo "=============================== Pulling Latest From Remote ================================"
cd {repo_root}
git remote remove originEnc
git remote add originEnc {repo_sync}

git pull originEnc master

"""
    res = tb.Terminal().run(f". {tb.P.tmpfile(suffix='.ps1').write_text(script)}", shell="powershell").capture().print()
    if res.is_successful(strict_err=False, strict_returcode=True):
        print("\n", "Pull succeeded, removing originEnc, the local copy of remote & pushing merged repo_root to remote ... ")
        repo_sync.delete(sure=True)
        from git.remote import Remote
        Remote.remove(repo, "originEnc")
        if args.push:
            repo_root.to_cloud(cloud=cloud, zip=True, encrypt=True, rel2home=True, key=args.key, pwd=args.pwd, os_specific=False)
    else:
        print(f"Failed to pull, keeping local copy of remote at {repo_sync} ... ")


if __name__ == "__main__":
    args_parser()
