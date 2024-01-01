
"""checkout_version.py
"""

from crocodile.file_management import P, Save, randstr
from crocodile.meta import Terminal
from machineconfig.utils.ve import get_ve_profile, get_ve_specs, get_ve_install_script
from machineconfig.scripts.python.repos import record_a_repo, install_repos
import platform


# TODO: add data requirements for added isolation of file system.


def checkout_version(version: str, repo_root: P, exclude_editable: bool = False):
    """Checkout a version of the repo and install its requirements."""
    ve_name = get_ve_profile(init_path=repo_root)
    ve_path = P.home().joinpath("venvs", ve_name)
    ve_specs = get_ve_specs(ve_path)
    py_version = ve_specs['version_major_minor']
    sys = platform.system().lower()

    target_dir = repo_root.expanduser().absolute().joinpath(f"versions/{version}").as_posix()
    if exclude_editable:
        editable_json = get_editable_packages(ve_name=ve_name)
        specs_path = P(target_dir).expanduser().joinpath("editable_packages.json")
        Save.json(obj=editable_json, path=specs_path, indent=4)
        install_editable_packages = install_repos(specs_path=str(specs_path), editable_install=True)
    else: install_editable_packages = ""

    version_root = repo_root.collapseuser().joinpath(f"versions/{version}").as_posix()
    version_root_obj = P(version_root).expanduser().create()
    checkout_ve = f"{repo_root.name}-{version}-prod" if not exclude_editable else ve_name
    checkout_ve = input(f"Name of the ve to create (default: {checkout_ve}): ") or checkout_ve

    ve_template = get_ve_install_script(ve_name=checkout_ve, py_version=py_version, system="Windows", delete_if_exists=False, install_crocodile_and_machineconfig=False)
    version_root_obj.joinpath("install_ve.ps1").write_text(ve_template)
    ve_template = get_ve_install_script(ve_name=checkout_ve, py_version=py_version, system="Linux", delete_if_exists=False, install_crocodile_and_machineconfig=False)
    version_root_obj.joinpath("install_ve.sh").write_text(ve_template)

    install_requirements = f"""
. $HOME/scripts/activate_ve {ve_name}
cd {version_root}
pip install -r requirements_{sys}.txt
{install_editable_packages}
"""
    if sys == "windows":
        version_root_obj.joinpath("install_requirements.ps1").write_text(install_requirements)
        if not version_root_obj.joinpath("install_requirements.sh").exists(): version_root_obj.joinpath("install_requirements.sh").write_text(install_requirements)
    elif sys == "linux":
        version_root_obj.joinpath("install_requirements.sh").write_text(install_requirements)
        if not version_root_obj.joinpath("install_requirements.ps1").exists(): version_root_obj.joinpath("install_requirements.ps1").write_text(install_requirements)
    else: raise NotImplementedError(f"System {sys} not supported.")

    pip_freeze_script = f"""
cd '{target_dir}'
. "$HOME/scripts/activate_ve" {ve_name}
python -m pip freeze {'--exclude-editable' if exclude_editable else ''} > requirements_{sys}.txt
"""
    Terminal().run_script(pip_freeze_script, verbose=True, shell="default").print()

    install_all_script = r"""
#!/usr/bin/bash

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
. $CUR_DIR/install_ve.sh
. $CUR_DIR/install_requirements.sh
"""
    version_root_obj.joinpath("install.sh").write_text(install_all_script)
    install_all_script = r"""

$CUR_DIR = Split-Path $MyInvocation.MyCommand.Path -Parent
. $CUR_DIR/install_ve.ps1
. $CUR_DIR/install_requirements.ps1

"""
    version_root_obj.joinpath("install.ps1").write_text(install_all_script)
    print(f"✅ Installed requirements for version {version}.")


def main():
    from git.repo import Repo
    from git.exc import InvalidGitRepositoryError
    try:
        repo = Repo(P.cwd(), search_parent_directories=True)
        print(f"✅ Found repo at {repo.working_dir}")
    except InvalidGitRepositoryError as err:
        print(f"❌ No repo found at {P.cwd()} or its parents.")
        raise err
    version = input("Enter version name: ")
    from rich.prompt import Confirm
    exclude_editable = Confirm.ask("Exclude editable packages?", default=False)

    repo_root = P(repo.working_dir)
    checkout_version(version, repo_root, exclude_editable=exclude_editable)


def get_editable_packages(ve_name: str):
    file = P.tmp().joinpath(f"tmp_files/editable_requirements_{randstr()}.txt")
    editable_packages_script = f"""
. $HOME/scripts/activate_ve {ve_name}
pip list --editable > {file}
"""
    Terminal().run_script(editable_packages_script, verbose=True, shell="default").print()
    try: tmp3 = file.read_text(encoding='utf-16').splitlines()[2:]
    except UnicodeError: tmp3 = file.read_text().splitlines()[2:]

    res = []
    for a_pkg in tmp3:
        tmp = P(a_pkg.split(" ")[-1].rstrip())
        tmp1 = record_a_repo(tmp, search_parent_directories=True)  # pip list --editable returns path to package or repo in a way not yet understood.
        res.append(tmp1)
    return res


if __name__ == "__main__":
    pass
