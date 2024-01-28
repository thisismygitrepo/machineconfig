
"""CS
TODO: use tap typed-argument-parser to parse args
TODO: use typer to make clis
"""

from crocodile.file_management import P, Read, Struct
from crocodile.core import install_n_import
from machineconfig.utils.utils import PROGRAM_PATH, DEFAULTS_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse
import os
from typing import Optional
# from dataclasses import dataclass
# from tap import Tap


ES = "^"  # chosen carefully to not mean anything on any shell. `$` was a bad choice.


class ArgsDefaults:
    # source: str = None
    # target: str = None
    encrypt: bool = False
    zip_: bool = False
    overwrite: bool = False
    share: bool = False
    rel2home = False
    root = None
    os_specific = False
    key = None
    pwd = None


install_n_import("pydantic")
from pydantic.dataclasses import dataclass  # type: ignore # ruffle: ignore
from pydantic import ConfigDict


@dataclass(config=ConfigDict(extra="forbid", frozen=True))
class Args():
    cloud: Optional[str] = None

    zip: bool = ArgsDefaults.zip_
    overwrite: bool = ArgsDefaults.overwrite
    share: bool = ArgsDefaults.share

    root: Optional[str] = ArgsDefaults.root
    os_specific: bool = ArgsDefaults.os_specific
    rel2home: bool = ArgsDefaults.rel2home

    encrypt: bool = ArgsDefaults.encrypt
    key: Optional[str] = ArgsDefaults.key
    pwd: Optional[str] = ArgsDefaults.pwd

    config: Optional[str] = None

    @staticmethod
    def from_config(config_path: P):
        # from crocodile.core import install_n_import
        # install_n_import("pydantic")
        # from pydantic import BaseModel, ConfigDict
        return Args(**Read.json(config_path))


def absolute(path: str) -> P:
    obj = P(path).expanduser()
    if not path.startswith(".") and  obj.exists(): return obj
    try_absing =  P.cwd().joinpath(path)
    if try_absing.exists(): return try_absing
    print(f"Warning: {path} was not resolved to absolute one, trying out resolving symlinks (This may result in unintended paths)")
    return obj.absolute()


def get_secure_share_cloud_config(interactive: bool = True) -> Args:
    if os.environ.get("CLOUD_CONFIG_NAME") is not None:
        default_cloud = os.environ.get("CLOUD_CONFIG_NAME")
        assert default_cloud is not None
        cloud = default_cloud
    else:
        try:
            default_cloud__ = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        except Exception:
            default_cloud__ = 'No default cloud found.'
        if default_cloud__ == 'No default cloud found.' or interactive:
            # assert default_cloud is not None
            cloud = input(f"Enter cloud name (default {default_cloud__}): ") or default_cloud__
        else:
            cloud = default_cloud__

    default_password_path = P.home().joinpath("dotfiles/creds/passwords/quick_password")
    if default_password_path.exists():
        pwd = default_password_path.read_text().strip()
        default_message = "defaults to quick_password"
    else:
        pwd = ""
        default_message = "no default password found"
    pwd = input(f"Enter encryption password ({default_message}): ") or pwd
    res = Args(cloud=cloud,
               pwd=pwd, encrypt=True,
               zip=True, overwrite=True, share=True,
               rel2home=True, root="myshare", os_specific=False,)
    Struct(res.__dict__).print(as_config=True, title=f"⚠️ Using SecureShare cloud config")
    return res


def find_cloud_config(path: P):
    for _i in range(len(path.parts)):
        if path.joinpath("cloud.json").exists():
            res =  Args.from_config(path.joinpath("cloud.json"))
            Struct(res.__dict__).print(as_config=True, title=f"⚠️ Using default cloud config @ {path.joinpath('cloud.json')} ")
            return res
        path = path.parent
    return None


