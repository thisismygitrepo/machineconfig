
"""checkout_version.py
"""

from crocodile.file_management import P, Save
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
        Save.json(obj=editable_json, path=specs_path)
        extra_program = install_repos(specs_path=str(specs_path), editable_install=True)
    else: extra_program = ""

    req_root = repo_root.collapseuser().joinpath(f"versions/{version}").as_posix()
    checkout_ve = f"{repo_root.name}-{version}-prod" if not exclude_editable else ve_name
    checkout_ve = input(f"Name of the ve to create (default: {checkout_ve}): ") or checkout_ve

    template = get_ve_install_script(ve_name=checkout_ve, py_version=py_version)
    template += f"""
. $HOME/scripts/activate_ve $ve_name
cd {req_root}
pip install -r requirements_{sys}.txt
"""
    P(req_root).expanduser().create().joinpath("install" + (".ps1" if sys == "windows" else ".sh")).write_text(template + "\n" + extra_program)
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
        tmp1 = record_a_repo(tmp, search_parent_directories=True)  # pip list --editable returns path to package or repo in a way not yet understood.
        res.append(tmp1)
    return res


if __name__ == "__main__":
    pass
