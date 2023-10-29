
"""CS
"""

from crocodile.file_management import P, Read, Struct
from machineconfig.utils.utils import PROGRAM_PATH, DEFAULTS_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse


def parse_cloud_source_target(args: argparse.Namespace) -> tuple[str, str, str]:
    if args.source == ":":  # default cloud name is omitted cloud_name:
        path = P(args.target).expanduser().absolute()
        for _i in range(len(path.parts)):
            if path.joinpath("cloud.json").exists():
                tmp = path.joinpath("cloud.json").readit()
                args.source = f"{tmp['cloud']}:"
                args.root = tmp["root"]
                args.rel2home = tmp['rel2home']
                print(f"⚠️ Using default cloud config: cloud={tmp['cloud']}, root={args.root}, rel2home={args.rel2home}")
                break
            path = path.parent
        else:
            default_cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: {default_cloud}")
            args.source = default_cloud + ":"
    if args.target == ":":  # default cloud name is omitted cloud_name:
        path = P(args.source).expanduser().absolute()
        for _i in range(len(path.parts)):
            if path.joinpath("cloud.json").exists():
                tmp = path.joinpath("cloud.json").readit()
                args.target = f"{tmp['cloud']}:"
                args.root = tmp["root"]
                args.rel2home = tmp['rel2home']
                Struct(tmp).print(as_config=True, title=f"Cloud Config @ {path.joinpath('cloud.json')}")
                break
            path = path.parent
        else:
            default_cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: {default_cloud}")
            args.target = default_cloud + ":"

    if ":" in args.source and (":" != args.source[1] if len(args.source) > 1 else True):  # avoid the case of "C:/"
        cloud: str = args.source.split(":")[0]
        target = P(args.target).expanduser().absolute()
        remote_path = target.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home, strict=False)
        source = P(f"{cloud}:{remote_path.as_posix()}")
    elif ":" in args.target and (":" != args.target[1] if len(args.target) > 1 else True):  # avoid the case of "C:/"
        cloud = args.target.split(":")[0]
        print("h2")
        source = P(args.source).expanduser().absolute()
        remote_path = source.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home, strict=False)
        print(f"remote_path: {remote_path}, root: {args.root}, rel2home: {args.rel2home}, os_specific: {args.os_specific}, strict: {False}")
        target = P(f"{cloud}:{remote_path.as_posix()}")
    else:
        # user, being slacky and did not indicate the remotepath with ":", so it will be inferred here
        # but first we need to know whether the cloud is source or target
        remotes = Read.ini(P.home().joinpath(".config/rclone/rclone.conf")).sections()
        for cloud in remotes:
            if str(args.source) == cloud:
                target = P(args.target).expanduser().absolute()
                remote_path = target.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home)
                source = P(f"{cloud}:{remote_path.as_posix()}")
                break
            if str(args.target) == cloud:
                source = P(args.source).expanduser().absolute()
                remote_path = source.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home)
                target = P(f"{cloud}:{remote_path.as_posix()}")
                break
        else:
            print(f"Could not find a remote in {remotes} that matches {args.source} or {args.target}.")
            raise ValueError
    return cloud, str(source), str(target)


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
    args.os_specific = False
    args.rel2home = True

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
    else: txt = f"""{rclone_cmd}"""
    print(r'running command'.center(100, '-'))
    print(txt)
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