def parse_cloud_source_target(args: Args, source: str, target: str) -> tuple[str, str, str]:
    if source.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in source
        # At the moment, this cloud.json defaults overrides the args and is activated only when source or target are just ":"
        # consider activating it by a flag, and also not not overriding explicitly passed args options.
        assert ES not in target, f"Not Implemented here yet."
        path = absolute(target)
        if args.config is None:
            maybe_config: Optional[Args] = find_cloud_config(path=path)
        else:
            if args.config == "ss": maybe_config = get_secure_share_cloud_config()
            else: maybe_config = Args.from_config(absolute(args.config))

        if maybe_config is None:
            default_cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: {default_cloud}")
            source = default_cloud + ":" + source[1:]
        else:
            tmp = maybe_config
            source = f"{tmp.cloud}:" + source[1:]
            args.root = tmp.root
            args.rel2home = tmp.rel2home
            args.pwd = tmp.pwd
            args.encrypt = tmp.encrypt
            args.zip = tmp.zip
            args.share = tmp.share
            # args.jh = 22

    if target.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in target
        assert ES not in source, f"Not Implemented here yet."
        path = absolute(source)
        if args.config is None:
            maybe_config = find_cloud_config(path)
        else:
            if args.config == "ss": maybe_config = get_secure_share_cloud_config()
            else: maybe_config = Args.from_config(absolute(args.config))

        if maybe_config is not None:
            tmp = maybe_config
            target = f"{tmp.cloud}:" + target[1:]
            args.root = tmp.root
            args.rel2home = tmp.rel2home
            args.pwd = tmp.pwd
            args.encrypt = tmp.encrypt
            args.zip = tmp.zip
            args.share = tmp.share

        else:
            default_cloud = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            print(f"⚠️ Using default cloud: {default_cloud}")
            target = default_cloud + ":" + target[1:]

    if ":" in source and (source[1] != ":" if len(source) > 1 else True):  # avoid the deceptive case of "C:/"
        source_parts: list[str] = source.split(":")
        cloud = source_parts[0]

        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            assert ES not in target, f"You can't use expand symbol `{ES}` in both source and target. Cyclical inference dependency arised."
            target_obj = absolute(target)
            remote_path = target_obj.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home, strict=False)
            source = f"{cloud}:{remote_path.as_posix()}"

        else:  # source path is mentioned, target? maybe.
            if target == ES:  # target path is to be inferred from source.
                raise NotImplementedError(f"There is no .get_local_path method yet")
            else:
                target_obj = absolute(target)
        if args.zip and ".zip" not in source: source += ".zip"
        if args.encrypt and ".enc" not in source: source += ".enc"

    elif ":" in target and (target[1] != ":" if len(target) > 1 else True):  # avoid the case of "C:/"
        target_parts: list[str] = target.split(":")
        cloud = target.split(":")[0]

        if len(target_parts) > 1 and target_parts[1] == ES:  # the target path is to be inferred from source.
            assert ES not in source, f"You can't use $ in both source and target. Cyclical inference dependency arised."
            source_obj = absolute(source)
            remote_path = source_obj.get_remote_path(os_specific=args.os_specific, root=args.root, rel2home=args.rel2home, strict=False)
            target = f"{cloud}:{remote_path.as_posix()}"
        else:  # target path is mentioned, source? maybe.
            target = str(target)
            if source == ES:
                raise NotImplementedError(f"There is no .get_local_path method yet")
            else:
                source_obj = absolute(source)
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

    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--encrypt", "-e", help="Decrypt after receiving.", action="store_true")  # default is False
    parser.add_argument("--zip", "-z", help="unzip after receiving.", action="store_true")  # default is False

    parser.add_argument("--bisync", "-b", help="Bidirectional sync.", action="store_true")  # default is False
    parser.add_argument("--delete", "-D", help="Delete files in remote that are not in local.", action="store_true")  # default is False
    parser.add_argument("--verbose", "-v", help="Verbosity of mprocs to show details of syncing.", action="store_true")  # default is False

    args = parser.parse_args()
    args_dict = vars(args)
    source: str = args_dict.pop("source")
    target: str = args_dict.pop("target")
    verbose: bool = args_dict.pop("verbose")
    delete: bool = args_dict.pop("delete")
    bisync: bool = args_dict.pop("bisync")
    transfers: int = args_dict.pop("transfers")
    args_obj = Args(**args_dict)

    args_obj.os_specific = False
    args_obj.rel2home = True

    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    # map short flags to long flags (-u -> --upload), for easier use in the script
    if bisync:
        print(f"SYNCING 🔄️ {source} {'<>' * 7} {target}`")
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync"""
    else:
        print(f"SYNCING {source} {'>' * 15} {target}`")
        rclone_cmd = f"""rclone sync '{source}' '{target}' """

    rclone_cmd += f" --progress --transfers={transfers} --verbose"
    # rclone_cmd += f"  --vfs-cache-mode full"
    if delete: rclone_cmd += " --delete-during"

    if verbose: txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, cloud_brand="Unknown")
    else: txt = f"""{rclone_cmd}"""
    print(r'running command'.center(100, '-'))
    print(txt)
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
