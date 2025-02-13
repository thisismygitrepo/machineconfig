"""
CC
"""

from crocodile.file_management import P
from crocodile.core import Struct
from crocodile.meta import RepeatUntilNoException
import getpass
from machineconfig.scripts.python.cloud_sync import parse_cloud_source_target, ArgsDefaults, Args
import argparse
import os
# from dataclasses import dataclass
# from pydantic import BaseModel
from typing import Optional


@RepeatUntilNoException(retry=3, sleep=1)
def get_securely_shared_file(url: Optional[str] = None, folder: Optional[str] = None) -> None:
    folder_obj = P.cwd() if folder is None else P(folder)
    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        pwd: str=str(os.environ.get("DECRYPTION_PASSWORD"))
    else:
        pwd = getpass.getpass(prompt="Enter decryption password: ")
    if url is None:
        if os.environ.get("SHARE_URL") is not None:
            url = os.environ.get("SHARE_URL")
            assert url is not None
        else:
            url = input("Enter share url: ")
    from rich.progress import Progress
    with Progress(transient=True) as progress:
        _task = progress.add_task("Downloading ... ", total=None)
        url_obj = P(url).download(folder=folder_obj)
        print(f"📥 Downloaded to {url_obj}")
    with Progress(transient=True) as progress:
        _task = progress.add_task("Decrypting ... ", total=None)
        tmp_folder = P.tmpdir(prefix="tmp_unzip")
        res = url_obj.decrypt(pwd=pwd, inplace=True).unzip(inplace=True, folder=tmp_folder)
        res.search("*").apply(lambda x: x.move(folder=folder_obj, overwrite=True))
        print(f"🔓 Decrypted to {res}")


def arg_parser() -> None:
    parser = argparse.ArgumentParser(description='🚀 Cloud CLI. It wraps rclone with sane defaults for optimum type time.')

    # positional argument
    parser.add_argument("source", help="📂 file/folder path to be taken from here.")
    parser.add_argument("target", help="🎯 file/folder path to be be sent to here.")

    parser.add_argument("--overwrite", "-w", help="✍️ Overwrite existing file.", action="store_true", default=ArgsDefaults.overwrite)
    parser.add_argument("--share", "-s", help="🔗 Share file / directory", action="store_true", default=ArgsDefaults.share)
    parser.add_argument("--rel2home", "-r", help="🏠 Relative to `myhome` folder", action="store_true", default=ArgsDefaults.rel2home)
    parser.add_argument("--root", "-R", help="🌳 Remote root. None is the default, unless rel2home is raied, making the default `myhome`.", default=ArgsDefaults.root)

    parser.add_argument("--key", "-k", help="🔑 Key for encryption", type=str, default=ArgsDefaults.key)
    parser.add_argument("--pwd", "-p", help="🔒 Password for encryption", type=str, default=ArgsDefaults.pwd)
    parser.add_argument("--encrypt", "-e", help="🔐 Decrypt after receiving.", action="store_true", default=ArgsDefaults.encrypt)
    parser.add_argument("--zip", "-z", help="📦 unzip after receiving.", action="store_true", default=ArgsDefaults.zip_)
    parser.add_argument("--os_specific", "-o", help="💻 choose path specific for this OS.", action="store_true", default=ArgsDefaults.os_specific)

    parser.add_argument("--config", "-c",  help="⚙️ path to cloud.json file.", default=None)

    args = parser.parse_args()
    args_dict = vars(args)
    source: str = args_dict.pop("source")
    target: str = args_dict.pop("target")
    args_obj = Args(**args_dict)

    if args_obj.config == "ss" and (source.startswith("http") or source.startswith("bit.ly")):
        if source.startswith("https://drive.google.com/open?id="):
            source = "https://drive.google.com/uc?export=download&id=" + source.split("https://drive.google.com/open?id=")[1]
        return get_securely_shared_file(url=source, folder=target)

    if args_obj.rel2home is True and args_obj.root is None:
        args_obj.root = "myhome"

    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    Struct(args_obj.__dict__).print(as_config=True, title="CLI config")

    assert args_obj.key is None, "Key is not supported yet."
    if cloud in source:
        P(target).from_cloud(cloud=cloud, remotepath=source.replace(cloud + ":", ""),
                            unzip=args_obj.zip, decrypt=args_obj.encrypt, pwd=args_obj.pwd,
                            overwrite=args_obj.overwrite,
                            rel2home=args_obj.rel2home, os_specific=args_obj.os_specific, root=args_obj.root, strict=False,
                            )
    elif cloud in target:
        res = P(source).to_cloud(cloud=cloud, remotepath=target.replace(cloud + ":", ""),
                                    zip=args_obj.zip, encrypt=args_obj.encrypt, pwd=args_obj.pwd,
                                    rel2home=args_obj.rel2home, root=args_obj.root, os_specific=args_obj.os_specific, strict=False,
                                    share=args_obj.share)
        if args_obj.share:
            fname = f".share_url_{cloud}"
            if P(source).is_dir(): share_url_path = P(source).joinpath(fname)
            else: share_url_path = P(source).with_suffix(fname)
            share_url_path.write_text(res.as_url_str())
            print(f"🔗 share url saved to {share_url_path}")
            print(f"🌍 {res.as_url_str()}")
    else: raise ValueError(f"Cloud `{cloud}` not found in source or target.")


if __name__ == "__main__":
    arg_parser()
