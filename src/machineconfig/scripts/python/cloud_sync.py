
from crocodile.file_management import P, Read
from machineconfig.utils.utils import PROGRAM_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse

"""

"""

# TODO add  --vfs-cache-mode full


def args_parser():
    parser = argparse.ArgumentParser(description="""A wrapper for rclone sync and rclone bisync, with some extra features.""")

    parser.add_argument("source", help="source", default=None)
    parser.add_argument("target", help="target", default=None)

    parser.add_argument("--transfers", "-t", help="Number of threads in syncing.", default=10)  # default is False
    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    # parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--bisync", "-b", help="Bidirectional sync.", action="store_true")  # default is False
    parser.add_argument("--delete", "-D", help="Delete files in remote that are not in local.", action="store_true")  # default is False

    parser.add_argument("--verbose", "-v", help="Verbosity of mprocs to show details of syncing.", action="store_true")  # default is False

    args = parser.parse_args()

    if ":" in args.source:
        source = args.source
        target = P(args.target).expanduser().absolute()
        cloud = source.split(":")[0]
        localpath = target
    elif ":" in args.target:
        source = args.target  # unchanged
        target = P(args.source).expanduser().absolute()
        cloud = source.split(":")[0]
        localpath = target
    else:  # user did not specify remotepath, so it will be inferred here
        # but first we need to know whether the cloud is source or target
        remotes = Read.ini(P.home().joinpath(".config/rclone/rclone.conf")).sections()
        for a_remote in remotes:
            if args.source == a_remote:
                target = P(args.target).expanduser().absolute()
                source = f"{args.source}:{'myhome/generic_os' / target.rel2home()}"
                cloud = args.source
                localpath = target
                break
            if args.target == a_remote:
                source = P(args.source).expanduser().absolute()
                target = f"{args.target}:{'myhome/generic_os' / source.rel2home()}"
                cloud = args.target
                localpath = source
                break
        else:
            print(f"Could not find a remote in {remotes} that matches {args.source} or {args.target}.")
            raise ValueError

    # map short flags to long flags (-u -> --upload), for easier use in the script
    if args.bisync: print(f"Syncing {source} {'<>' * 7} {target}`")
    else: print(f"Syncing {source} {'>' * 15} {target}`")

    if args.bisync: rclone_cmd = f"""rclone bisync {source} {target}"""
    else: rclone_cmd = f"""rclone sync {source} {target}"""

    rclone_cmd += f" --progress --transfers={args.transfers} --verbose"
    if args.bisync: rclone_cmd += " --resync"
    if args.delete: rclone_cmd += " --delete-during"

    if args.verbose: txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, localpath=localpath)
    else: txt = f"""cd ~\n{rclone_cmd}"""
    print(r'running command'.center(100, '-'))
    print(txt)
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
