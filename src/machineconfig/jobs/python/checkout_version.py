
"""checkout_version.py
"""

from crocodile.file_management import P
from crocodile.meta import Terminal
from machineconfig.utils.ve import get_ve_profile, get_ve_specs
import platform

# TODO: add data requirements for added isolation of file system.


def get_ps1_install_template(version: str, repo_root: P, py_version: str):
    template = f"""
$ve_name = '{repo_root.name}-{version}-prod'
$py_version = {py_version}  # type: ignore
(Invoke-WebRequest bit.ly/cfgvewindows).Content | Invoke-Expression
activate_ve $ve_name
cd '{repo_root.collapseuser().joinpath(f"versions/{version}").as_posix()}'
pip install -r requirements_{platform.system().lower()}.txt
"""
    return template


def get_bash_install_template(version: str, repo_root: P, py_version: str = "3.11"):
    template = f"""
export ve_name='{repo_root.name}-{version}-prod'
export py_version={py_version}  # type: ignore
curl -L bit.ly/cfgvelinux | bash
activate_ve $ve_name
cd '{repo_root.collapseuser().joinpath(f"versions/{version}").as_posix()}'
pip install -r requirements_{platform.system().lower()}.txt
"""
    return template


def checkout_version(version: str, repo_root: P):
    """Checkout a version of the repo and install its requirements."""
    ve_name = get_ve_profile(init_path=repo_root)
    ve_path = P.home().joinpath("venvs", ve_name)
    ve_specs = get_ve_specs(ve_path)
    py_version = ve_specs['version_major_minor']

    if platform.system() == "Windows":
        tmplate_ps1 = get_ps1_install_template(version, repo_root, py_version=py_version)
        repo_root.joinpath("versions", version).create().joinpath("install.ps1").write_text(tmplate_ps1)
    elif platform.system() == "Linux":
        tmplate_bash = get_bash_install_template(version, repo_root, py_version=py_version)
        repo_root.joinpath("versions", version).create().joinpath("install.sh").write_text(tmplate_bash)
    else: raise NotImplementedError
    target_dir = repo_root.expanduser().absolute().joinpath(f"versions/{version}").as_posix()
    Terminal().run_script(f"""
cd '{target_dir}'
. $HOME/scripts/activate_ve {ve_name}
pip freeze > requirements_{platform.system().lower()}.txt""").print()
    print(f"✅ Installed requirements for version {version}.")


def main():
    version = input("Enter version: ")
    repo_root = P.cwd()
    from git.repo import Repo
    from git.exc import InvalidGitRepositoryError
    try:
        repo = Repo(repo_root, search_parent_directories=False)
        print(f"✅ Found repo at {repo.working_dir}")
    except InvalidGitRepositoryError as err:
        print(f"❌ No repo found at {repo_root}.")
        raise err
    checkout_version(version, repo_root)
