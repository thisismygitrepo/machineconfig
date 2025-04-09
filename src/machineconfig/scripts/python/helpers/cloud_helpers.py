
from crocodile.core import Struct
from crocodile.file_management import P, Read
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing import Optional
import os
from machineconfig.utils.utils import DEFAULTS_PATH


class ArgsDefaults:
    # source: str=None
    # target: str=None
    encrypt: bool=False
    zip_: bool=False
    overwrite: bool=False
    share: bool=False
    rel2home = False
    root = None
    os_specific = False
    key = None
    pwd = None


@dataclass(config=ConfigDict(extra="forbid", frozen=False))
class Args():
    cloud: Optional[str] = None

    zip: bool=ArgsDefaults.zip_
    overwrite: bool=ArgsDefaults.overwrite
    share: bool=ArgsDefaults.share

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


def find_cloud_config(path: P):
    print(f"""
╭{'─' * 70}╮
│ 🔍 Searching for cloud configuration file...                              │
╰{'─' * 70}╯
""")

    for _i in range(len(path.parts)):
        if path.joinpath("cloud.json").exists():
            res = Args.from_config(path.joinpath("cloud.json"))
            print(f"""
╭{'─' * 70}╮
│ ✅ Found cloud config at: {path.joinpath('cloud.json')}   │
╰{'─' * 70}╯
""")
            Struct(res.__dict__).print(as_config=True, title="Cloud Config")
            return res
        path = path.parent

    print("❌ No cloud configuration file found")
    return None


def absolute(path: str) -> P:
    obj = P(path).expanduser()
    if not path.startswith(".") and  obj.exists(): return obj
    try_absing =  P.cwd().joinpath(path)
    if try_absing.exists(): return try_absing
    print(f"""
╭{'─' * 70}╮
│ ⚠️  WARNING:                                                              │
│ Path {path} could not be resolved to absolute path.         
│ Trying to resolve symlinks (this may result in unintended paths).        │
╰{'─' * 70}╯
""")
    return obj.absolute()



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
