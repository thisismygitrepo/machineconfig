from typing import Optional, TypedDict, cast, NotRequired, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

class CLOUD(TypedDict):
    cloud: str
    root: str
    rel2home: bool

    pwd: Optional[str]
    key: Optional[str]
    encrypt: bool

    os_specific: bool
    zip: bool
    share: bool
    overwrite: bool
def read_default_cloud_config() -> CLOUD:
    return {
        "cloud": "mycloud101",
        "root": "myhome",
        "rel2home": False,
        "pwd": None,
        "key": None,
        "encrypt": False,
        "os_specific": False,
        "zip": False,
        "share": False,
        "overwrite": False,
    }

class VE_SPECS(TypedDict):
    ve_path: str
    ipy_profile: NotRequired[str]
class VE_INI(TypedDict):
    specs: NotRequired[VE_SPECS]
    cloud: NotRequired[CLOUD]


def get_ve_path_and_ipython_profile(init_path: "Path") -> tuple[Optional[str], Optional[str]]:
    """Works with .ve.ini .venv"""
    ve_path: Optional[str] = None
    ipy_profile: Optional[str] = None
    tmp = init_path
    from machineconfig.utils.io import read_ini
    for _ in init_path.parents:
        if tmp.joinpath(".ve.ini").exists():
            print(f"🔍 Found .ve.ini @ {tmp}/.ve.ini")
            ini = cast(VE_INI, read_ini(tmp.joinpath(".ve.ini")))
            if ve_path is None:
                if "spdecs" in ini:
                    specs = ini["specs"]
                    if "ve_path" in specs:
                        ve_path = specs["ve_path"]
                        print(f"🐍 Using Virtual Environment: {ve_path}. This is based on this file {tmp.joinpath('.ve.ini')}")
                    else: print(f"⚠️ .ve.ini @ {tmp}/.ve.ini [specs] has no ve_path key.")
                else: print(f"⚠️ .ve.ini @ {tmp}/.ve.ini has no [specs] section.")
            if ipy_profile is None:
                if "specs" in ini:
                    specs = ini["specs"]
                    if "ipy_profile" in specs:
                        ipy_profile = specs["ipy_profile"]
                        print(f"✨ Using IPython profile: {ipy_profile}")
                    else: print(f"⚠️ .ve.ini @ {tmp}/.ve.ini [specs] has no ipy_profile key.")
                else: print(f"⚠️ .ve.ini @ {tmp}/.ve.ini has no [specs] section.")
        if ve_path is None and tmp.joinpath(".venv").exists():
            print(f"🔮 Using Virtual Environment found @ {tmp}/.venv")
            ve_path = tmp.joinpath(".venv").resolve().__str__()
        tmp = tmp.parent
        if ve_path and ipy_profile:
            break
    else:
        print("🔍 No Virtual Environment or IPython profile found.")
    return ve_path, ipy_profile


def get_ve_activate_line(ve_root: str):
    import platform
    from pathlib import Path
    if platform.system() == "Windows":
        q = Path(ve_root).expanduser().relative_to(Path.home()).as_posix()
        activate_ve_line = f". $HOME/{q}/Scripts/activate.ps1"
    elif platform.system() in ["Linux", "Darwin"]:
        activate_ve_line = f". {ve_root}/bin/activate"
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")
    return activate_ve_line

