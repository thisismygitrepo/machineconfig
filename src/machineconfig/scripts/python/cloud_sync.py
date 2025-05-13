"""CS
TODO: use typer or typed-argument-parser to parse args
"""

from machineconfig.scripts.python.helpers.helpers2 import parse_cloud_source_target
from machineconfig.scripts.python.helpers.cloud_helpers import Args
from machineconfig.scripts.python.cloud_mount import get_mprocs_mount_txt
from machineconfig.utils.utils import PROGRAM_PATH
import argparse

BOX_WIDTH = 150  # width for box drawing


def _get_padding(text: str, padding_before: int = 2, padding_after: int = 1) -> str:
    """Calculate the padding needed to align the box correctly.
    
    Args:
        text: The text to pad
        padding_before: The space taken before the text (usually "║ ")
        padding_after: The space needed after the text (usually " ║")
    
    Returns:
        A string of spaces for padding
    """
    # Count visible characters (might not be perfect for all Unicode characters)
    text_length = len(text)
    padding_length = BOX_WIDTH - padding_before - text_length - padding_after
    return ' ' * max(0, padding_length)


def args_parser():
    title = "☁️  Cloud Sync Utility"
    print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}{_get_padding(title)}║
╚{'═' * BOX_WIDTH}╝
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
        title = "🔄 BI-DIRECTIONAL SYNC"
        source_line = f"Source: {source}"
        target_line = f"Target: {target}"
        print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}{_get_padding(title)}║
╠{'═' * BOX_WIDTH}╣
║ {source_line}{_get_padding(source_line)}║
║ {target_line}{_get_padding(target_line)}║
╚{'═' * BOX_WIDTH}╝
""")
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync"""
    else:
        title = "📤 ONE-WAY SYNC"
        source_line = f"Source: {source}"
        arrow_line = "↓"
        target_line = f"Target: {target}"
        print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}{_get_padding(title)}║
╠{'═' * BOX_WIDTH}╣
║ {source_line}{_get_padding(source_line)}║
║ {arrow_line}{_get_padding(arrow_line)}║
║ {target_line}{_get_padding(target_line)}║
╚{'═' * BOX_WIDTH}╝
""")
        rclone_cmd = f"""rclone sync '{source}' '{target}' """

    rclone_cmd += f" --progress --transfers={transfers} --verbose"
    # rclone_cmd += f"  --vfs-cache-mode full"
    if delete: rclone_cmd += " --delete-during"

    if verbose: txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, cloud_brand="Unknown")
    else: txt = f"""{rclone_cmd}"""
    
    title = "🚀 EXECUTING COMMAND"
    cmd_line = f"{rclone_cmd[:65]}..."
    print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}{_get_padding(title)}║
╠{'═' * BOX_WIDTH}╣
║ {cmd_line}{_get_padding(cmd_line)}║
╚{'═' * BOX_WIDTH}╝
""")
    
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    args_parser()
