from pathlib import Path
from machineconfig.utils.io import read_ini, read_json
from machineconfig.utils.accessories import pprint
from typing import Optional
import os
from machineconfig.utils.source_of_truth import DEFAULTS_PATH
from rich.console import Console
from rich.panel import Panel
from rich import box  # Import box
from dataclasses import dataclass

console = Console()



class ArgsDefaults:
    # source: str=None
    # target: str=None
    encrypt: bool = False
    zip_: bool = False
    overwrite: bool = False
    share: bool = False
    rel2home = False
    root = None
    os_specific = False
    key = None
    pwd = None

@dataclass
class Args:
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
    def from_config(config_path: Path):
        return Args(**read_json(config_path))


def find_cloud_config(path: Path):
    display_header(f"Searching for cloud configuration file @ {path}")

    for _i in range(len(path.parts)):
        if path.joinpath("cloud.json").exists():
            res = Args.from_config(path.joinpath("cloud.json"))
            display_success(f"Found cloud config at: {path.joinpath('cloud.json')}")
            pprint(res.__dict__, "Cloud Config")
            return res
        path = path.parent

    display_error("No cloud configuration file found")
    return None


def absolute(path: str) -> Path:
    obj = Path(path).expanduser()
    if not path.startswith(".") and obj.exists():
        return obj
    try_absing = Path.cwd().joinpath(path)
    if try_absing.exists():
        return try_absing
    display_warning(f"Path {path} could not be resolved to absolute path.")
    display_warning("Trying to resolve symlinks (this may result in unintended paths).")
    return obj.absolute()


def get_secure_share_cloud_config(interactive: bool, cloud: Optional[str]) -> Args:
    console = Console()
    console.print(Panel("🔐 Secure Share Cloud Configuration", expand=False))

    if cloud is None:
        if os.environ.get("CLOUD_CONFIG_NAME") is not None:
            default_cloud = os.environ.get("CLOUD_CONFIG_NAME")
            assert default_cloud is not None
            cloud = default_cloud
            console.print(f"☁️  Using cloud from environment: {cloud}")
        else:
            try:
                default_cloud__ = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            except Exception:
                default_cloud__ = "No default cloud found."
            if default_cloud__ == "No default cloud found." or interactive:
                # assert default_cloud is not None
                cloud = input(f"☁️  Enter cloud name (default {default_cloud__}): ") or default_cloud__
            else:
                cloud = default_cloud__
                console.print(f"☁️  Using default cloud: {cloud}")

    default_password_path = Path.home().joinpath("dotfiles/creds/passwords/quick_password")
    if default_password_path.exists():
        pwd = default_password_path.read_text(encoding="utf-8").strip()
        default_message = "defaults to quick_password"
    else:
        pwd = ""
        default_message = "no default password found"
    pwd = input(f"🔑 Enter encryption password ({default_message}): ") or pwd
    res = Args(cloud=cloud, pwd=pwd, encrypt=True, zip=True, overwrite=True, share=True, rel2home=True, root="myshare", os_specific=False)

    display_success("Using SecureShare cloud config")
    pprint(res.__dict__, "SecureShare Config")
    return res


def display_header(title: str):
    console.print(Panel(title, box=box.DOUBLE_EDGE, title_align="left"))  # Replace print with Panel


def display_subheader(title: str):
    console.print(Panel(title, box=box.ROUNDED, title_align="left"))  # Replace print with Panel


def display_content(content: str):
    console.print(Panel(content, box=box.ROUNDED, title_align="left"))  # Replace print with Panel


def display_status(status: str):
    console.print(Panel(status, box=box.ROUNDED, title_align="left"))  # Replace print with Panel


def display_success(message: str):
    console.print(Panel(message, box=box.ROUNDED, border_style="green", title_align="left"))  # Replace print with Panel


def display_warning(message: str):
    console.print(Panel(message, box=box.ROUNDED, border_style="yellow", title_align="left"))  # Replace print with Panel


def display_error(message: str):
    console.print(Panel(message, box=box.ROUNDED, border_style="red", title_align="left"))  # Replace print with Panel
