
"""checkout_version.py
"""

from crocodile.file_management import P, Save
from crocodile.meta import Terminal
from machineconfig.utils.ve import get_ve_profile, get_ve_specs
from machineconfig.scripts.python.repos import record_a_repo, install_repos
import platform


# TODO: add data requirements for added isolation of file system.


def get_ps1_install_template(ve_name: str, req_root: str, py_version: str):
    template = f"""
$ve_name = '{ve_name}'
$py_version = {py_version}  # type: ignore
(Invoke-WebRequest bit.ly/cfgvewindows).Content | Invoke-Expression
activate_ve $ve_name
cd {req_root}
pip install -r requirements_{platform.system().lower()}.txt
"""
    return template


def get_bash_install_template(ve_name: str, req_root: str, py_version: str = "3.11"):
    template = f"""
export ve_name='{ve_name}'
export py_version={py_version}  # type: ignore
curl -L bit.ly/cfgvelinux | bash
. activate_ve $ve_name
cd {req_root}
pip install -r requirements_{platform.system().lower()}.txt
"""
    return template


def checkout_version(version: str, repo_root: P, exclude_editable: bool = False):
    """Checkout a version of the repo and install its requirements."""
    ve_name = get_ve_profile(init_path=repo_root)
    ve_path = P.home().joinpath("venvs", ve_name)
    ve_specs = get_ve_specs(ve_path)
    py_version = ve_specs['version_major_minor']

    target_dir = repo_root.expanduser().absolute().joinpath(f"versions/{version}").as_posix()
    if exclude_editable:
        editable_json = get_editable_packages(ve_name=ve_name)
        specs_path = P(target_dir).expanduser().joinpath("editable_packages.json")
        Save.json(obj=editable_json, path=specs_path)
        extra_program = install_repos(specs_path=str(specs_path))
    else: extra_program = ""

    req_root = repo_root.collapseuser().joinpath(f"versions/{version}").as_posix()
    checkout_ve = f"{repo_root.name}-{version}-prod" if not exclude_editable else ve_name
    checkout_ve = input(f"Name of the ve to create (default: {checkout_ve}): ") or checkout_ve
    if platform.system() == "Windows":
        tmplate_ps1 = get_ps1_install_template(ve_name=checkout_ve, req_root=req_root, py_version=py_version)
        P(req_root).expanduser().create().joinpath("install.ps1").write_text(tmplate_ps1 + "\n" + extra_program)
    elif platform.system() == "Linux":
        tmplate_bash = get_bash_install_template(ve_name=checkout_ve, req_root=req_root, py_version=py_version)
        P(req_root).expanduser().create().joinpath("install.sh").write_text(tmplate_bash + "\n" + extra_program)
    else: raise NotImplementedError
    Terminal().run_script(f"""
cd '{target_dir}'
. $HOME/scripts/activate_ve {ve_name}
pip freeze {'--exclude-editable' if exclude_editable else ''} > requirements_{platform.system().lower()}.txt""", verbose=True).print()
    print(f"✅ Installed requirements for version {version}.")


def main():
    version = input("Enter version: ")
    exclude_editable = input("Exclude editable packages? (y/[n]): ") == "y"
    repo_root = P.cwd()
    from git.repo import Repo
    from git.exc import InvalidGitRepositoryError
    try:
        repo = Repo(repo_root, search_parent_directories=False)
        print(f"✅ Found repo at {repo.working_dir}")
    except InvalidGitRepositoryError as err:
        print(f"❌ No repo found at {repo_root}.")
        raise err
    checkout_version(version, repo_root, exclude_editable=exclude_editable)


def get_editable_packages(ve_name: str):
    file = P.tmp().joinpath("tmp_files/editable_requirements.txt")
    Terminal().run_script(f"""
. $HOME/scripts/activate_ve {ve_name}
pip list --editable > {file}""", verbose=True).print()
    res = []
    # print(file)
    tmp3 = file.read_text(encoding='utf-16').splitlines()[2:]
    for a_pkg in tmp3:
        tmp = P(a_pkg.split(" ")[-1].rstrip())
        tmp1 = record_a_repo(tmp)
        res.append(tmp1)
    return res


if __name__ == "__main__":
    pass
