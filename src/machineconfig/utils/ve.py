"""python and ve installation related utils
"""

from crocodile.core import Struct, List
from crocodile.file_management import P

import platform
from dataclasses import dataclass
from typing import Optional, Literal

from machineconfig.utils.ve_utils.ve1 import get_installed_interpreters
from machineconfig.utils.ve_utils.ve1 import get_ve_specs
from machineconfig.utils.ve_utils.ve2 import get_bash_repos_install_script
from machineconfig.utils.ve_utils.ve2 import get_ps1_repos_install_script
from machineconfig.utils.ve_utils.ve2 import get_bash_ve_install_script
from machineconfig.utils.ve_utils.ve2 import get_ps1_ve_install_script
from machineconfig.utils.ve_utils.ve2 import create_symlinks
from machineconfig.utils.ve_utils.ve2 import make_installation_recipe



@dataclass
class VE_Specs:
    ve_name: str
    py_version: str
    ipy_profile: str
    os: str


@dataclass
class VE_INI:
    specs: VE_Specs


def get_ve_install_script(ve_name: Optional[str] = None, py_version: Optional[str] = None,
                          install_crocodile_and_machineconfig: Optional[bool] = None,
                          delete_if_exists: bool=True,
                          ) -> str:
    from rich.console import Console
    console = Console()
    if py_version is None:
        print("""
{'=' * 60}
🔍 AVAILABLE PYTHON VERSIONS
{'=' * 60}
""")
        res = get_installed_interpreters()
        List(res).print()
        print("""
{'=' * 60}
""")
        dotted_py_version = input("🔢 Enter python version (3.11): ") or "3.11"
    else:
        dotted_py_version = py_version

    if ve_name is None:
        console.rule("📦 Existing Virtual Environments")
        for ve_path in P.home().joinpath("venvs").search("*", files=False):
            try:
                ve_specs = get_ve_specs(ve_path)
            except Exception as _e:
                continue
            Struct(ve_specs).print(title=ve_path.stem, as_config=True)
        default_ve_name = P.cwd().name
        ve_name = input(f"📝 Enter virtual environment name ({default_ve_name}): ") or default_ve_name

    if install_crocodile_and_machineconfig is None:
        essential_repos = input("🔄 Install essential repos? (y/[n]): ") == "y"
        other_repos = input("📦 Input space separated other packages: ")
    else:
        essential_repos = install_crocodile_and_machineconfig
        other_repos = ""

    env_path = P.home().joinpath("venvs", ve_name)
    if delete_if_exists and env_path.exists():
        sure = input(f"⚠️ An existing environment found. Are you sure you want to delete {env_path} before making new one? (y/[n]): ") == "y"
        console.rule("🗑️ Deleting existing environment with similar name")
        env_path.delete(sure=sure)

    system: Literal["Windows", "Linux"]
    if platform.system() == "Windows":
        system = "Windows"
        script = get_ps1_ve_install_script(ve_name=ve_name, py_version=dotted_py_version, use_web=False, system=system)
    elif platform.system() == "Linux":
        system = "Linux"
        script = get_bash_ve_install_script(ve_name=ve_name, py_version=dotted_py_version, use_web=False, system=system)
    else:
        raise NotImplementedError(f"❌ System {platform.system()} not supported.")

    if essential_repos:
        if system == "Windows":
            script += "\n" + get_ps1_repos_install_script(ve_name=ve_name, use_web=False, system=system)
        elif system == "Linux":
            script += "\n" + get_bash_repos_install_script(ve_name=ve_name, use_web=False, system=system)
        else:
            raise NotImplementedError(f"❌ System {system} not supported.")

    if other_repos != "":
        script += "\nuv pip install " + other_repos

    link_ve: bool = input("🔗 Create symlinks? [y/[n]] ") == "y"
    if link_ve: create_symlinks(repo_root=P.cwd(), ve_name=ve_name, dotted_py_version=dotted_py_version, system=system, ipy_profile="default")
    make_installation_recipe(repo_root=P.cwd(), ve_name=ve_name, py_version=dotted_py_version)
    return script

