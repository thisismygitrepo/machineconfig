
"""python and ve installation related utils
"""

from crocodile.file_management import P


def get_ipython_profile(init_path: P):
    a_path = init_path
    ipy_profile: str = "profile_default"
    idx = len(a_path.parts)
    while idx >= 0:
        if a_path.joinpath(".ipy_profile").exists():
            ipy_profile = a_path.joinpath(".ipy_profile").read_text().rstrip()
            print(f"✅ Using IPython profile: {ipy_profile}")
            break
        idx -= 1
        a_path = a_path.parent
    return ipy_profile


def get_ve_profile(init_path: P, strict: bool = False):
    ve = ""
    tmp = init_path
    for _ in init_path.parents:
        if tmp.joinpath(".ve_path").exists():
            ve = P(tmp.joinpath(".ve_path").read_text().rstrip().replace("\n", "")).name
            print(f"✅ Using Virtual Environment: {ve}")
            break
        tmp = tmp.parent
    if ve == "" and strict: raise ValueError("❌ No virtual environment found.")
    return ve


def get_current_ve():
    import sys
    path = P(sys.executable)  # something like ~\\venvs\\ve\\Scripts\\python.exe'
    if str(P.home().joinpath("venvs")) in str(path): return path.parent.parent.stem
    else: raise NotImplementedError("Not a kind of virtual enviroment that I expected.")


def get_installed_interpreters() -> list[P]:
    import platform
    system = platform.system()
    from crocodile.file_management import List
    if system == "Windows":
        tmp: list[P] = P.get_env().PATH.search("python.exe").reduce().list[1:]
        List(tmp).print()
    else:
        tmp = list(set(List(P.get_env().PATH.search("python3*").reduce()).filter(lambda x: not x.is_symlink() and "-" not in x)))  # type: ignore
        List(tmp).print()
    return [P(x) for x in tmp]


def get_ve_specs(ve_path: P) -> dict[str, str]:
    ini = r"[mysection]\n" + ve_path.joinpath("pyvenv.cfg").read_text()
    import configparser
    config = configparser.ConfigParser()
    config.read_string(ini)
    res = dict(config['mysection'])
    res['version_major_minor'] = ".".join(res['version'].split(".")[0:2])
    return res
