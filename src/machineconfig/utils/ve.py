
"""python and ve installation related utils
"""

from crocodile.file_management import P, Struct, modify_text, List
from machineconfig.utils.utils import LIBRARY_ROOT
import platform
from dataclasses import dataclass
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
    system = platform.system()
    if system == "Windows":
        tmp: list[P] = P.get_env().PATH.search("python.exe").reduce().list[1:]
    else:
        tmp = list(set(List(P.get_env().PATH.search("python3*").reduce()).filter(lambda x: not x.is_symlink() and "-" not in x)))  # type: ignore
    List(tmp).print()
    return list(set([P(x) for x in tmp]))


def get_ve_specs(ve_path: P) -> dict[str, str]:
    ini = r"[mysection]\n" + ve_path.joinpath("pyvenv.cfg").read_text()
    import configparser
    config = configparser.ConfigParser()
    config.read_string(ini)
    res = dict(config['mysection'])
    res['version_major_minor'] = ".".join(res['version'].split(".")[0:2])
    return res


def get_ve_install_script(ve_name: Optional[str] = None, py_version: Optional[str] = None, install_crocodile_and_machineconfig: Optional[bool] = None,
                          delete_if_exists: bool = True,
                          system: Optional[Literal["Windows", "Linux"]] = None) -> str:
    from rich.console import Console
    if system is None:
        system_: str = platform.system()
    else: system_ = system
    console = Console()

    if py_version is None:
        print("\n\n")
        console.rule("Existing Python versions", style="bold red")
        res = get_installed_interpreters()
        List(res).print()
        print("\n\n")
        dotted_py_version = input("Enter python version (3.11): ") or "3.11"
    else: dotted_py_version = py_version

    if ve_name is None:
        console.rule(f"Existing virtual environments")
        for ve_path in P.home().joinpath("venvs").search("*", files=False):
            ve_specs = get_ve_specs(ve_path)
            # console.print(Panel(str(ve_specs), title=ve_path.stem, style="bold blue"))
            Struct(ve_specs).print(title=ve_path.stem, as_config=True)
        ve_name = input("Enter virtual environment name (tst): ") or "tst"

    if install_crocodile_and_machineconfig is None: croco_mac = input("Install essential repos? (y/[n]): ") == "y"
    else: croco_mac = install_crocodile_and_machineconfig

    env_path = P.home().joinpath("venvs", ve_name)
    if delete_if_exists and env_path.exists():
        sure = input(f"An existing environment found. Are you sure you want to delete {env_path} before making new one? (y/[n]): ") == "y"
        console.rule(f"Deleting existing enviroment with similar name")
        env_path.delete(sure=sure)

    scripts = LIBRARY_ROOT.joinpath(f"setup_{system_.lower()}/ve.{'ps1' if system_ == 'Windows' else 'sh'}").read_text()

    variable_prefix = "$" if system_ == "Windows" else ""
    line1 = f"{variable_prefix}ve_name='{ve_name}'"
    line2 = f"{variable_prefix}py_version='{dotted_py_version}'"
    line_start = "# --- Define ve name and python version here ---"
    line_end = "# --- End of user defined variables ---"
    assert line_start in scripts and line_end in scripts, "Script template was mutated beyond recognition."
    scripts = scripts.split(line_start)[0] + "\n".join([line_start, line1, line2, line_end]) + scripts.split(line_end)[1]

    if croco_mac:  # TODO make this more robust by removing sections of the script as opposed to word placeholders.
        text = LIBRARY_ROOT.joinpath(f"setup_{system_.lower()}/repos.{'ps1' if system_ == 'Windows' else 'sh'}").read_text()
        text = modify_text(txt_raw=text, txt_search="ve_name=", txt_alt=f"{variable_prefix}ve_name='{ve_name}'", replace_line=True)
        scripts += text

    # ve_ini_specs = VE_Specs(ve_name=ve_name, py_version=dotted_py_version, ipy_profile="default", os=system_)
    # ve_ini = VE_INI(specs=ve_ini_specs)
    return scripts


def get_ve_install_script_from_specs(repo_root: str, system: Literal["Windows", "Linux"]):
    from crocodile.file_management import Read, Save
    ini_file = P(repo_root).joinpath(".ve.ini")
    assert ini_file.exists(), f"File {ini_file} does not exist."
    ini = Read.ini(ini_file)
    ve_name = ini["specs"]["ve_name"]
    py_version = ini["specs"]["py_version"]
    ipy_profile = ini["specs"]["ipy_profile"]

    # repo_root = ini_file.with_name("requirements.txt").parent

    # for backward compatibility:
    ini_file.with_name(".ve_path").write_text(f"~/venvs/{ve_name}")
    ini_file.with_name(".ipy_profile").write_text(ipy_profile)

    # vscode:
    if not system == "Windows":  # symlinks on windows require admin rights.
        P(repo_root).joinpath(".venv").symlink_to(P.home().joinpath("venvs", ve_name))

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

    base_path = P(repo_root).joinpath("versions", "init").create()
    if system == "Windows":
        script = get_ps1_install_template(ve_name=ve_name, py_version=py_version)
        base_path.joinpath("install_ve.ps1").write_text(script)
    elif system == "Linux":
        script = get_bash_install_template(ve_name=ve_name, py_version=py_version)
        base_path.joinpath("install_ve.sh").write_text(script)
    else:
        raise NotImplementedError(f"System {system} not supported.")

    base_path.joinpath("install_requirements.ps1").write_text(get_install_requirements_template(repo_root=P(repo_root)))
    base_path.joinpath("install_requirements.sh").write_text(get_install_requirements_template(repo_root=P(repo_root)))

    return script


def get_ps1_install_template(ve_name: str, py_version: str):
    template = f"""
$ve_name = '{ve_name}'
$py_version = '{py_version}'  # type: ignore
(Invoke-WebRequest https://bit.ly/cfgvewindows).Content | Invoke-Expression
. $HOME/scripts/activate_ve $ve_name
"""
    return template
def get_bash_install_template(ve_name: str, py_version: str):
    template = f"""
export ve_name='{ve_name}'
export py_version='{py_version}'  # type: ignore
curl -L https://bit.ly/cfgvelinux | bash
. $HOME/scripts/activate_ve $ve_name
"""
    return template


def get_install_requirements_template(repo_root: P):
    return f"""
# This is a template that is meant to be modified manually to install requirements.txt and editable packages.
# one can dispense with this and install libraries manually and on adhoc-basis and then use version_checkout utility.
cd $HOME/{repo_root.as_posix()}
. $HOME/scripts/activate_ve
pip install -r requirements.txt
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
