from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.utils2 import read_ini
import platform
from typing import Optional
from pathlib import Path


def get_ve_path_and_ipython_profile(init_path: PathExtended) -> tuple[Optional[str], Optional[str]]:
    """Works with .ve.ini .venv and .ve_path"""
    ve_path: Optional[str] = None
    ipy_profile: Optional[str] = None
    tmp = init_path
    for _ in init_path.parents:
        if tmp.joinpath(".ve.ini").exists():
            ini = read_ini(tmp.joinpath(".ve.ini"))
            if ve_path is None:
                try:
                    ve_path = ini["specs"]["ve_path"]
                except KeyError:
                    raise KeyError(f".ve.ini file at {tmp.joinpath('.ve.ini')} is missing the 've_path' key in the 'specs' section.")
                print(f"🐍 Using Virtual Environment: {ve_path}. This is based on this file {tmp.joinpath('.ve.ini')}")
            if ipy_profile is None:
                ipy_profile = ini["specs"]["ipy_profile"]
                print(f"✨ Using IPython profile: {ipy_profile}")
        if ipy_profile is None and tmp.joinpath(".ipy_profile").exists():
            ipy_profile = tmp.joinpath(".ipy_profile").read_text(encoding="utf-8").rstrip()
            print(f"✨ Using IPython profile: {ipy_profile}. This is based on this file {tmp.joinpath('.ipy_profile')}")
        if ve_path is None and tmp.joinpath(".ve_path").exists():
            ve_path = tmp.joinpath(".ve_path").read_text(encoding="utf-8").rstrip().replace("\n", "")
            print(f"🔮 Using Virtual Environment found @ {tmp}/.ve_path: {ve_path}")
        if ve_path is None and tmp.joinpath(".venv").exists():
            print(f"🔮 Using Virtual Environment found @ {tmp}/.venv")
            ve_path = tmp.joinpath(".venv").resolve().__str__()
        tmp = tmp.parent
        if ve_path and ipy_profile:
            break
    else:
        print("🔍 No Virtual Environment or IPython profile found.")
    return ve_path, ipy_profile


def get_repo_root(path: Path) -> Optional[Path]:
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(str(path), search_parent_directories=True)
        root = repo.working_tree_dir
        if root is not None:
            return Path(root)
    except InvalidGitRepositoryError:
        pass
    return None


def get_ve_activate_line(ve_root: str):
    if platform.system() == "Windows":
        activate_ve_line = f". {ve_root}/Scripts/activate.ps1"
    elif platform.system() in ["Linux", "Darwin"]:
        activate_ve_line = f". {ve_root}/bin/activate"
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")
    return activate_ve_line
