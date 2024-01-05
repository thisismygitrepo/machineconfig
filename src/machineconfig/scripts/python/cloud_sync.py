
"""CS
TODO: use tap typed-argument-parser to parse args
TODO: use typer to make clis
"""

from crocodile.file_management import P, Read, Struct
from machineconfig.utils.utils import PROGRAM_PATH, DEFAULTS_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse
import os
from typing import Union, Optional
# from dataclasses import dataclass
# from tap import Tap


ES = "^"  # chosen carefully to not mean anything on any shell. `$` was a bad choice.


def absolute(path: str) -> P:
    obj = P(path).expanduser()
    if not path.startswith(".") and  obj.exists(): return obj
    try_absing =  P.cwd().joinpath(path)
    if try_absing.exists(): return try_absing
    print(f"Warning: {path} was not resolved to absolute one, trying out resolving symlinks (This may result in unintended paths)")
    return obj.absolute()


def get_secure_share_cloud_config(interactive: bool = True):
    if os.environ.get("CLOUD_CONFIG_NAME") is not None:
        default_cloud = os.environ.get("CLOUD_CONFIG_NAME")
        assert default_cloud is not None
        cloud = default_cloud
    else:
        try:
            default_cloud = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        except Exception:
            default_cloud = 'No default cloud found.'
        if default_cloud == 'No default cloud found.' or interactive:
            cloud = input(f"Enter cloud name (default {default_cloud}): ") or default_cloud
        else: cloud = default_cloud

    default_password_path = P.home().joinpath("dotfiles/creds/passwords/quick_password")
    if default_password_path.exists():
        pwd = default_password_path.read_text().strip()
        default_message = "defaults to quick_password"
    else:
        pwd = ""
        default_message = "no default password found"
    pwd = input(f"Enter encryption password ({default_message}): ") or pwd
    return {
    "cloud": cloud,
    "pwd": pwd,
    "encrypt": True,
    "zip": True,
    "overwrite": True,
    "share": True,
    "rel2home": True,
    "root": "myhome",
    "os_specific": False,
}

# class Args(Tap):
#     source: str
#     target: str
#     os_specific: bool = False
#     rel2home: bool = True
#     root: str = "myhome"
#     zip: bool = False
#     encrypt: bool = False
#     verbose: bool = False
#     delete: bool = False
#     bisync: bool = False
#     transfers: int = 10


def find_cloud_config(path: P):
    for _i in range(len(path.parts)):
        if path.joinpath("cloud.json").exists():
            res: dict[str, Union[str, bool]] =  path.joinpath("cloud.json").readit()
            Struct(res).print(as_config=True, title=f"⚠️ Using default cloud config @ {path.joinpath('cloud.json')} ")
            return res
        path = path.parent
    return None


def parse_cloud_source_target(args: argparse.Namespace) -> tuple[str, str, str]:
    if args.source.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in args.source
        # At the moment, this cloud.json defaults overrides the args and is activated only when source or target are just ":"
        # consider activating it by a flag, and also not not overriding explicitly passed args options.
        assert ES not in args.target, f"Not Implemented here yet."
        path = absolute(args.target)
        if args.config is None:
            maybe_config = find_cloud_config(path=path)
        else:
            if args.config == "ss": maybe_config = get_secure_share_cloud_config()
            else: maybe_config: Optional[dict[str, Union[str, bool]]] = Read.json(absolute(args.config))

        if maybe_config is None:
            default_cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: {default_cloud}")
            args.source = default_cloud + ":" + args.source[1:]
        else:
            tmp = maybe_config
            args.source = f"{tmp['cloud']}:" + args.source[1:]
            args.root = str(tmp["root"])
            tmp__: bool = bool(tmp['rel2home'])
            args.rel2home = tmp__
            args.pwd = tmp['pwd']
            args.encrypt = tmp['encrypt']
            args.zip = tmp['zip']
            args.share = tmp['share']

    if args.target.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in args.target
        assert ES not in args.source, f"Not Implemented here yet."
        path = absolute(args.source)
        if args.config is None:
            maybe_config = find_cloud_config(path)
        else:
            if args.config == "ss": maybe_config = get_secure_share_cloud_config()
            else: maybe_config: Optional[dict[str, Union[str, bool]]] = Read.json(absolute(args.config))

        if maybe_config is not None:
            tmp = maybe_config
            args.target = f"{tmp['cloud']}:" + args.target[1:]
            args.root = str(tmp["root"])
            args.rel2home = bool(tmp['rel2home'])
            args.pwd = tmp['pwd']
            args.encrypt = tmp['encrypt']
            args.zip = tmp['zip']
            args.share = tmp['share']

        else:
            default_cloud = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: {default_cloud}")
            args.target = default_cloud + ":" + args.target[1:]

    if ":" in args.source and (args.source[1] != ":" if len(args.source) > 1 else True):  # avoid the deceptive case of "C:/"
        source_parts: str = args.source.split(":")
        cloud = source_parts[0]

        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            assert ES not in args.target, f"You can't use expand symbol `{ES}` in both source and target. Cyclical inference dependency arised."
            target = absolute(args.target)
            remote_path = target.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home, strict=False)
            source = P(f"{cloud}:{remote_path.as_posix()}")

        else:  # source path is mentioned, target? maybe.
            source = str(args.source)
            if args.target == ES:  # target path is to be inferred from source.
                raise NotImplementedError(f"There is no .get_local_path method yet")
            else:
                target = absolute(args.target)
        if args.zip and ".zip" not in source: source += ".zip"
        if args.encrypt and ".enc" not in source: source += ".enc"

    elif ":" in args.target and (args.target[1] != ":" if len(args.target) > 1 else True):  # avoid the case of "C:/"
        target_parts: str = args.target.split(":")
        cloud = args.target.split(":")[0]

        if len(target_parts) > 1 and target_parts[1] == ES:  # the target path is to be inferred from source.
            assert ES not in args.source, f"You can't use $ in both source and target. Cyclical inference dependency arised."
            source = absolute(args.source)
            remote_path = source.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home, strict=False)
            target = P(f"{cloud}:{remote_path.as_posix()}")
        else:  # target path is mentioned, source? maybe.
            target = str(args.target)
            if args.source == ES:
                raise NotImplementedError(f"There is no .get_local_path method yet")
            else:
                source = absolute(args.source)
        if args.zip and ".zip" not in target: target += ".zip"
        if args.encrypt and ".enc" not in target: target += ".enc"
    else:
        raise ValueError("Either source or target must be a remote path (i.e. machine:path)")
    Struct({"cloud": cloud, "source": str(source), "target": str(target)}).print(as_config=True, title="CLI Resolution")
    return cloud, str(source), str(target)


def args_parser():
    parser = argparse.ArgumentParser(description="""A wrapper for rclone sync and rclone bisync, with some extra features.""")

    parser.add_argument("source", help="source", default=None)
    parser.add_argument("target", help="target", default=None)

    parser.add_argument("--transfers", "-t", help="Number of threads in syncing.", default=10)  # default is False
    parser.add_argument("--root", "-R", help="Remote root.", default="myhome")  # default is False

    # parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--encrypt", "-e", help="Decrypt after receiving.", action="store_true")  # default is False
    parser.add_argument("--zip", "-z", help="unzip after receiving.", action="store_true")  # default is False

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
