
from crocodile.file_management import P
from machineconfig.utils.utils import PROGRAM_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse


def args_parser():
    parser = argparse.ArgumentParser(description="Secure Repo CLI.")

    parser.add_argument("--cloud", "-c", help="rclone cloud profile name.", default=None)
    parser.add_argument("--path", "-p", help="rclone cloud profile name.", default=None)
    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    # parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--upload", "-u", help="Upload direction, local is unchanged.", action="store_true")  # default is False
    parser.add_argument("--download", "-d", help="Download direction, local is unchanged.", action="store_true")  # default is False
    parser.add_argument("--bisync", "-b", help="Bidirectional sync.", action="store_true")  # default is False

    parser.add_argument("--verbose", "-v", help="Verbosity of mprocs to show details of syncing.", action="store_true")  # default is False

    args = parser.parse_args()

    # map short flags to long flags (-u -> --upload), for easier use in the script
    if args.upload: strategy = "upload"
    elif args.download: strategy = "download"
    elif args.bisync: strategy = "bisync"
    else: strategy = "bisync"

    local = P(args.path).expanduser().absolute()
    remote = "myhome/generic_os" / local.rel2home()
    print(f"Syncing {local} to {args.cloud}:{remote} | using strategy `{strategy}`")

    if args.upload: rclone_cmd = f"""rclone sync {local} {args.cloud}:{remote}"""
    elif args.download: rclone_cmd = f"""rclone sync {args.cloud}:{remote} {local}"""
    elif args.bisync: rclone_cmd = f"""rclone bisync {local} {args.cloud}:{remote} --resync"""
    else: rclone_cmd = f"""rclone bisync {local} {args.cloud}:{remote} --resync"""

    if args.verbose: txt = get_mprocs_mount_txt(cloud=args.cloud, cloud_brand="unknown", rclone_cmd=rclone_cmd, localpath=local)
    else: txt = f"""cd ~\n{rclone_cmd}"""
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
