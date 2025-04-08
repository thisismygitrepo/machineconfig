
from crocodile.core import List
from crocodile.file_management import P, Read
import platform
from typing import Optional


def get_ipython_profile(init_path: P, ve_name: Optional[str] = None):
    """Relies on .ipy_profile"""
    a_path = init_path
    ipy_profile: str = "default"
    idx = len(a_path.parts)
    while idx >= 0:
        if a_path.joinpath(".ipy_profile").exists():
            ipy_profile = a_path.joinpath(".ipy_profile").read_text().rstrip()
            print(f"✨ Using IPython profile: {ipy_profile}")
            break
        idx -= 1
        a_path = a_path.parent
    else:
        if ve_name is not None and P.home().joinpath(".ipython", f"profile_{ve_name}").exists():
            ipy_profile = ve_name
            print(f"✨ Using IPython profile: {ipy_profile}")
        else:
            print(f"⚠️ Using default IPython: {ipy_profile}")
    return ipy_profile


def get_ve_profile(init_path: P) -> Optional[str]:
    """Relies on .ve_path"""
    ve: Optional[str] = None
    tmp = init_path
    for _ in init_path.parents:
        if tmp.joinpath(".ve_path").exists():
            ve = P(tmp.joinpath(".ve_path").read_text().rstrip().replace("\n", "")).name
            print(f"🔮 Using Virtual Environment found @ {tmp}/.ve_path: {ve}")
            break
        tmp = tmp.parent
    return ve


def get_repo_root(choice_file: str) -> Optional[str]:
    from git import Repo, InvalidGitRepositoryError
    try:
        repo = Repo(P(choice_file), search_parent_directories=True)
        # Convert PathLike to str to satisfy mypy
        repo_root = str(repo.working_tree_dir) if repo.working_tree_dir else None
    except InvalidGitRepositoryError:
        repo_root = None
    return repo_root


def get_ve_activate_line(ve_name: Optional[str], a_path: str):

    if ve_name == "" or ve_name is None:
        ve_profile_maybe = get_ve_profile(P(a_path))
        if ve_profile_maybe is not None:
            # activate_ve_line = f". $HOME/scripts/activate_ve {ve_resolved}"
            if platform.system() == "Windows": activate_ve_line = f". $HOME/venvs/{ve_profile_maybe}/Scripts/activate.ps1"
            elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = f". $HOME/venvs/{ve_profile_maybe}/bin/activate"
            else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
            return activate_ve_line

    repo_root = get_repo_root(str(a_path))
    if repo_root is not None and P(repo_root).joinpath(".venv").exists():
        if platform.system() == "Windows":
            activate_ve_line = f". {repo_root}\\.venv\\Scripts\\activate.ps1"
        elif platform.system() in ["Linux", "Darwin"]:
            activate_ve_line = f". {repo_root}/.venv/bin/activate"
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")
        print(f"⚠️ .ve_path not found; using the one found in {repo_root}/.venv")
    else:
        # path passed is not a repo root, or .venv doesn't exist, let's try to find .venv by searching up the directory tree
        tmp = P(a_path)
        for _ in range(len(tmp.parts)):
            if tmp.joinpath(".venv").exists():
                if platform.system() == "Windows": activate_ve_line = f". {tmp}\\.venv\\Scripts\\activate.ps1"
                elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = f". {tmp}/.venv/bin/activate"
                print(f"🔮 Using Virtual Environment @ {tmp.joinpath('.venv')}")
                break
            tmp = tmp.parent
        else:  # nothing worked, let's use the default
            # activate_ve_line = ". $HOME/scripts/activate_ve"
            if platform.system() == "Windows": activate_ve_line = ". $HOME/venvs/ve/Scripts/activate.ps1"
            elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = ". $HOME/venvs/ve/bin/activate"
            else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
            print(f"⚠️ Using default virtual environment: {activate_ve_line}")
    return activate_ve_line


def get_ve_name_and_ipython_profile(init_path: P):
    ve_name = "ve"
    ipy_profile = "default"
    tmp = init_path
    for _ in init_path.parents:
        if tmp.joinpath(".ve.ini").exists():
            ini = Read.ini(tmp.joinpath(".ve.ini"))
            ve_name = ini["specs"]["ve_name"]
            # py_version = ini["specs"]["py_version"]
            ipy_profile = ini["specs"]["ipy_profile"]
            print(f"🐍 Using Virtual Environment: {ve_name}")
            print(f"✨ Using IPython profile: {ipy_profile}")
            break
        tmp = tmp.parent
    return ve_name, ipy_profile


def get_installed_interpreters() -> list[P]:
    system = platform.system()
    if system == "Windows":
        tmp: list[P] = P.get_env().PATH.search("python.exe").reduce(func=lambda x, y: x+y).list[1:]
    else:
        items: List[P] = P.get_env().PATH.search("python3*").reduce(lambda x, y: x+y)
        tmp = list(set(items.filter(lambda x: not x.is_symlink() and "-" not in x)))
    print("🔍 Found Python interpreters:")
    List(tmp).print()
    return list(set([P(x) for x in tmp]))


def get_current_ve():
    import sys
    path = P(sys.executable)  # something like ~\\venvs\\ve\\Scripts\\python.exe'
    if str(P.home().joinpath("venvs")) in str(path): return path.parent.parent.stem
    else: raise NotImplementedError("❌ Not a kind of virtual enviroment that I expected.")


def get_ve_specs(ve_path: P) -> dict[str, str]:
    ini = r"[mysection]\n" + ve_path.joinpath("pyvenv.cfg").read_text()
    import configparser
    config = configparser.ConfigParser()
    config.read_string(ini)
    res = dict(config['mysection'])
    return res