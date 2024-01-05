
"""CC
"""

from crocodile.file_management import P
from crocodile.meta import RepeatUntilNoException
import getpass
from machineconfig.scripts.python.cloud_sync import parse_cloud_source_target, ArgsDefaults, Args
import argparse
import os
# from dataclasses import dataclass
# from pydantic import BaseModel
from typing import Optional


@RepeatUntilNoException()
def get_shared_file(url: Optional[str] = None, folder: Optional[str] = None):

    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        pwd = os.environ.get("DECRYPTION_PASSWORD")
    else:
        pwd = getpass.getpass("Enter decryption password: ")

    if url is None:
        if os.environ.get("SHARE_URL") is not None:
            url = os.environ.get("SHARE_URL")
            assert url is not None
        else:
            url = input("Enter share url: ")

    from rich.progress import Progress
    with Progress(transient=True) as progress:
        _task = progress.add_task("Downloading ... ", total=None)
        url_obj = P(url).download(folder=folder)
    with Progress(transient=True) as progress:
        _task = progress.add_task("Decrypting ... ", total=None)
        res = url_obj.decrypt(pwd=pwd, inplace=True).unzip(inplace=True, merge=True)
        print(f"Decrypted to {res}")


def arg_parser() -> None:
    parser = argparse.ArgumentParser(description='Cloud CLI. It wraps rclone with sane defaults for optimum type time.')

    # positional argument
    parser.add_argument("source", help="file/folder path to be taken from here.")
    parser.add_argument("target", help="file/folder path to be be sent to here.")
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--encrypt", "-e", help="Decrypt after receiving.", action="store_true", default=ArgsDefaults.encrypt)
    parser.add_argument("--zip", "-z", help="unzip after receiving.", action="store_true", default=ArgsDefaults.zip_)
    parser.add_argument("--overwrite", "-w", help="Overwrite existing file.", action="store_true", default=ArgsDefaults.overwrite)
    parser.add_argument("--share", "-s", help="Share file / directory", action="store_true", default=ArgsDefaults.share)
    # optional argument
    parser.add_argument("--rel2home", "-r", help="Relative to `myhome` folder", action="store_true", default=ArgsDefaults.rel2home)
    parser.add_argument("--root", "-R", help="Remote root. None is the default, unless rel2home is raied, making the default `myhome`.", default=ArgsDefaults.root)
    parser.add_argument("--os_specific", "-o", help="OS specific path (relevant only when relative flag is raised as well.", action="store_true", default=ArgsDefaults.os_specific)

    parser.add_argument("--key", "-k", help="Key for encryption", type=str, default=ArgsDefaults.key)
    parser.add_argument("--pwd", "-p", help="Password for encryption", type=str, default=ArgsDefaults.pwd)

    parser.add_argument("--config", "-c",  help="path to cloud.json file.", default=None)

    args = parser.parse_args()
    args_dict = vars(args)
    source: str = args_dict.pop("source")
    target = args_dict.pop("target")
    args_obj = Args(**args_dict)

    if args_obj.config == "ss" and (source.startswith("http") or source.startswith("bit.ly")): return get_shared_file(url=args.source, folder=args.target)
    if args_obj.rel2home is True and args.root is None: args_obj.root = "myhome"

    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    # print(f"{cloud=}, {source=}, {target=}")

    if cloud in source:
        # print(f"Downloading from {source} to {target}")
        P(target).from_cloud(cloud=cloud, remotepath=source.replace(cloud + ":", ""),
                                unzip=args.zip, decrypt=args.encrypt, pwd=args.pwd, key=args.key,
                                overwrite=args.overwrite,
                                rel2home=args.rel2home, os_specific=args.os_specific, root=args.root, strict=False,
                                )
    elif cloud in target:
        res = P(source).to_cloud(cloud=cloud, remotepath=target.replace(cloud + ":", ""),
                                    zip=args.zip, encrypt=args.encrypt, key=args.key, pwd=args.pwd,
                                    rel2home=args.rel2home, root=args.root, os_specific=args.os_specific, strict=False,
                                    share=args.share)
        if args.share: print(res.as_url_str())
    else: raise ValueError(f"Cloud `{cloud}` not found in source or target.")


if __name__ == "__main__":
    arg_parser()
