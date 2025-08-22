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
                print(f"✨ Using IPython profile: {ipy_profile}")
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


# if platform.system() == "Windows": activate_ve_line = f". $HOME/venvs/{ve_name}/Scripts/activate.ps1"
# elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = f". $HOME/venvs/{ve_name}/bin/activate"
# else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
# return activate_ve_line


def get_ve_activate_line(ve_root: str):
    if platform.system() == "Windows": activate_ve_line = f". {ve_root}/Scripts/activate.ps1"
    elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = f". {ve_root}/bin/activate"
    else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    return activate_ve_line
    # repo_root = get_repo_root(str(a_path))
    # if repo_root is not None and PathExtended(repo_root).joinpath(".venv").exists():
    #     if platform.system() == "Windows":
    #         activate_ve_line = f". {repo_root}\\.venv\\Scripts\\activate.ps1"
    #     elif platform.system() in ["Linux", "Darwin"]:
    #         activate_ve_line = f". {repo_root}/.venv/bin/activate"
    #     else:
    #         raise NotImplementedError(f"Platform {platform.system()} not supported.")
    #     print(f"⚠️ .ve_path not found; using the one found in {repo_root}/.venv")
    # else:
    #     # path passed is not a repo root, or .venv doesn't exist, let's try to find .venv by searching up the directory tree
    #     activate_ve_line = ""  # Initialize to avoid unbound variable warning
    #     tmp = PathExtended(a_path)
    #     for _ in range(len(tmp.parts)):
    #         if tmp.joinpath(".venv").exists():
    #             if platform.system() == "Windows": activate_ve_line = f". {tmp}\\.venv\\Scripts\\activate.ps1"
    #             elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = f". {tmp}/.venv/bin/activate"
    #             print(f"🔮 Using Virtual Environment @ {tmp.joinpath('.venv')}")
    #             break
    #         tmp = tmp.parent
    #     else:  # nothing worked, let's use the default
    #         # activate_ve_line = ". $HOME/scripts/activate_ve"
    #         if platform.system() == "Windows": activate_ve_line = ". $HOME/venvs/ve/Scripts/activate.ps1"
    #         elif platform.system() in ["Linux", "Darwin"]: activate_ve_line = ". $HOME/venvs/ve/bin/activate"
    #         else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    #         print(f"⚠️ Using default virtual environment: {activate_ve_line}")


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


def get_current_ve():
    import sys
    path = PathExtended(sys.executable)  # something like ~\\venvs\\ve\\Scripts\\python.exe'
    if str(PathExtended.home().joinpath("venvs")) in str(path): return path.parent.parent.stem
    else: raise NotImplementedError("❌ Not a kind of virtual enviroment that I expected.")
def get_ve_specs(ve_path: PathExtended) -> dict[str, str]:
    ini = r"[mysection]\n" + ve_path.joinpath("pyvenv.cfg").read_text()
    import configparser
    config = configparser.ConfigParser()
    config.read_string(ini)
    res = dict(config['mysection'])
    return res