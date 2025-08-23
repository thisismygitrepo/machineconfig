from crocodile.file_management import P as PathExtended
from machineconfig.utils.utils2 import read_ini
import platform
from typing import Optional


def get_ve_path_and_ipython_profile(init_path: PathExtended) -> tuple[Optional[str], Optional[str]]:
    """Works with .ve.ini .venv and .ve_path"""
    ve_path: Optional[str] = None
    ipy_profile: Optional[str] = None
    tmp = init_path
    for _ in init_path.parents:
        if tmp.joinpath(".ve.ini").exists():
            ini = read_ini(tmp.joinpath(".ve.ini"))
            ve_path = ini["specs"]["ve_path"]
            # py_version = ini["specs"]["py_version"]
            ipy_profile = ini["specs"]["ipy_profile"]
            print(f"🐍 Using Virtual Environment: {ve_path}. This is based on this file {tmp.joinpath('.ve.ini')}")
            print(f"✨ Using IPython profile: {ipy_profile}")
            break
        if tmp.joinpath(".ve_path").exists() or tmp.joinpath(".ipy_profile").exists():
            if tmp.joinpath(".ipy_profile").exists():
                ipy_profile = tmp.joinpath(".ipy_profile").read_text().rstrip()
                print(f"✨ Using IPython profile: {ipy_profile}. This is based on this file {tmp.joinpath('.ipy_profile')}")
            if tmp.joinpath(".ve_path").exists():
                ve_path = tmp.joinpath(".ve_path").read_text().rstrip().replace("\n", "")
                print(f"🔮 Using Virtual Environment found @ {tmp}/.ve_path: {ve_path}")
            break
        if tmp.joinpath(".venv").exists():
            ve_path = tmp.joinpath(".venv").resolve().__str__()
            break
        tmp = tmp.parent
    return ve_path, ipy_profile


def get_repo_root(choice_file: str) -> Optional[str]:
    from git import Repo, InvalidGitRepositoryError
    try:
        repo = Repo(PathExtended(choice_file), search_parent_directories=True)
        repo_root = str(repo.working_tree_dir) if repo.working_tree_dir else None
    except InvalidGitRepositoryError:
        repo_root = None
    return repo_root

def get_ve_activate_line(ve_root: str):
    if platform.system() == "Windows": activate_ve_line = f". {ve_root}/Scripts/activate.ps1"
    elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = f". {ve_root}/bin/activate"
    else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    return activate_ve_line

def get_installed_interpreters() -> list[PathExtended]:
    system = platform.system()
    if system == "Windows":
        tmp: list[PathExtended] = PathExtended.get_env().PATH.search("python.exe").reduce(func=lambda x, y: x+y).list[1:]
    else:
        all_matches: list[PathExtended] = PathExtended.get_env().PATH.search("python3*").reduce(lambda x, y: x+y).list
        tmp = list(set([x for x in all_matches if (not x.is_symlink()) and ("-" not in str(x))]))
    print("🔍 Found Python interpreters:")
    for interpreter_path in tmp:
        print(interpreter_path)
    return list(set([PathExtended(x) for x in tmp]))
