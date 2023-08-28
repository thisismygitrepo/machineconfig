
"""CS
"""

from crocodile.file_management import P, Read
from machineconfig.utils.utils import PROGRAM_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse



def parse_cloud_source_target(args: argparse.Namespace):
    if args.source == ":":
        path = P(args.target).expanduser().absolute()
        for _i in range(len(path.parts)):
            if path.joinpath("cloud.json").exists():
                tmp = path.joinpath("cloud.json").readit()
                args.source = f"{tmp['cloud']}:"
                args.root = tmp["root"]
                args.rel2home = tmp['rel2home']
                break
            path = path.parent
        else: args.source = P.home().joinpath(r"dotfiles/machineconfig/setup/rclone_remote").read_text().rstrip() + ":"
    if args.target == ":":
        path = P(args.source).expanduser().absolute()
        for _i in range(len(path.parts)):
            if path.joinpath("cloud.json").exists():
                tmp = path.joinpath("cloud.json").readit()
                args.target = f"{tmp['cloud']}:"
                args.root = tmp["root"]
                args.rel2home = tmp['rel2home']
                break
            path = path.parent
        else: args.target = P.home().joinpath(r"dotfiles/machineconfig/setup/rclone_remote").read_text().rstrip() + ":"

    if ":" in args.source:
        cloud = args.source.split(":")[0]
        target = P(args.target).expanduser().absolute()
        source = f"{cloud}:{target.get_remote_path(os_specific=False, root=args.root).as_posix()}"
    elif ":" in args.target:
        cloud = args.target.split(":")[0]
        source = P(args.source).expanduser().absolute()
        target = f"{cloud}:{source.get_remote_path(os_specific=False, root=args.root).as_posix()}"
    else:  # user did not specify remotepath, so it will be inferred here
        # but first we need to know whether the cloud is source or target
        remotes = Read.ini(P.home().joinpath(".config/rclone/rclone.conf")).sections()
        for cloud in remotes:
            if args.source == cloud:
                target = P(args.target).expanduser().absolute()
                source = f"{cloud}:{target.get_remote_path(os_specific=False, root=args.root).as_posix()}"
                break
            if args.target == cloud:
                source = P(args.source).expanduser().absolute()
                target = f"{cloud}:{source.get_remote_path(os_specific=False, root=args.root).as_posix()}"
                break
        else:
            print(f"Could not find a remote in {remotes} that matches {args.source} or {args.target}.")
            raise ValueError
    return cloud, source, target


def args_parser():
    parser = argparse.ArgumentParser(description="""A wrapper for rclone sync and rclone bisync, with some extra features.""")

    parser.add_argument("source", help="source", default=None)
    parser.add_argument("target", help="target", default=None)

    parser.add_argument("--transfers", "-t", help="Number of threads in syncing.", default=10)  # default is False
    parser.add_argument("--root", "-R", help="Remote root.", default="myhome")  # default is False

    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    # parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--bisync", "-b", help="Bidirectional sync.", action="store_true")  # default is False
    parser.add_argument("--delete", "-D", help="Delete files in remote that are not in local.", action="store_true")  # default is False
    parser.add_argument("--verbose", "-v", help="Verbosity of mprocs to show details of syncing.", action="store_true")  # default is False

    args = parser.parse_args()

    cloud, source, target = parse_cloud_source_target(args)
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

    if args.verbose: txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, cloud_brand="Unknown")
    else: txt = f"""cd ~\n{rclone_cmd}"""
    print(r'running command'.center(100, '-'))
    print(txt)
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
