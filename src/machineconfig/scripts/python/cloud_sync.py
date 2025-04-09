"""CS
TODO: use typer or typed-argument-parser to parse args
"""

from machineconfig.scripts.python.helpers.helpers2 import parse_cloud_source_target
from machineconfig.scripts.python.helpers.cloud_helpers import Args
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
from machineconfig.utils.utils import PROGRAM_PATH
import argparse


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
