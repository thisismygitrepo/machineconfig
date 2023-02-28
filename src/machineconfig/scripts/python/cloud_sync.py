
from crocodile.file_management import P
from machineconfig.utils.utils import PROGRAM_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse


def args_parser():
    parser = argparse.ArgumentParser(description="Secure Repo CLI.")

    parser.add_argument("--cloud", "-c", help="rclone cloud profile name.", default=None)
    parser.add_argument("--localpath", "-l", help="rclone cloud profile name.", default=None)
    parser.add_argument("--transfers", "-t", help="Number of threads in syncing.", default=10)  # default is False
    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    # parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--upload", "-u", help="Upload direction, local is unchanged.", action="store_true")  # default is False
    parser.add_argument("--download", "-d", help="Download direction, local is unchanged.", action="store_true")  # default is False
    parser.add_argument("--bisync", "-b", help="Bidirectional sync.", action="store_true")  # default is False
    parser.add_argument("--delete", "-D", help="Delete files in remote that are not in local.", action="store_true")  # default is False

    parser.add_argument("--verbose", "-v", help="Verbosity of mprocs to show details of syncing.", action="store_true")  # default is False

    args = parser.parse_args()

    local = P(args.path).expanduser().absolute()
    if ":" not in args.cloud:  # usee did not specify remotepath, so it will be inferred here:
        remote = "myhome/generic_os" / local.rel2home()
        remote_exp = f"{args.cloud}:{remote}"
    else: remote_exp = args.cloud

    # map short flags to long flags (-u -> --upload), for easier use in the script
    if args.upload: _strategy = "upload"; print(f"Syncing {local} {'>' * 30} {remote_exp}`")
    elif args.download: _strategy = "download"; print(f"Syncing {local} {'<' * 30} {remote_exp}`")
    else: _strategy = "bisync"; print(f"Syncing {local} {'<>' * 15} {remote_exp}`")

    if args.upload: rclone_cmd = f"""rclone sync {local} {remote_exp}"""
    elif args.download: rclone_cmd = f"""rclone sync {remote_exp} {local}"""
    elif args.bisync: rclone_cmd = f"""rclone bisync {local} {remote_exp}"""
    else: rclone_cmd = f"""rclone bisync {local} {remote_exp}"""
    rclone_cmd += f" --progress --transfers={args.transfers}"
    if args.bisync: rclone_cmd += " --resync"
    if args.delete: rclone_cmd += " --delete-during"
    # if args.verbose: rclone_cmd += " --verbose"

    if args.verbose: txt = get_mprocs_mount_txt(cloud=args.cloud, cloud_brand="unknown", rclone_cmd=rclone_cmd, localpath=local)
    else: txt = f"""cd ~\n{rclone_cmd}"""
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
