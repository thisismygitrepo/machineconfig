
"""python and ve installation related utils
"""

from crocodile.core import Struct, Save, List
from crocodile.file_management import P, Read

from machineconfig.utils.utils import LIBRARY_ROOT
import platform
from dataclasses import dataclass, asdict
from typing import Optional, Literal


@dataclass
class VE_Specs:
    ve_name: str
    py_version: str
    ipy_profile: str
    os: str


@dataclass
class VE_INI:
    specs: VE_Specs


def get_ipython_profile(init_path: P):
    """Relies on .ipy_profile"""
    a_path = init_path
    ipy_profile: str = "default"
    idx = len(a_path.parts)
    while idx >= 0:
        if a_path.joinpath(".ipy_profile").exists():
            ipy_profile = a_path.joinpath(".ipy_profile").read_text().rstrip()
            print(f"✅ Using IPython profile: {ipy_profile}")
            break
        idx -= 1
        a_path = a_path.parent
    else:
        print(f"⚠️ Using default IPython: {ipy_profile}")
    return ipy_profile


def get_ve_profile(init_path: P, strict: bool = False):
    """Relies on .ve_path"""
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
            print(f"✅ Using Virtual Environment: {ve_name}")
            print(f"✅ Using IPython profile: {ipy_profile}")
            break
        tmp = tmp.parent
    return ve_name, ipy_profile


def get_current_ve():
    import sys
    path = P(sys.executable)  # something like ~\\venvs\\ve\\Scripts\\python.exe'
    if str(P.home().joinpath("venvs")) in str(path): return path.parent.parent.stem
    else: raise NotImplementedError("Not a kind of virtual enviroment that I expected.")


def get_installed_interpreters() -> list[P]:
    system = platform.system()
    if system == "Windows":
        tmp: list[P] = P.get_env().PATH.search("python.exe").reduce(func=lambda x, y: x+y).list[1:]
    else:
        items: List[P] = P.get_env().PATH.search("python3*").reduce(lambda x, y: x+y)
        tmp = list(set(items.filter(lambda x: not x.is_symlink() and "-" not in x)))
    List(tmp).print()
    return list(set([P(x) for x in tmp]))


def get_ve_specs(ve_path: P) -> dict[str, str]:
    ini = r"[mysection]\n" + ve_path.joinpath("pyvenv.cfg").read_text()
    import configparser
    config = configparser.ConfigParser()
    config.read_string(ini)
    res = dict(config['mysection'])
    # try:
    #     res['version_major_minor'] = ".".join(res['version'].split(".")[0:2])
    # except KeyError:
    #     # res['version_major_minor'] = ".".join(res['version_info'].split(".")[0:2])
    return res


