
"""python and ve installation related utils
"""

from crocodile.file_management import P, Struct, modify_text, List
from machineconfig.utils.utils import LIBRARY_ROOT
import platform
from typing import Optional, Literal


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


def get_ve_install_script(ve_name: Optional[str] = None, py_version: Optional[str] = None, install_crocodile_and_machineconfig: Optional[bool] = None,
                          delete_if_exists: bool = True,
                          system: Optional[Literal["Windows", "Linux"]] = None):
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
    return scripts


def get_ps1_install_template(ve_name: str, req_root: str, py_version: str):
    template = f"""
$ve_name = '{ve_name}'
$py_version = '{py_version}'  # type: ignore
(Invoke-WebRequest bit.ly/cfgvewindows).Content | Invoke-Expression
. $HOME/scripts/activate_ve $ve_name
cd {req_root}
pip install -r requirements_{platform.system().lower()}.txt
"""
    return template
def get_bash_install_template(ve_name: str, req_root: str, py_version: str = "3.11"):
    template = f"""
export ve_name='{ve_name}'
export py_version='{py_version}'  # type: ignore
curl -L bit.ly/cfgvelinux | bash
. activate_ve $ve_name
cd {req_root}
pip install -r requirements_{platform.system().lower()}.txt
"""
    return template
