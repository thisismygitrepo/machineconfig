"""CS
TODO: use typer or typed-argument-parser to parse args
"""

from machineconfig.scripts.python.helpers.helpers2 import parse_cloud_source_target
from machineconfig.scripts.python.helpers.cloud_helpers import Args
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt

import argparse
from rich.console import Console
from rich.panel import Panel

console = Console()


def args_parser():
    title = "☁️  Cloud Sync Utility"
    console.print(Panel(title, title_align="left", border_style="blue"))
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
        title = "🔄 BI-DIRECTIONAL SYNC"
        source_line = f"Source: {source}"
        target_line = f"Target: {target}"
        console.print(Panel(f"{source_line}\n{target_line}", title=title, border_style="blue"))
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync"""
    else:
        title = "📤 ONE-WAY SYNC"
        source_line = f"Source: {source}"
        arrow_line = "↓"
        target_line = f"Target: {target}"
        console.print(Panel(f"{source_line}\n{arrow_line}\n{target_line}", title=title, border_style="blue"))
        if delete:
            rclone_cmd = f'rclone sync -P "{source}" "{target}" --delete-during --transfers={transfers}'
        else:
            rclone_cmd = f'rclone sync -P "{source}" "{target}" --transfers={transfers}'

    rclone_cmd += f" --progress --transfers={transfers} --verbose"
    # rclone_cmd += f"  --vfs-cache-mode full"
    if delete:
        rclone_cmd += " --delete-during"

    if verbose:
        txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, cloud_brand="Unknown")
    else:
        txt = f"""{rclone_cmd}"""

    title = "🚀 EXECUTING COMMAND"
    cmd_line = f"{rclone_cmd[:65]}..."
    console.print(Panel(f"{title}\n{cmd_line}", title="[bold blue]Command[/bold blue]", expand=False))

    # PROGRAM_PATH.write_text(txt, encoding="utf-8")
    import subprocess

    subprocess.run(txt, shell=True, check=True)


if __name__ == "__main__":
    args_parser()