def get_ve_install_script(ve_name: Optional[str] = None, py_version: Optional[str] = None,
                          install_crocodile_and_machineconfig: Optional[bool] = None,
                          delete_if_exists: bool = True,
                        #   system: Optional[Literal["Windows", "Linux"]] = None
                          ) -> str:
    from rich.console import Console
    console = Console()
    if py_version is None:
        print("\n\n")
        console.rule("Existing Python versions", style="bold red")
        res = get_installed_interpreters()
        List(res).print()
        print("\n\n")
        dotted_py_version = input("Enter python version (3.11): ") or "3.11"
    else:
        dotted_py_version = py_version

    if ve_name is None:
        console.rule("Existing virtual environments")
        for ve_path in P.home().joinpath("venvs").search("*", files=False):
            try:
                ve_specs = get_ve_specs(ve_path)
            except Exception as _e:
                continue
            Struct(ve_specs).print(title=ve_path.stem, as_config=True)
        ve_name = input("Enter virtual environment name (tst): ") or "tst"

    if install_crocodile_and_machineconfig is None:
        essential_repos = input("Install essential repos? (y/[n]): ") == "y"
        other_repos = input("Input space separated other packages: ")
    else:
        essential_repos = install_crocodile_and_machineconfig
        other_repos = ""

    env_path = P.home().joinpath("venvs", ve_name)
    if delete_if_exists and env_path.exists():
        sure = input(f"An existing environment found. Are you sure you want to delete {env_path} before making new one? (y/[n]): ") == "y"
        console.rule("Deleting existing enviroment with similar name")
        env_path.delete(sure=sure)

    system = platform.system()
    if system == "Windows":
        script = get_ps1_ve_install_script(ve_name=ve_name, py_version=dotted_py_version, use_web=False)
    elif system == "Linux":
        script = get_bash_ve_install_script(ve_name=ve_name, py_version=dotted_py_version, use_web=False)
    else:
        raise NotImplementedError(f"System {system} not supported.")

    if essential_repos:
        if system == "Windows":
            script += "\n" + get_ps1_repos_install_script(ve_name=ve_name, use_web=False)
        elif system == "Linux":
            script += "\n" + get_bash_repos_install_script(ve_name=ve_name, use_web=False)
        else:
            raise NotImplementedError(f"System {system} not supported.")

    if other_repos != "": script += "\n$HOME/.cargo/bin/uv pip install " + other_repos

    link_ve: str = input(f"Symlink to .venv from {P.cwd()}? (y/[n]): ") == "y"
    if link_ve:

        target = P.cwd().joinpath(".venv")
        source = P.home().joinpath("venvs", ve_name)
        if system == "Windows": cmd = f'New-Item -ItemType SymbolicLink -Path "{target}" -Target "{source}"'
        elif system == "Linux": cmd = f'ln -s "{source}" "{target}"'
        else: raise NotImplementedError(f"System {system} not supported.")
        script += f"\n{cmd}"

        P.cwd().joinpath(".ve_path").write_text(f"~/venvs/{ve_name}")
        ve_ini_specs = VE_Specs(ve_name=ve_name, py_version=dotted_py_version, ipy_profile="default", os=system)
        ve_ini = VE_INI(specs=ve_ini_specs)
        Save.ini(obj=asdict(ve_ini), path=P.cwd().joinpath(".ve.ini"))
        vscode = P.cwd().joinpath(".vscode/settings.json")
        if vscode.exists():
            settings = Read.json(vscode)
        else:
            settings = {}
        if system == "Windows":
            settings["python.defaultInterpreterPath"] = P.home().joinpath("venvs", ve_name, "Scripts", "python.exe").as_posix()
        elif system == "Linux":
            settings["python.defaultInterpreterPath"] = P.home().joinpath("venvs", ve_name, "bin", "python").as_posix()
        Save.json(obj=settings, path=vscode, indent=4)
    return script


def get_ve_install_script_from_specs(repo_root: str, system: Literal["Windows", "Linux"]):
    ini_file = P(repo_root).joinpath(".ve.ini")
    assert ini_file.exists(), f"File {ini_file} does not exist."
    ini = Read.ini(ini_file)
    ve_name = ini["specs"]["ve_name"]
    py_version = ini["specs"]["py_version"]
    ipy_profile = ini["specs"]["ipy_profile"]

    # for backward compatibility:
    ini_file.with_name(".ve_path").write_text(f"~/venvs/{ve_name}")
    ini_file.with_name(".ipy_profile").write_text(ipy_profile)

    vscode_settings = P(repo_root).joinpath(".vscode/settings.json")
    if vscode_settings.exists():
        settings = Read.json(vscode_settings)
    else:
        settings = {}
    if system == "Windows":
        settings["python.defaultInterpreterPath"] = f"~/venvs/{ve_name}/Scripts/python.exe"
    elif system == "Linux":
        settings["python.defaultInterpreterPath"] = f"~/venvs/{ve_name}/bin/python"
        pass
    else:
        raise NotImplementedError(f"System {system} not supported.")
    Save.json(obj=settings, path=vscode_settings, indent=4)

    subpath = "versions/init"
    base_path = P(repo_root).joinpath(subpath).create()
    if system == "Windows":
        script = get_ps1_ve_install_script(ve_name=ve_name, py_version=py_version)
        base_path.joinpath("install_ve.ps1").write_text(script)
    elif system == "Linux":
        script = get_bash_ve_install_script(ve_name=ve_name, py_version=py_version)
        base_path.joinpath("install_ve.sh").write_text(script)
    else:
        raise NotImplementedError(f"System {system} not supported.")

    base_path.joinpath("install_requirements.ps1").write_text(get_install_requirements_template(repo_root=P(repo_root), requirements_subpath=subpath))
    base_path.joinpath("install_requirements.sh").write_text(get_install_requirements_template(repo_root=P(repo_root), requirements_subpath=subpath))

    # vscode:
    if not system == "Windows":  # symlinks on windows require admin rights.
        P(repo_root).joinpath(".venv").symlink_to(target=P.home().joinpath("venvs", ve_name), strict=False)
        # set strict to False since ve doesn't exist yet.
    return script


