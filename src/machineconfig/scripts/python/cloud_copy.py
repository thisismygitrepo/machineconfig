"""
CC
"""

from crocodile.file_management import P
from crocodile.core import Struct
from crocodile.meta import RepeatUntilNoException
import getpass
from machineconfig.scripts.python.helpers.cloud_helpers import Args
import argparse
import os
# from dataclasses import dataclass
# from pydantic import BaseModel
from typing import Optional

from machineconfig.scripts.python.helpers.helpers2 import parse_cloud_source_target
from machineconfig.scripts.python.helpers.cloud_helpers import ArgsDefaults
from rich.console import Console
from rich.panel import Panel

console = Console()


def _get_padding(text: str, box_width: int = 150, padding_before: int = 2, padding_after: int = 1) -> str:
    """Calculate the padding needed to align the box correctly.
    
    Args:
        text: The text to pad
        box_width: The total width of the box
        padding_before: The space taken before the text (usually "║ ")
        padding_after: The space needed after the text (usually " ║")
    
    Returns:
        A string of spaces for padding
    """
    # Count visible characters (might not be perfect for all Unicode characters)
    text_length = len(text)
    padding_length = box_width - padding_before - text_length - padding_after
    return ' ' * max(0, padding_length)


@RepeatUntilNoException(retry=3, sleep=1)
def get_securely_shared_file(url: Optional[str] = None, folder: Optional[str] = None) -> None:
    console.print(Panel("🚀 Secure File Downloader", title="[bold blue]Downloader[/bold blue]", border_style="blue"))
    
    folder_obj = P.cwd() if folder is None else P(folder)
    print(f"📂 Target folder: {folder_obj}")
    
    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        print("🔑 Using password from environment variables")
        pwd: str=str(os.environ.get("DECRYPTION_PASSWORD"))
    else:
        pwd = getpass.getpass(prompt="🔑 Enter decryption password: ")
        
    if url is None:
        if os.environ.get("SHARE_URL") is not None:
            url = os.environ.get("SHARE_URL")
            assert url is not None
            print("🔗 Using URL from environment variables")
        else:
            url = input("🔗 Enter share URL: ")
    
    console.print(Panel("📡 Downloading from URL...", title="[bold blue]Download[/bold blue]", border_style="blue"))
    from rich.progress import Progress
    with Progress(transient=True) as progress:
        _task = progress.add_task("Downloading... ", total=None)
        url_obj = P(url).download(folder=folder_obj)
        
    console.print(Panel(f"📥 Downloaded file: {url_obj}", title="[bold green]Success[/bold green]", border_style="green"))
    
    console.print(Panel("🔐 Decrypting and extracting...", title="[bold blue]Processing[/bold blue]", border_style="blue"))
    with Progress(transient=True) as progress:
        _task = progress.add_task("Decrypting... ", total=None)
        tmp_folder = P.tmpdir(prefix="tmp_unzip")
        res = url_obj.decrypt(pwd=pwd, inplace=True).unzip(inplace=True, folder=tmp_folder)
        res.search("*").apply(lambda x: x.move(folder=folder_obj, overwrite=True))


def arg_parser() -> None:
    console.print(Panel("☁️  Cloud Copy Utility", title="[bold blue]Cloud Copy[/bold blue]", border_style="blue", width=152))
    
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
        console.print(Panel("🔒 Detected secure share link", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
        if source.startswith("https://drive.google.com/open?id="):
            source = "https://drive.google.com/uc?export=download&id=" + source.split("https://drive.google.com/open?id=")[1]
            print("🔄 Converting Google Drive link to direct download URL")
        return get_securely_shared_file(url=source, folder=target)

    if args_obj.rel2home is True and args_obj.root is None:
        args_obj.root = "myhome"
        print("🏠 Using 'myhome' as root directory")

    console.print(Panel("🔍 Parsing source and target paths...", title="[bold blue]Info[/bold blue]", border_style="blue"))
    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    
    console.print(Panel("⚙️  Configuration:", title="[bold blue]Config[/bold blue]", border_style="blue"))
    Struct(args_obj.__dict__).print(as_config=True, title="CLI config")

    assert args_obj.key is None, "Key is not supported yet."
    
    if cloud in source:
        console.print(Panel(f"📥 DOWNLOADING FROM CLOUD\n☁️  Cloud: {cloud}\n📂 Source: {source.replace(cloud + ':', '')}\n🎯 Target: {target}", title="[bold blue]Download[/bold blue]", border_style="blue", width=152))
        
        P(target).from_cloud(cloud=cloud, remotepath=source.replace(cloud + ":", ""),
                            unzip=args_obj.zip, decrypt=args_obj.encrypt, pwd=args_obj.pwd,
                            overwrite=args_obj.overwrite,
                            rel2home=args_obj.rel2home, os_specific=args_obj.os_specific, root=args_obj.root, strict=False,
                            )
        console.print(Panel("✅ Download completed successfully", title="[bold green]Success[/bold green]", border_style="green", width=152))
        
    elif cloud in target:
        console.print(Panel(f"📤 UPLOADING TO CLOUD\n☁️  Cloud: {cloud}\n📂 Source: {source}\n🎯 Target: {target.replace(cloud + ':', '')}", title="[bold blue]Upload[/bold blue]", border_style="blue", width=152))
        
        res = P(source).to_cloud(cloud=cloud, remotepath=target.replace(cloud + ":", ""),
                                    zip=args_obj.zip, encrypt=args_obj.encrypt, pwd=args_obj.pwd,
                                    rel2home=args_obj.rel2home, root=args_obj.root, os_specific=args_obj.os_specific, strict=False,
                                    share=args_obj.share)
        console.print(Panel("✅ Upload completed successfully", title="[bold green]Success[/bold green]", border_style="green", width=152))
        
        if args_obj.share:
            fname = f".share_url_{cloud}"
            if P(source).is_dir(): share_url_path = P(source).joinpath(fname)
            else: share_url_path = P(source).with_suffix(fname)
            share_url_path.write_text(res.as_url_str())
            console.print(Panel(f"🔗 SHARE URL GENERATED\n📝 URL file: {share_url_path}\n🌍 {res.as_url_str()}", title="[bold blue]Share[/bold blue]", border_style="blue", width=152))
    else: 
        console.print(Panel(f"❌ ERROR: Cloud '{cloud}' not found in source or target", title="[bold red]Error[/bold red]", border_style="red", width=152))
        raise ValueError(f"Cloud `{cloud}` not found in source or target.")


if __name__ == "__main__":
    arg_parser()
