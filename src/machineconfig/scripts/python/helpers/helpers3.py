from crocodile.core import Struct
from crocodile.file_management import P
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass, Read
from typing import Optional

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