def get_ps1_ve_install_script(ve_name: str, py_version: str, use_web: bool = False):
    if use_web:
        install_line = """(Invoke-WebRequest https://bit.ly/cfgvewindows).Content | Invoke-Expression"""
    else:
        system_ = platform.system()
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system_.lower()}/ve.{'ps1' if system_ == 'Windows' else 'sh'}").read_text()
    template = f"""
$ve_name = '{ve_name}'
$py_version = '{py_version}'  # type: ignore
{install_line}
. $HOME/scripts/activate_ve $ve_name
"""
    return template
def get_bash_ve_install_script(ve_name: str, py_version: str, use_web: bool = False):
    if use_web: install_line = """curl -L https://bit.ly/cfgvelinux | bash"""
    else:
        system_ = platform.system()
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system_.lower()}/ve.{'ps1' if system_ == 'Windows' else 'sh'}").read_text()
    template = f"""
export ve_name='{ve_name}'
export py_version='{py_version}'  # type: ignore
{install_line}
. $HOME/scripts/activate_ve $ve_name
"""
    return template
def get_ps1_repos_install_script(ve_name: str, use_web: bool = False):
    if use_web: install_line = """(Invoke-WebRequest https://bit.ly/cfgreposwindows).Content | Invoke-Expression"""
    else:
        system_ = platform.system()
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system_.lower()}/repos.{'ps1' if system_ == 'Windows' else 'sh'}").read_text()
    template = f"""
$ve_name = '{ve_name}'
. $HOME/scripts/activate_ve $ve_name
{install_line}
"""
    return template

def get_bash_repos_install_script(ve_name: str, use_web: bool = False):
    if use_web: install_line = """curl -L https://bit.ly/cfgreposlinux | bash"""
    else:
        system_ = platform.system()
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system_.lower()}/repos.{'ps1' if system_ == 'Windows' else 'sh'}").read_text()
    template = f"""
export ve_name='{ve_name}'
. $HOME/scripts/activate_ve $ve_name
{install_line}
"""
    return template


def get_install_requirements_template(repo_root: P, requirements_subpath: str):
    return f"""
# This is a template that is meant to be modified manually to install requirements.txt and editable packages.
# one can dispense with this and install libraries manually and on adhoc-basis and then use version_checkout utility.

set -e  # exit on error, you don't want to install reqiurements in wrong environment.
cd $HOME/{repo_root.rel2home().as_posix()}
. $HOME/scripts/activate_ve 've'
pip install -r {requirements_subpath}/requirements.txt
pip install -e .

# cd ~/code; git clone https://github.com/thisismygitrepo/crocodile.git --origin origin
# cd ~/code/crocodile; git remote set-url origin https://github.com/thisismygitrepo/crocodile.git
# cd ~/code/crocodile; git remote add origin https://github.com/thisismygitrepo/crocodile.git
# cd ~/code/crocodile; pip install -e .

# cd ~/code; git clone https://github.com/thisismygitrepo/machineconfig --origin origin
# cd ~/code/machineconfig; git remote set-url origin https://github.com/thisismygitrepo/machineconfig
# cd ~/code/machineconfig; git remote add origin https://github.com/thisismygitrepo/machineconfig
# cd ~/code/machineconfig; pip install -e .

"""
