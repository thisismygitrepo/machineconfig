
from crocodile.file_management import P, Read
from machineconfig.utils.utils import PROGRAM_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse

"""

"""


def args_parser():
    parser = argparse.ArgumentParser(description="""A wrapper for rclone sync and rclone bisync, with some extra features.""")

    parser.add_argument("source", help="source", default=None)
    parser.add_argument("target", help="target", default=None)

    parser.add_argument("--transfers", "-t", help="Number of threads in syncing.", default=10)  # default is False
    parser.add_argument("--root", "-r", help="Remote root.", default="myhome")  # default is False

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
    elif ":" in args.target:
        source = args.target  # unchanged
        target = P(args.source).expanduser().absolute()
        cloud = source.split(":")[0]
    else:  # user did not specify remotepath, so it will be inferred here
        # but first we need to know whether the cloud is source or target
        remotes = Read.ini(P.home().joinpath(".config/rclone/rclone.conf")).sections()
        for cloud in remotes:
            if args.source == cloud:
                target = P(args.target).expanduser().absolute()
                source = f"{cloud}:{target._get_remote_path(root=args.root)}"
                break
            if args.target == cloud:
                source = P(args.source).expanduser().absolute()
                target = f"{cloud}:{source._get_remote_path(root=args.root)}"
                break
        else:
            print(f"Could not find a remote in {remotes} that matches {args.source} or {args.target}.")
            raise ValueError

    # map short flags to long flags (-u -> --upload), for easier use in the script
    if args.bisync:
        print(f"SYNCING 🔄️ {source} {'<>' * 7} {target}`")
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync"""
    else:
        print(f"SYNCING {source} {'>' * 15} {target}`")
        rclone_cmd = f"""rclone sync '{source}' '{target}' """

    rclone_cmd += f" --progress --transfers={args.transfers} --verbose"
    # rclone_cmd += f"  --vfs-cache-mode full"
    if args.delete: rclone_cmd += " --delete-during"

    if args.verbose: txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd)
    else: txt = f"""cd ~\n{rclone_cmd}"""
    print(r'running command'.center(100, '-'))
    print(txt)
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
