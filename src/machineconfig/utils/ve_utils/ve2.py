from crocodile.core import Save
from dataclasses import asdict
from crocodile.file_management import P, Read


from typing import Literal

from machineconfig.utils.utils import LIBRARY_ROOT
from machineconfig.utils.ve import VE_INI, VE_Specs


def get_install_requirements_template(repo_root: P, requirements_subpath: str, ve_name: str, system: Literal["Windows", "Linux"]):
    if system == 'Windows':
        set_e_equivalent = 'Set-StrictMode -Version Latest'  # PowerShell equivalent
        install_line = """(Invoke-WebRequest https://bit.ly/cfgreposwindows).Content | Invoke-Expression"""
        activate_ve = fr"""$HOME\venvs\{ve_name}\Scripts\Activate.ps1 -ErrorAction Stop """
    elif system == 'Linux':
        set_e_equivalent = 'set -e'  # Bash equivalent
        install_line = """curl -L https://bit.ly/cfgreposlinux | bash"""
        activate_ve = fr""". $HOME/venvs/{ve_name}/bin/activate """
    else: raise NotImplementedError(f"❌ System {system} not supported.")
    return f"""

# 📝 This is a template that is meant to be modified manually to install requirements.txt and editable packages.
# 💡 One can dispense with this and install libraries manually and on adhoc-basis and then use version_checkout utility.

# mkdir -p $HOME/{repo_root.rel2home().as_posix()}
# cd $HOME/{repo_root.rel2home().as_posix()}
# git clone URL --depth 2

{set_e_equivalent}

cd $HOME/{repo_root.rel2home().as_posix()}

{activate_ve}

# {install_line}
pip install -r {requirements_subpath}/requirements.txt
# pip install -e .

"""


def get_bash_repos_install_script(ve_name: str, use_web: bool, system: Literal["Windows", "Linux"]):
    if use_web: install_line = """curl -L https://bit.ly/cfgreposlinux | bash"""
    else:
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system.lower()}/repos.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    template = f"""
export ve_name='{ve_name}'
. $HOME/scripts/activate_ve $ve_name
{install_line}
"""
    return template


def get_ps1_repos_install_script(ve_name: str, use_web: bool, system: Literal["Windows", "Linux"]):
    if use_web: install_line = """(Invoke-WebRequest https://bit.ly/cfgreposwindows).Content | Invoke-Expression"""
    else:
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system.lower()}/repos.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    template = f"""
$ve_name = '{ve_name}'
. $HOME/scripts/activate_ve $ve_name
{install_line}
"""
    return template


def get_bash_ve_install_script(ve_name: str, py_version: str, use_web: bool, system: Literal["Windows", "Linux"]):
    if use_web: install_line = """curl -L https://bit.ly/cfgvelinux | bash"""
    else:
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system.lower()}/ve.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    template = f"""
export ve_name='{ve_name}'
export py_version='{py_version}'  # type: ignore
{install_line}
. $HOME/scripts/activate_ve $ve_name
"""
    return template


def get_ps1_ve_install_script(ve_name: str, py_version: str, use_web: bool, system: Literal["Windows", "Linux"]):
    if use_web:
        install_line = """(Invoke-WebRequest https://bit.ly/cfgvewindows).Content | Invoke-Expression"""
    else:
        install_line = LIBRARY_ROOT.joinpath(f"setup_{system.lower()}/ve.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    template = f"""
$ve_name = '{ve_name}'
$py_version = '{py_version}'  # type: ignore
{install_line}
. $HOME/scripts/activate_ve $ve_name
"""
    return template


def create_symlinks(repo_root: P, ve_name: str, dotted_py_version: str, system: Literal["Windows", "Linux"], ipy_profile: str):
    from machineconfig.utils.utils import symlink_func
    source = repo_root.joinpath(".venv")
    target = P.home().joinpath("venvs", ve_name)
    target.mkdir(exist_ok=True, parents=True)  # if ve not created yet, make up a folder at least, so that symlink can be created, then this folder is either populated or recreated by ve creation script.
    symlink_func(this=source, to_this=target)

    # for backward compatibility:
    repo_root.joinpath(".ve_path").write_text(f"~/venvs/{ve_name}")
    repo_root.joinpath(".ipy_profile").write_text(ipy_profile)

    ve_ini_specs = VE_Specs(ve_name=ve_name, py_version=dotted_py_version, ipy_profile="default", os=system)
    ve_ini = VE_INI(specs=ve_ini_specs)
    Save.ini(obj=asdict(ve_ini), path=repo_root.joinpath(".ve.ini"))
    vscode = repo_root.joinpath(".vscode/settings.json")
    if vscode.exists():
        settings = Read.json(vscode)
    else:
        settings = {}
    if system == "Windows":
        settings["python.defaultInterpreterPath"] = P.home().joinpath("venvs", ve_name, "Scripts", "python.exe").as_posix()
    elif system == "Linux":
        settings["python.defaultInterpreterPath"] = P.home().joinpath("venvs", ve_name, "bin", "python").as_posix()
    else:
        raise NotImplementedError(f"System {system} not supported.")
    Save.json(obj=settings, path=vscode, indent=4)


def make_installation_recipe(repo_root: str, ve_name: str, py_version: str):
    subpath = "versions/init"
    base_path = P(repo_root).joinpath(subpath).create()

    system: Literal["Windows", "Linux"] = "Windows"
    path3 = base_path.joinpath("install_requirements.ps1")
    if path3.exists(): print(f"❌ File already exists @ {path3}, skipping.")
    else:
        install_ve_script = get_ps1_ve_install_script(ve_name=ve_name, py_version=py_version, use_web=True, system=system)
        install_req_script = get_install_requirements_template(repo_root=P(repo_root), requirements_subpath=subpath, ve_name=ve_name, system=system)
        path3.write_text(install_ve_script + "\n" + install_req_script)

    system = "Linux"
    path4 = base_path.joinpath("install_requirements.sh")
    if path4.exists(): print(f"❌ File already exists @ {path4}, skipping.")
    else:
        install_ve_script = get_bash_ve_install_script(ve_name=ve_name, py_version=py_version, use_web=True, system=system)
        install_req_script = get_install_requirements_template(repo_root=P(repo_root), requirements_subpath=subpath, ve_name=ve_name, system=system)
        path4.write_text(install_ve_script + "\n" + install_req_script)
    return None