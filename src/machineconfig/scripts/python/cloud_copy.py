
"""CC
"""

from crocodile.file_management import P
from crocodile.meta import RepeatUntilNoException
import getpass
from machineconfig.scripts.python.cloud_sync import parse_cloud_source_target
import argparse
import os
from typing import Optional


class ArgsDefaults:
    encrypt: bool = False
    zip_: bool = False
    overwrite: bool = False
    share: bool = False
    rel2home = False
    root = None
    os_specific = False
    key = None
    pwd = None


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
        res = url_obj.decrypt(pwd=pwd).unzip(inplace=True)
        print(f"Decrypted to {res}")


def arg_parser() -> None:
    parser = argparse.ArgumentParser(description='Cloud CLI. It wraps rclone with sane defaults for optimum type time.')

    # positional argument
    parser.add_argument("source", help="file/folder path to be taken from here.", default=None)
    parser.add_argument("target", help="file/folder path to be be sent to here.", default=None)
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--encrypt", "-e", help="Decrypt after receiving.", action="store_true")  # default is False
    parser.add_argument("--zip", "-z", help="unzip after receiving.", action="store_true")  # default is False
    parser.add_argument("--overwrite", "-w", help="Overwrite existing file.", action="store_true")  # default is False
    parser.add_argument("--share", "-s", help="Share file / directory", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--rel2home", "-r", help="Relative to `myhome` folder", action="store_true")  # default is False
    parser.add_argument("--root", "-R", help="Remote root. None is the default, unless rel2home is raied, making the default `myhome`.", default=None)  # default is only meaningful when rel2home is True
    parser.add_argument("--os_specific", "-o", help="OS specific path (relevant only when relative flag is raised as well.", action="store_true")

    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    parser.add_argument("--config", "-c",  help="path to cloud.json file.", default=None)

    args = parser.parse_args()

    if args.config == "ss" and str(args.source).startswith("http"): return get_shared_file(folder=args.target)

    if args.rel2home is True and args.root is None: args.root = "myhome"

    cloud, source, target = parse_cloud_source_target(args)
    print(f"{cloud=}, {source=}, {target=}")

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
