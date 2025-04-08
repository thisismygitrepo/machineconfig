"""CS
TODO: use typer or typed-argument-parser to parse args
"""

from crocodile.file_management import P, Read
from crocodile.core import Struct
from machineconfig.scripts.python.helpers.helpers2 import parse_cloud_source_target
from machineconfig.scripts.python.helpers.helpers3 import Args
from machineconfig.utils.utils import PROGRAM_PATH, DEFAULTS_PATH
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
import argparse
import os
from typing import Optional
# from dataclasses import dataclass
# install_n_import("pydantic")
# from tap import Tap


ES = "^"  # chosen carefully to not mean anything on any shell. `$` was a bad choice.


def get_secure_share_cloud_config(interactive: bool, cloud: Optional[str]) -> Args:
    print(f"""
╔{'═' * 70}╗
║ 🔐 Secure Share Cloud Configuration                                       ║
╚{'═' * 70}╝
""")
    
    if cloud is None:
        if os.environ.get("CLOUD_CONFIG_NAME") is not None:
            default_cloud = os.environ.get("CLOUD_CONFIG_NAME")
            assert default_cloud is not None
            cloud = default_cloud
            print(f"☁️  Using cloud from environment: {cloud}")
        else:
            try:
                default_cloud__ = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
            except Exception:
                default_cloud__ = 'No default cloud found.'
            if default_cloud__ == 'No default cloud found.' or interactive:
                # assert default_cloud is not None
                cloud = input(f"☁️  Enter cloud name (default {default_cloud__}): ") or default_cloud__
            else:
                cloud = default_cloud__
                print(f"☁️  Using default cloud: {cloud}")

    default_password_path = P.home().joinpath("dotfiles/creds/passwords/quick_password")
    if default_password_path.exists():
        pwd = default_password_path.read_text().strip()
        default_message = "defaults to quick_password"
    else:
        pwd = ""
        default_message = "no default password found"
    pwd = input(f"🔑 Enter encryption password ({default_message}): ") or pwd
    res = Args(cloud=cloud,
               pwd=pwd, encrypt=True,
               zip=True, overwrite=True, share=True,
               rel2home=True, root="myshare", os_specific=False,)
    
    print(f"""
╭{'─' * 70}╮
│ ⚙️  Using SecureShare cloud config                                        │
╰{'─' * 70}╯
""")
    Struct(res.__dict__).print(as_config=True, title="SecureShare Config")
    return res


def args_parser():
    print(f"""
╔{'═' * 70}╗
║ ☁️  Cloud Sync Utility                                                    ║
╚{'═' * 70}╝
""")
    
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
    source: str=args_dict.pop("source")
    target: str=args_dict.pop("target")
    verbose: bool=args_dict.pop("verbose")
    delete: bool=args_dict.pop("delete")
    bisync: bool=args_dict.pop("bisync")
    transfers: int = args_dict.pop("transfers")
    args_obj = Args(**args_dict)

    args_obj.os_specific = False
    args_obj.rel2home = True

    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    # map short flags to long flags (-u -> --upload), for easier use in the script
    if bisync:
        print(f"""
╔{'═' * 70}╗
║ 🔄 BI-DIRECTIONAL SYNC                                                    ║
╠{'═' * 70}╣
║ Source: {source}                       
║ Target: {target}                       
╚{'═' * 70}╝
""")
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync"""
    else:
        print(f"""
╔{'═' * 70}╗
║ 📤 ONE-WAY SYNC                                                           ║
╠{'═' * 70}╣
║ Source: {source}                       
║ ↓                                                                        ║
║ Target: {target}                       
╚{'═' * 70}╝
""")
        rclone_cmd = f"""rclone sync '{source}' '{target}' """

    rclone_cmd += f" --progress --transfers={transfers} --verbose"
    # rclone_cmd += f"  --vfs-cache-mode full"
    if delete: rclone_cmd += " --delete-during"

    if verbose: txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, cloud_brand="Unknown")
    else: txt = f"""{rclone_cmd}"""
    
    print(f"""
╔{'═' * 70}╗
║ 🚀 EXECUTING COMMAND                                                      ║
╠{'═' * 70}╣
║ {rclone_cmd[:65]}... ║
╚{'═' * 70}╝
""")
    
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
